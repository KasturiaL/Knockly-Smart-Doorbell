# combined_main.py

import os, cv2, pickle, threading, time, datetime
import serial, mysql.connector, face_recognition, numpy as np
from pathlib import Path
from picamera2 import Picamera2
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Configuration
pi_port = "/dev/ttyACM0"
baud_rate = 9600
timeout_s = 0.1

FTP_USER = "pi"
FTP_PASSWORD = "raspberry"
FTP_DIR = "ftp_videos"
COMMAND_FILE = "command.txt"
DB_CONFIG = {
    "host": "localhost",
    "user": "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}
MIN_VIDEO_DURATION = 15
BRIGHTNESS_THRESHOLD = 32

# Setup paths
directory = Path(__file__).parent
log_file = directory / "log.txt"
command_file = directory / "command.txt"

# Arduino connection
arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s)

# Global camera instance
cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
cam.start()

# Logging function
def log(msg):
    now = datetime.datetime.now().strftime("%x %X")
    entry = f"{now} | {msg}"
    print(entry)
    with log_file.open("a") as f:
        f.write(entry + "\n")
        f.flush()

# Command handler
def send_command(cmd):
    with open(COMMAND_FILE, "w") as f:
        f.write(str(cmd))
    arduino.write(bytes(cmd, 'utf-8'))
    time.sleep(0.05)
    if cmd == "1": log("Phone has opened the door.")
    elif cmd == "2": log("Phone has closed the door.")
    elif cmd == "3": log("Known face detected.")
    elif cmd == "4": log("Blocked face detected.")

# FTP server
def start_ftp_server():
    os.makedirs(FTP_DIR, exist_ok=True)
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIR, perm="elradfmw")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("0.0.0.0", 2121), handler)
    print("[INFO] FTP Server started on port 2121...")
    server.serve_forever()

# Video processing
def extract_encodings_from_video(video_path, user_id):
    print(f"[INFO] Validating video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERROR] Could not open video file.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps if fps > 0 else 0
    if duration < MIN_VIDEO_DURATION:
        print(f"[ERROR] Video too short ({duration:.1f}s).")
        cap.release(); return

    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Could not read frame.")
        cap.release(); return

    brightness = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()
    if brightness < BRIGHTNESS_THRESHOLD:
        print(f"[ERROR] Too dark (avg brightness {brightness:.1f}).")
        cap.release(); return

    print(f"[INFO] Video valid (duration {duration:.1f}s, brightness {brightness:.1f})")

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    name = os.path.splitext(os.path.basename(video_path))[0]
    saved = 0
    for i in range(0, int(frame_count), max(int(frame_count) // 20, 1)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret: continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        if locs:
            encs = face_recognition.face_encodings(rgb, locs)
            for e in encs:
                store_face_encoding(user_id, name, e)
                saved += 1
        if saved >= 20: break
    cap.release()
    print(f"[INFO] Stored {saved} encodings for {name}")

# Store to DB
def store_face_encoding(uid, name, enc):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO face_profiles (user_id, face_profile_name, face_data) VALUES (%s,%s,%s)",
                    (uid, name, pickle.dumps(enc)))
        conn.commit()
        print(f"[DEBUG] Stored {name} (uid={uid})")
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        cur.close(); conn.close()

# Load all encodings
def fetch_all_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT face_profile_name, face_data FROM face_profiles")
    encs, names = [], []
    for n, b in cur.fetchall():
        names.append(n); encs.append(pickle.loads(b))
    cur.close(); conn.close()
    return encs, names

# Process most recent video
def process_latest_video(user_id):
    files = [f for f in os.listdir(FTP_DIR) if f.endswith(".mp4")]
    if not files:
        print("[INFO] No videos found.")
        return
    latest = max(files, key=lambda f: os.path.getctime(os.path.join(FTP_DIR, f)))
    extract_encodings_from_video(os.path.join(FTP_DIR, latest), user_id)

# Live recognition (always running)
def run_live_recognition():
    known_encs, known_names = fetch_all_encodings()
    print("[INFO] Running live facial recognition...")
    while True:
        frame = cam.capture_array()
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        encs = face_recognition.face_encodings(rgb, locs)
        for (t, r, b, l), e in zip(locs, encs):
            matches = face_recognition.compare_faces(known_encs, e)
            name = "Unknown"
            if known_encs:
                dists = face_recognition.face_distance(known_encs, e)
                idx = np.argmin(dists)
                if matches[idx]:
                    name = known_names[idx]
            if name != "Unknown":
                send_command("3")
                send_command("1")
                threading.Timer(5, lambda: send_command("2")).start()
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            t, r, b, l = [x * 4 for x in (t, r, b, l)]
            cv2.rectangle(frame, (l, t), (r, b), color, 2)
            cv2.putText(frame, name, (l + 6, t - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.stop(); cv2.destroyAllWindows()

# Start FTP server in background
threading.Thread(target=start_ftp_server, daemon=True).start()

# Start real-time recognition
threading.Thread(target=run_live_recognition, daemon=True).start()

# Simple menu
while True:
    print("\n[1] Process Latest Video\n[2] Exit")
    choice = input("Choice: ").strip()
    if choice == '1':
        uid = input("Enter user_id: ").strip()
        process_latest_video(uid)
    elif choice == '2':
        break
    else:
        print("Invalid option.")

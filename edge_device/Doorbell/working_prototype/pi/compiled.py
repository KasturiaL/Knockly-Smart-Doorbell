# combined_main.py

import os
import cv2
import pickle
import threading
import time
import datetime
import serial
import mysql.connector
import face_recognition
import numpy as np
from pathlib import Path
from picamera2 import Picamera2
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# ------------------------- Configuration -------------------------

pi_port            = "/dev/ttyACM0"
baud_rate          = 9600
timeout_s          = 0.1

FTP_USER           = "pi"
FTP_PASSWORD       = "raspberry"
FTP_DIR            = "ftp_videos"
COMMAND_FILE       = "command.txt"

DB_CONFIG = {
    "host":     "localhost",
    "user":     "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}

MIN_VIDEO_DURATION    = 15    # seconds
BRIGHTNESS_THRESHOLD  = 32    # mean gray value 0–255
OPEN_DOOR_COOLDOWN    = 5     # seconds between re-opening

# ------------------------- Paths & Files -------------------------

base_dir      = Path(__file__).parent
log_file      = base_dir / "log.txt"
ftp_dir       = base_dir / FTP_DIR
command_file  = base_dir / COMMAND_FILE

# ------------------------- Hardware Setup -------------------------

arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s)

cam = Picamera2()
cam.configure(cam.create_video_configuration(
    main={"format": 'XRGB8888', "size": (640, 480)}
))
cam.start()

# ------------------------- Utility Functions -------------------------

def log(msg):
    now   = datetime.datetime.now().strftime("%x %X")
    entry = f"{now} | {msg}"
    print(entry)
    with log_file.open("a") as f:
        f.write(entry + "\n")
        f.flush()

def send_command(cmd):
    # write to command file for middleman logic
    with open(command_file, "w") as f:
        f.write(str(cmd))
    # send to Arduino
    arduino.write(bytes(cmd, 'utf-8'))
    time.sleep(0.05)
    if   cmd == "0": log("Middleman startup complete.")
    elif cmd == "1": log("Phone has opened the door.")
    elif cmd == "2": log("Phone has closed the door.")
    elif cmd == "3": log("Known face detected.")
    elif cmd == "4": log("Blocked face detected.")

def setup():
    send_command("0")
    print("Listening for log messages...")

# ------------------------- Arduino Logging -------------------------

def arduino_logger():
    while True:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()
        if line:
            log(f"Arduino: {line}")
        time.sleep(0.1)

# ------------------------- FTP Server -------------------------

def start_ftp_server():
    ftp_dir.mkdir(exist_ok=True)
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, str(ftp_dir), perm="elradfmw")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("0.0.0.0", 2121), handler)
    log("[INFO] FTP Server started on port 2121.")
    server.serve_forever()

# ------------------------- Video Processing & DB -------------------------

def extract_encodings_from_video(video_path, user_id):
    log(f"[INFO] Validating video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        log("[ERROR] Could not open video file.")
        return

    fps         = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration    = frame_count / fps if fps > 0 else 0
    if duration < MIN_VIDEO_DURATION:
        log(f"[ERROR] Video too short ({duration:.1f}s).")
        cap.release()
        return

    ret, frame = cap.read()
    if not ret:
        log("[ERROR] Could not read first frame.")
        cap.release()
        return

    brightness = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()
    if brightness < BRIGHTNESS_THRESHOLD:
        log(f"[ERROR] Too dark (avg brightness {brightness:.1f}).")
        cap.release()
        return

    log(f"[INFO] Video OK (duration {duration:.1f}s, brightness {brightness:.1f})")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    name  = os.path.splitext(os.path.basename(video_path))[0]
    saved = 0
    step  = max(int(frame_count)//20, 1)

    for i in range(0, int(frame_count), step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            continue

        rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        if locs:
            encs = face_recognition.face_encodings(rgb, locs)
            for enc in encs:
                store_face_encoding(user_id, name, enc)
                saved += 1
        if saved >= 20:
            break

    cap.release()
    log(f"[INFO] Stored {saved} encodings for {name}")

def store_face_encoding(uid, profile_name, encoding):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO face_profiles (user_id, face_profile_name, face_data) "
            "VALUES (%s, %s, %s)",
            (uid, profile_name, pickle.dumps(encoding))
        )
        conn.commit()
        log(f"[DEBUG] Stored encoding for {profile_name} (uid={uid})")
    except Exception as e:
        log(f"[DB ERROR] {e}")
    finally:
        cur.close()
        conn.close()

def fetch_all_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute("SELECT face_profile_name, face_data FROM face_profiles")
    encs, names = [], []
    for name, blob in cur.fetchall():
        encs.append(pickle.loads(blob))
        names.append(name)
    cur.close()
    conn.close()
    return encs, names

def process_latest_video(user_id):
    files = [f for f in os.listdir(FTP_DIR) if f.endswith(".mp4")]
    if not files:
        log("[INFO] No videos found.")
        return
    latest = max(files, key=lambda f: os.path.getctime(os.path.join(FTP_DIR, f)))
    extract_encodings_from_video(os.path.join(FTP_DIR, latest), user_id)

# ------------------------- Live Recognition -------------------------

def run_live_recognition():
    known_encs, known_names = fetch_all_encodings()
    log("[INFO] Running live facial recognition...")
    last_open_time = 0.0

    while True:
        frame = cam.capture_array()
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locs  = face_recognition.face_locations(rgb)
        encs  = face_recognition.face_encodings(rgb, locs)

        for (t, r, b, l), enc in zip(locs, encs):
            matches = face_recognition.compare_faces(known_encs, enc)
            name    = "Unknown"
            if known_encs:
                dists = face_recognition.face_distance(known_encs, enc)
                idx   = np.argmin(dists)
                if matches[idx]:
                    name = known_names[idx]

            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            t, r, b, l = [x * 4 for x in (t, r, b, l)]
            cv2.rectangle(frame, (l, t), (r, b), color, 2)
            cv2.putText(frame, name, (l + 6, t - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if name != "Unknown":
                now = time.time()
                if now - last_open_time >= OPEN_DOOR_COOLDOWN:
                    send_command("3")
                    last_open_time = now

        # **UI calls on main thread → safe from segfault**
        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.stop()
    cv2.destroyAllWindows()

# ------------------------- Main Startup -------------------------

if __name__ == "__main__":
    setup()

    # background threads
    threading.Thread(target=start_ftp_server, daemon=True).start()
    threading.Thread(target=arduino_logger,   daemon=True).start()

    # **run recognition in main thread, no longer a background thread**
    run_live_recognition()

    # once the window is closed, fall back to your menu
    while True:
        choice = input("[1] Process Latest Video\n[2] Exit\nChoice: ").strip()
        if choice == '1':
            uid = input("Enter user_id: ").strip()
            process_latest_video(uid)
        elif choice == '2':
            break
        else:
            print("Invalid option.")

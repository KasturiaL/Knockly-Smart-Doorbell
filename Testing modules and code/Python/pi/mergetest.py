# doorbell_system.py
#
# Combines facial‐recognition (FTP, DB, live & recording) with Arduino “person detected” triggers
#
# What this does:
# 1. Runs an FTP server to grab incoming vids
# 2. Validates videos (duration/brightness), extracts face encodings, stores them in MySQL
# 3. Loads encodings to perform live recognition on PiCam
# 4. Can record a 30-second video with recognition active
# 5. Listens to Arduino over serial; when it logs “Object is a person.”, starts a 30s record+recognize
# 6. Also handles phone commands (open/close door) via command.txt
# 7. Provides a simple menu to process videos, launch live recognition, or manual recording

# Dependencies:
# pip install face_recognition opencv-python mysql-connector-python pyftpdlib
# sudo apt install libmysqlclient-dev

import os, cv2, time, pickle, threading, mysql.connector, face_recognition, numpy as np
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers    import FTPHandler
from pyftpdlib.servers     import FTPServer
from picamera2             import Picamera2
import serial, datetime
from pathlib import Path

# ─── CONFIG ────────────────────────────────────────────────────────────────────

# FTP server
FTP_USER     = "pi"
FTP_PASSWORD = "raspberry"
FTP_DIR      = "ftp_videos"

# MySQL
DB_CONFIG = {
    "host":     "localhost",
    "user":     "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}

# Validation
MIN_VIDEO_DURATION   = 15   # seconds
BRIGHTNESS_THRESHOLD = 32   # average gray

# Command file for Arduino middleman
BASE_DIR     = Path(__file__).parent
COMMAND_FILE = BASE_DIR / "command.txt"
LOG_FILE     = BASE_DIR / "log.txt"

# Arduino serial
ARDUINO_PORT = "/dev/ttyACM0"  # adjust as needed
BAUD_RATE    = 9600
TIMEOUT_S    = 0.1

cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"format":'XRGB8888',"size":(640,480)}))

is_recording = False

# Recording duration (30s for testing)
RECORD_DURATION = 30

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def send_command(cmd: int):
    """Write a single-digit command into COMMAND_FILE for the Arduino."""
    with open(COMMAND_FILE, "w") as f:
        f.write(str(cmd))

def log(msg: str):
    """Timestamp + append to LOG_FILE + print."""
    now   = datetime.datetime.now().strftime("%x %X")
    entry = f"{now} | {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def read_serial(ser):
    """Nonblocking read from serial.Serial; returns string or None."""
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    return line if line else None

def check_command_file():
    """If COMMAND_FILE exists, read & delete it, return the cmd string."""
    if COMMAND_FILE.is_file():
        cmd = COMMAND_FILE.read_text().strip()
        COMMAND_FILE.unlink()
        return cmd
    return None

# ─── ROTATION ──────────────────────────────────────────────────────────────────

def rotate_image(image, angle):
    if angle == 0:
        return image
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

# ─── FTP SERVER ────────────────────────────────────────────────────────────────

def start_ftp_server():
    os.makedirs(FTP_DIR, exist_ok=True)
    auth    = DummyAuthorizer()
    auth.add_user(FTP_USER, FTP_PASSWORD, FTP_DIR, perm="elradfmw")
    handler = FTPHandler; handler.authorizer = auth
    server  = FTPServer(("0.0.0.0", 2121), handler)
    log("FTP server started on port 2121")
    server.serve_forever()

# ─── VIDEO PROCESSING ───────────────────────────────────────────────────────────

def extract_encodings_from_video(video_path, user_id):
    log(f"Validating video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        log(f"[ERROR] Cannot open {video_path}")
        return

    fps         = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration    = frame_count/fps if fps>0 else 0
    if duration < MIN_VIDEO_DURATION:
        log(f"[ERROR] Too short ({duration:.1f}s) < {MIN_VIDEO_DURATION}s")
        cap.release(); return

    ret, frame = cap.read()
    if not ret:
        log("[ERROR] Cannot read first frame")
        cap.release(); return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if gray.mean() < BRIGHTNESS_THRESHOLD:
        log(f"[ERROR] Too dark ({gray.mean():.1f}) < {BRIGHTNESS_THRESHOLD}")
        cap.release(); return

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    log(f"[INFO] Video OK (dur {duration:.1f}s, bright {gray.mean():.1f})")

    person_name = os.path.splitext(os.path.basename(video_path))[0]
    interval    = max(int(frame_count)//20, 1)
    saved       = 0

    while saved < 20:
        for i in range(0, int(frame_count), interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frm = cap.read()
            if not ret: continue
            for ang in (0,90,180,270):
                rgb  = cv2.cvtColor(rotate_image(frm,ang), cv2.COLOR_BGR2RGB)
                locs = face_recognition.face_locations(rgb)
                if not locs: continue
                encs = face_recognition.face_encodings(rgb, locs)
                log(f"[DEBUG] Frame {i} rot{ang}° → {len(encs)} enc")
                for e in encs:
                    store_face_encoding(user_id, person_name, e)
                    saved += 1
                break
            if saved>=20: break
        break

    cap.release()
    log(f"[INFO] Stored {saved} encodings for {person_name}")

def store_face_encoding(uid, name, enc):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO face_profiles (user_id, face_profile_name, face_data) VALUES (%s,%s,%s)",
            (uid, name, pickle.dumps(enc))
        )
        conn.commit()
        log(f"[DEBUG] Stored {name} (uid={uid})")
    except Exception as e:
        log(f"[DB ERROR] {e}")
    finally:
        cur.close(); conn.close()

def fetch_all_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute("SELECT face_profile_name, face_data FROM face_profiles")
    encs, names = [], []
    for n, b in cur.fetchall():
        names.append(n); encs.append(pickle.loads(b))
    cur.close(); conn.close()
    return encs, names

# ─── LIVE RECOGNITION ──────────────────────────────────────────────────────────

def live_recognition(duration=None):
    encs, names = fetch_all_encodings()
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(main={"format":'XRGB8888',"size":(640,480)}))
    cam.start()
    log("[INFO] Live recognition started")
    start = time.time()
    while True:
        if duration and time.time() - start >= duration:
            break
        frame = cam.capture_array()
        small = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
        rgb   = cv2.cvtColor(small,cv2.COLOR_BGR2RGB)
        locs  = face_recognition.face_locations(rgb)
        encs2 = face_recognition.face_encodings(rgb, locs)
        for (t,r,b,l), e in zip(locs, encs2):
            m = face_recognition.compare_faces(encs, e)
            name="Unknown"
            if encs:
                d   = face_recognition.face_distance(encs, e)
                idx = np.argmin(d)
                if m[idx]: name=names[idx]
            t,r,b,l = [x*4 for x in (t,r,b,l)]
            col = (0,255,0) if name!="Unknown" else (0,0,255)
            cv2.rectangle(frame,(l,t),(r,b),col,2)
            cv2.putText(frame,name,(l+6,t-6),cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
            if name!="Unknown":
                send_command(3); time.sleep(0.1); send_command(1)
                threading.Timer(5, lambda: send_command(2)).start()
        cv2.imshow("Live Recognition", frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
    cam.stop(); cv2.destroyAllWindows()
    log("[INFO] Live recognition ended")

# ─── RECORD + RECOGNITION ──────────────────────────────────────────────────────

def record_and_recognize(duration=RECORD_DURATION, output_path="recorded_video.mp4"):
    is_recording=True
    encs, names = fetch_all_encodings()
    
    cam.start()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(output_path, fourcc, 30, (640,480))
    log(f"[INFO] Recording {duration}s with recognition…")
    start = time.time()
    while time.time() - start < duration:
        frame = cam.capture_array()
        small = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
        rgb   = cv2.cvtColor(small,cv2.COLOR_BGR2RGB)
        locs  = face_recognition.face_locations(rgb)
        encs2 = face_recognition.face_encodings(rgb, locs)
        for (t,r,b,l), e in zip(locs, encs2):
            m = face_recognition.compare_faces(encs, e)
            name="Unknown"
            if encs:
                d   = face_recognition.face_distance(encs, e)
                idx = np.argmin(d)
                if m[idx]: name=names[idx]
            t,r,b,l = [x*4 for x in (t,r,b,l)]
            col = (0,255,0) if name!="Unknown" else (0,0,255)
            cv2.rectangle(frame,(l,t),(r,b),col,2)
            cv2.putText(frame,name,(l+6,t-6),cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
            if name!="Unknown":
                send_command(3); time.sleep(0.1)
        out.write(frame)
        cv2.imshow("Recording + Recognition", frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
    out.release()
    cam.stop(); cv2.destroyAllWindows()
    log(f"[INFO] Saved video to {output_path}")
    log("[INFO] Recording ended")
    is_recording=False

# ─── VIDEO PROCESS LATEST ─────────────────────────────────────────────────────

def process_latest_video(user_id):
    files = [f for f in os.listdir(FTP_DIR) if f.lower().endswith(".mp4")]
    if not files:
        log("[INFO] No videos found.")
        return
    latest = max(files, key=lambda f: os.path.getctime(os.path.join(FTP_DIR,f)))
    extract_encodings_from_video(os.path.join(FTP_DIR,latest), user_id)

# ─── SERIAL LISTENER ──────────────────────────────────────────────────────────

def serial_listener():
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=TIMEOUT_S)
    log(f"[INFO] Listening on serial {ARDUINO_PORT}")
    while True:
        # phone commands
        cmd = check_command_file()
        if cmd:
            ser.write(cmd.encode()); time.sleep(0.05)
            if   cmd=="1": log("Phone has opened the door.")
            elif cmd=="2": log("Phone has closed the door.")
            elif cmd=="3": log("Known face detected.")
            elif cmd=="4": log("Blocked face detected.")
        # arduino logs
        msg = read_serial(ser)
        if msg:
            log(f"Arduino → {msg}")
            if msg == "Object is a person.":
                if not is_recording:
                    log("Triggering record_and_recognize")
                    record_and_recognize()
                else:
                    log("Recording in progress; trigger ignored.")
        time.sleep(0.01)

# ─── MAIN MENU ────────────────────────────────────────────────────────────────

def main():

    # start FTP server
    threading.Thread(target=start_ftp_server, daemon=True).start()
    # start serial listener
    threading.Thread(target=serial_listener,    daemon=True).start()

    # menu loop
    while True:
        print("\n[1] Process Latest Video")
        print("[2] Start Live Recognition")
        print("[3] Record 30-Second Video with Recognition")
        print("[4] Exit")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            uid = input("Enter user_id: ").strip()
            process_latest_video(uid)
        elif choice == '2':
            live_recognition()
        elif choice == '3':
            record_and_recognize()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

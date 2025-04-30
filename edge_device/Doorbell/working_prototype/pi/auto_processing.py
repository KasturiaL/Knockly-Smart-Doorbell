# GUI now runs on the main thread. Prior issue was with GUI (opencv.imshow - GTK) running on a daemon thread, causing the seg-fault.

import os
import cv2
import pickle
import shutil
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
from pyftpdlib.handlers    import FTPHandler
from pyftpdlib.servers     import FTPServer

# ------------------------- Configuration -------------------------

pi_port            = "/dev/ttyACM0"
baud_rate          = 9600
timeout_s          = 0.1

FTP_USER           = "pi"
FTP_PASSWORD       = "raspberry"
FTP_DIR            = "ftp_videos"
PROCESSED_DIR      = "processed_videos"
COMMAND_FILE       = "command.txt"

DB_CONFIG = {
    "host":     "localhost",
    "user":     "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}

DOORBELL_ID           = 1
MIN_VIDEO_DURATION    = 15    # seconds
BRIGHTNESS_THRESHOLD  = 32    # mean gray value 0–255
OPEN_DOOR_COOLDOWN    = 5     # seconds between re-opening

# ------------------------- Paths & Files -------------------------

base_dir       = Path(__file__).parent
log_file       = base_dir / "log.txt"
ftp_dir        = base_dir / FTP_DIR
processed_dir  = base_dir / PROCESSED_DIR
command_file   = base_dir / COMMAND_FILE

# Make sure the working folders exist on first boot
ftp_dir.mkdir(exist_ok=True)
processed_dir.mkdir(exist_ok=True)

# ------------------------- Hardware Setup -------------------------

arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s)

cam = Picamera2()
cam.configure(cam.create_video_configuration(
    main={"format": 'XRGB8888', "size": (640, 480)}))
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
    """Relay a single‑character command to both the file middleman
    (used by the Android app) and the Arduino."""
    try:
        with open(command_file, "w") as f:
            f.write(str(cmd))
        arduino.write(bytes(cmd, 'utf-8'))
    except Exception as e:
        log(f"[ERROR] Sending command {cmd}: {e}")
    time.sleep(0.05)
    if   cmd == "0": log("Middleman startup complete.")
    elif cmd == "1": log("Phone has opened the door.")
    elif cmd == "2": log("Phone has closed the door.")
    elif cmd == "3": log("Known face detected – door opened.")
    elif cmd == "4": log("Blocked face detected – door kept shut.")

# ------------------------- Arduino Logging Thread -------------------------

def arduino_logger():
    """Continuously mirror anything the Arduino prints to the main log."""
    while True:
        try:
            line = arduino.readline().decode('utf-8', errors='ignore').strip()
            if line:
                log(f"Arduino: {line}")
        except Exception as e:
            log(f"[ERROR] Reading Arduino: {e}")
        time.sleep(0.1)

# ------------------------- FTP Server Thread -------------------------

def start_ftp_server():
    """A tiny pyftpdlib server so a phone can upload visitor videos."""
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, str(ftp_dir), perm="elradfmw")
    handler            = FTPHandler
    handler.authorizer = authorizer
    server             = FTPServer(("0.0.0.0", 2121), handler)
    log("[INFO] FTP Server started on port 2121.")
    server.serve_forever()

# ------------------------- DB Helpers -------------------------

def store_face_encoding(doorbell_id, profile_name, encoding):
    conn = cur = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO face_profiles (doorbell_id, face_profile_name, face_data) "
            "VALUES (%s, %s, %s)",
            (doorbell_id, profile_name, pickle.dumps(encoding))
        )
        conn.commit()
        log(f"[DEBUG] Stored encoding for {profile_name}")
    except Exception as e:
        log(f"[DB ERROR] {e}")
    finally:
        if cur:  cur.close()
        if conn: conn.close()

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

# ------------------------- Video Processing -------------------------

def extract_encodings_from_video(video_path, doorbell_id):
    log(f"[INFO] Validating video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        log("[ERROR] Could not open video file.")
        return

    fps         = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration    = frame_count / fps if fps else 0
    if duration < MIN_VIDEO_DURATION:
        log(f"[ERROR] Video too short ({duration:.1f}s).")
        cap.release()
        return

    ret, frame = cap.read()
    if not ret or frame is None:
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

    name      = Path(video_path).stem
    saved     = 0
    step      = max(int(frame_count)//20, 1)

    for i in range(0, int(frame_count), step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            log(f"[WARN] Bad frame at {i}, skipping")
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)

        try:
            locs = face_recognition.face_locations(rgb)
            if not locs:
                continue
            encs = face_recognition.face_encodings(rgb, locs)
            for enc in encs:
                store_face_encoding(doorbell_id, name, enc)
                saved += 1
            if saved >= 20:
                break
        except Exception as e:
            log(f"[ERROR] face_recognition failed at frame {i}: {e}")

    cap.release()
    log(f"[INFO] Stored {saved} encodings for {name}")

# ------------------------- Auto‑processing Thread -------------------------

def process_latest_video(doorbell_id):
    for mp4 in ftp_dir.glob("*.mp4"):
        try:
            extract_encodings_from_video(str(mp4), doorbell_id)
            processed_dir.mkdir(exist_ok=True)
            shutil.move(str(mp4), str(processed_dir/mp4.name))
        except Exception as e:
            log(f"[ERROR] Auto-process {mp4.name}: {e}")

def auto_process_loop():
    while True:
        process_latest_video(DOORBELL_ID)
        time.sleep(5)

# ------------------------- Live Recognition (MAIN THREAD) -------------------------

def run_live_recognition():
    known_encs, known_names = fetch_all_encodings()
    log("[INFO] Running live facial recognition…")
    last_open_time = 0.0

    while True:
        frame = cam.capture_array().copy()   # deep‑copy avoids DMA reuse crash
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        rgb   = np.ascontiguousarray(rgb)

        try:
            locs = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, locs)
        except Exception as e:
            log(f"[ERROR] Recognition failed: {e}")
            continue

        for (t, r, b, l), enc in zip(locs, encs):
            matches = face_recognition.compare_faces(known_encs, enc)
            name    = "Unknown"
            if known_encs:
                dists = face_recognition.face_distance(known_encs, enc)
                idx   = np.argmin(dists)
                if matches[idx]:
                    name = known_names[idx]

            color = (0,255,0) if name != "Unknown" else (0,0,255)
            t, r, b, l = [x*4 for x in (t, r, b, l)]
            cv2.rectangle(frame, (l, t), (r, b), color, 2)
            cv2.putText(frame, name, (l+6, t-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            now = time.time()
            if name != "Unknown" and (now - last_open_time) >= OPEN_DOOR_COOLDOWN:
                send_command("3")
                last_open_time = now

        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ------------------------- Startup & Shutdown -------------------------

def setup():
    send_command("0")
    log("Middleman ready. Press 'q' in the preview window to quit.")

if __name__ == "__main__":
    setup()

    # background helpers
    threading.Thread(target=start_ftp_server,  daemon=True).start()
    threading.Thread(target=arduino_logger,    daemon=True).start()
    threading.Thread(target=auto_process_loop, daemon=True).start()

    try:
        run_live_recognition()           # -> Now runs on main thread (fixes seg‑fault)
    except KeyboardInterrupt:
        log("[INFO] KeyboardInterrupt – shutting down.")
    finally:
        cam.stop()
        cv2.destroyAllWindows()
        log("[INFO] Clean shutdown complete.")

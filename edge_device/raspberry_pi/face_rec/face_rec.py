# full Python setup for the Raspberry Pi side of the facial recognition 
# What this does:
# 1. Runs an FTP server to grab incoming vids
# 2. Goes through those videos and pulls out faces
# 3. Stores the face encodings in a MySQL db
# 4. Then loads those encodings and uses them to train a recognition model
# 5. Finally runs live recognition using the Pi cam, sending door commands via command.txt
# 6. Can also record a 5‑minute video with recognition active

# Dependencies:
# pip install face_recognition opencv-python mysql-connector-python pyftpdlib
# sudo apt install libmysqlclient-dev

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading
import os
import cv2
import face_recognition
import mysql.connector
import pickle
import time
import numpy as np
from picamera2 import Picamera2

# file used by the Arduino‑Pi middleman to pick up commands
COMMAND_FILE = "command.txt"

def send_command(cmd):
    """Write a single-digit command into command.txt for the Arduino."""
    with open(COMMAND_FILE, "w") as f:
        f.write(str(cmd))


# Some config stuff
FTP_USER = "pi"
FTP_PASSWORD = "raspberry"
FTP_DIR = "ftp_videos"
DB_CONFIG = {
    "host": "localhost",
    "user": "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}
KNOWN_USERS_DIR = "known_users"
UNKNOWN_DIR = "unknown_people"


# helper fn: rotates image based on angle we give it
def rotate_image(image, angle):
    if angle == 0:
        return image
    elif angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)


# Step 1: Start FTP server to accept uploaded videos
def start_ftp_server():
    os.makedirs(FTP_DIR, exist_ok=True)
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIR, perm="elradfmw")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("0.0.0.0", 2121), handler)
    print("[INFO] FTP Server started on port 2121...")
    server.serve_forever()


# Step 2: takes a video and tries to pull face encodings from it
def extract_encodings_from_video(video_path, user_id):
    person_name = os.path.splitext(os.path.basename(video_path))[0]
    print(f"[DEBUG] Processing video: {video_path} for user_id={user_id}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video file: {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(frame_count // 20, 1)
    saved = 0

    for i in range(0, frame_count, interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            print(f"[WARN] Could not read frame {i}")
            continue

        rotations = [0, 90, 180, 270]
        for angle in rotations:
            rotated = rotate_image(frame, angle)
            rgb = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            if locs:
                encs = face_recognition.face_encodings(rgb, locs)
                print(f"[DEBUG] Frame {i} (rotated {angle}°): Found {len(encs)} encoding(s)")
                for enc in encs:
                    store_face_encoding(user_id, person_name, enc)
                    saved += 1
                break

        if saved >= 20:
            break

    cap.release()
    print(f"[INFO] Stored {saved} encodings for {person_name}")


# Step 3: saves an encoding into the MySQL DB
def store_face_encoding(user_id, profile_name, encoding):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            INSERT INTO face_profiles (user_id, face_profile_name, face_data)
            VALUES (%s, %s, %s)
        """
        data_blob = pickle.dumps(encoding)
        cursor.execute(query, (user_id, profile_name, data_blob))
        conn.commit()
        print(f"[DEBUG] Stored encoding for {profile_name} (user_id={user_id})")
    except Exception as e:
        print(f"[DB ERROR] Failed to insert encoding: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Step 4: load all encodings+names from db so we can recognize later
def fetch_all_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT face_profile_name, face_data FROM face_profiles")
    results = cursor.fetchall()
    encodings = []
    names = []
    for name, blob in results:
        enc = pickle.loads(blob)
        encodings.append(enc)
        names.append(name)
    cursor.close()
    conn.close()
    return encodings, names


# Step 5: this does real-time recognition using PiCam,
#         annotates known (green) vs unknown (red), and sends commands
def live_recognition():
    print("[INFO] Fetching encodings from DB...")
    known_face_encodings, known_face_names = fetch_all_encodings()

    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"format": 'XRGB8888', "size": (640, 480)}
        )
    )
    picam2.start()
    print("[INFO] Starting live recognition. Press 'q' to quit.")

    cv_scaler = 4  # downsize for speed

    while True:
        frame = picam2.capture_array()
        small = cv2.resize(frame, (0, 0), fx=1/cv_scaler, fy=1/cv_scaler)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locs = face_recognition.face_locations(rgb_small)
        encs = face_recognition.face_encodings(rgb_small, locs)

        for (top, right, bottom, left), enc in zip(locs, encs):
            matches = face_recognition.compare_faces(known_face_encodings, enc)
            name = "Unknown"
            if known_face_encodings:
                dists = face_recognition.face_distance(known_face_encodings, enc)
                best_idx = np.argmin(dists)
                if matches[best_idx]:
                    name = known_face_names[best_idx]

            # scale coords back up for drawing
            top    *= cv_scaler
            right  *= cv_scaler
            bottom *= cv_scaler
            left   *= cv_scaler

            if name == "Unknown":
                # draw red box + label for unknown only
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left + 6, top - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # draw green box + name for known faces
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left + 6, top - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

              
                #  Code to send "Known Face" command to middleman
                
                send_command(3)
                time.sleep(0.1)

                
                #  Code to send "Open door" command to middleman
                
                send_command(1)

                # automatic door close after 5 seconds
                threading.Timer(5, lambda: send_command(2)).start()

        cv2.imshow("Facial Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.stop()


#  Step 6: Code to record 5‑minute video with live recognition active

def record_and_recognize(duration=300, output_path="recorded_video.mp4"):
    print(f"[INFO] Recording {duration//60}‑minute video with active recognition...")
    known_face_encodings, known_face_names = fetch_all_encodings()

    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"format": 'XRGB8888', "size": (640, 480)}
    )
    picam2.configure(config)
    picam2.start()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    out = cv2.VideoWriter(output_path, fourcc, fps, (640, 480))

    start_time = time.time()
    cv_scaler = 4

    while time.time() - start_time < duration:
        frame = picam2.capture_array()

        small = cv2.resize(frame, (0, 0), fx=1/cv_scaler, fy=1/cv_scaler)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locs = face_recognition.face_locations(rgb_small)
        encs = face_recognition.face_encodings(rgb_small, locs)

        for (top, right, bottom, left), enc in zip(locs, encs):
            matches = face_recognition.compare_faces(known_face_encodings, enc)
            name = "Unknown"
            if known_face_encodings:
                dists = face_recognition.face_distance(known_face_encodings, enc)
                best_idx = np.argmin(dists)
                if matches[best_idx]:
                    name = known_face_names[best_idx]

            top    *= cv_scaler
            right  *= cv_scaler
            bottom *= cv_scaler
            left   *= cv_scaler

            color = (0,255,0) if name != "Unknown" else (0,0,255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left + 6, top - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if name != "Unknown":
                send_command(3)
                time.sleep(0.1)
                send_command(1)
                threading.Timer(5, lambda: send_command(2)).start()

        out.write(frame)
        cv2.imshow("Recording with Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    out.release()
    picam2.stop()
    cv2.destroyAllWindows()
    print(f"[INFO] Saved video to {output_path}")



#  Step 7: Main processing of latest uploaded video

def process_latest_video(user_id):
    video_files = [f for f in os.listdir(FTP_DIR) if f.endswith(".mp4")]
    if not video_files:
        print("[INFO] No videos found.")
        return
    latest_video = max(video_files, key=lambda x: os.path.getctime(os.path.join(FTP_DIR, x)))
    full_path = os.path.join(FTP_DIR, latest_video)
    print(f"[DEBUG] Found latest video: {full_path}")
    extract_encodings_from_video(full_path, user_id)


#  Step 8: Interactive menu: process / recognize / record / exit

def main():
    threading.Thread(target=start_ftp_server, daemon=True).start()
    while True:
        print("\n[1] Process Latest Video")
        print("[2] Start Facial Recognition Only")
        print("[3] Record 5‑Minute Video with Recognition")
        print("[4] Exit")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            uid = input("Enter user_id to associate encodings: ").strip()
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

# face_rec.py
# full Python setup for the Raspberry Pi side of the facial recognition 
# What this does:
# 1. Runs an FTP server to grab incoming vids
# 2. Goes through those videos and pulls out faces (with validation)
# 3. Stores the face encodings in a MySQL db
# 4. Then loads those encodings and uses them to train a recognition model
# 5. Finally runs live recognition using the Pi cam, sending door commands via command.txt
# 6. Can also record a 5-minute video with recognition active
# 7. Provides a simple menu to trigger processing / recognition / recording

# Dependencies:
# pip install face_recognition opencv-python mysql-connector-python pyftpdlib
# sudo apt install libmysqlclient-dev

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers    import FTPHandler
from pyftpdlib.servers     import FTPServer
import threading, os, cv2, time, pickle, mysql.connector, face_recognition, numpy as np
from picamera2             import Picamera2

is_recording = False

cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"format":'XRGB8888',"size":(640,480)}))
# file used by the Arduino-Pi middleman to pick up commands
COMMAND_FILE = "command.txt"
def send_command(cmd):
    """Write a single-digit command into command.txt for the Arduino."""
    with open(COMMAND_FILE, "w") as f:
        f.write(str(cmd))

# validation constants
MIN_VIDEO_DURATION   = 15    # seconds
BRIGHTNESS_THRESHOLD = 32    # mean gray value, 0–255

# Some config stuff
FTP_USER     = "pi"
FTP_PASSWORD = "raspberry"
FTP_DIR      = "ftp_videos"
DB_CONFIG    = {
    "host":     "localhost",
    "user":     "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}

# helper fn: rotates image based on angle we give it
def rotate_image(image, angle):
    if angle == 0:
        return image
    elif angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    else:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

# Step 1: Start FTP server to accept uploaded videos
def start_ftp_server():
    os.makedirs(FTP_DIR, exist_ok=True)
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIR, perm="elradfmw")
    handler = FTPHandler; handler.authorizer = authorizer
    server  = FTPServer(("0.0.0.0", 2121), handler)
    print("[INFO] FTP Server started on port 2121...")
    server.serve_forever()

# Step 2: validate & extract face encodings from video
def extract_encodings_from_video(video_path, user_id):
    print(f"[INFO] Validating video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video file: {video_path}")
        return

    fps         = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration    = frame_count/fps if fps>0 else 0
    if duration < MIN_VIDEO_DURATION:
        print(f"[ERROR] Video too short ({duration:.1f}s). Minimum is {MIN_VIDEO_DURATION}s.")
        cap.release(); return

    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Could not read first frame for brightness check.")
        cap.release(); return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if gray.mean() < BRIGHTNESS_THRESHOLD:
        print(f"[ERROR] Video too dark (avg brightness {gray.mean():.1f}). Please record in better lighting.")
        cap.release(); return

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    print(f"[INFO] Video OK (duration {duration:.1f}s, brightness {gray.mean():.1f})")

    person_name = os.path.splitext(os.path.basename(video_path))[0]
    interval    = max(int(frame_count)//20, 1)
    saved       = 0

    for i in range(0, int(frame_count), interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            print(f"[WARN] Could not read frame {i}")
            continue

        for angle in (0, 90, 180, 270):
            rgb = cv2.cvtColor(rotate_image(frame, angle), cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            if locs:
                encs = face_recognition.face_encodings(rgb, locs)
                print(f"[DEBUG] Frame {i} (rotated {angle}°): Found {len(encs)} encoding(s)")
                for e in encs:
                    store_face_encoding(user_id, person_name, e)
                    saved += 1
                break
        if saved >= 20:
            break

    cap.release()
    print(f"[INFO] Stored {saved} encodings for {person_name}")

# Step 3: save encoding blob to MySQL
def store_face_encoding(uid, name, enc):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO face_profiles (user_id, face_profile_name, face_data) VALUES (%s,%s,%s)",
            (uid, name, pickle.dumps(enc))
        )
        conn.commit()
        print(f"[DEBUG] Stored {name} (uid={uid})")
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        cur.close(); conn.close()

# Step 4: fetch all encodings for recognition
def fetch_all_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute("SELECT face_profile_name, face_data FROM face_profiles")
    encs, names = [], []
    for n,b in cur.fetchall():
        names.append(n); encs.append(pickle.loads(b))
    cur.close(); conn.close()
    return encs, names

# Step 5: live recognition (optional duration)
def live_recognition(duration=None):
    known_encs, known_names = fetch_all_encodings()
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(main={"format":'XRGB8888',"size":(640,480)}))
    cam.start()
    print("[INFO] Live recognition started")
    start = time.time()
    while True:
        if duration and time.time()-start>=duration:
            break
        frame = cam.capture_array()
        small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locs  = face_recognition.face_locations(rgb)
        encs  = face_recognition.face_encodings(rgb, locs)
        for (t,r,b,l),e in zip(locs,encs):
            m = face_recognition.compare_faces(known_encs, e)
            name="Unknown"
            if known_encs:
                d = face_recognition.face_distance(known_encs, e)
                idx = np.argmin(d)
                if m[idx]: name=known_names[idx]
            t,r,b,l=[x*4 for x in (t,r,b,l)]
            col=(0,255,0) if name!="Unknown" else (0,0,255)
            cv2.rectangle(frame,(l,t),(r,b),col,2)
            cv2.putText(frame,name,(l+6,t-6),cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
            if name!="Unknown":
                send_command(3); time.sleep(0.1); send_command(1)
                threading.Timer(5,lambda:send_command(2)).start()
        cv2.imshow("Live Recognition", frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
    cam.stop(); cv2.destroyAllWindows()
    print("[INFO] Live recognition ended")

# Step 6: record + recognition
def record_and_recognize(duration=30, output_path="recorded_video.mp4"):
    global is_recording
    is_recording= True
    
    known_encs, known_names = fetch_all_encodings()
    
    cam.start()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(output_path, fourcc, 30, (640,480))
    print(f"[INFO] Recording {duration//60}-minute video with recognition…")
    start = time.time()
    while time.time()-start<duration:
        frame = cam.capture_array()
        small = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
        rgb   = cv2.cvtColor(small,cv2.COLOR_BGR2RGB)
        locs  = face_recognition.face_locations(rgb)
        encs  = face_recognition.face_encodings(rgb, locs)
        for (t,r,b,l),e in zip(locs,encs):
            m = face_recognition.compare_faces(known_encs, e)
            name="Unknown"
            if known_encs:
                d = face_recognition.face_distance(known_encs, e)
                idx = np.argmin(d)
                if m[idx]: name=known_names[idx]
            t,r,b,l=[x*4 for x in (t,r,b,l)]
            col=(0,255,0) if name!="Unknown" else (0,0,255)
            cv2.rectangle(frame,(l,t),(r,b),col,2)
            cv2.putText(frame,name,(l+6,t-6),cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
            if name!="Unknown":
                send_command(3); time.sleep(0.1)
        out.write(frame)
        cv2.imshow("Recording + Recognition", frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
    out.release()
    cam.stop()
    cv2.destroyAllWindows()
    print(f"[INFO] Saved video to {output_path}")
    is_recording = False

# Step 7: process latest uploaded video
def process_latest_video(user_id):
    files = [f for f in os.listdir(FTP_DIR) if f.endswith(".mp4")]
    if not files:
        print("[INFO] No videos found."); return
    latest = max(files, key=lambda f: os.path.getctime(os.path.join(FTP_DIR, f)))
    extract_encodings_from_video(os.path.join(FTP_DIR, latest), user_id)

# Step 8: interactive menu
def main():
    threading.Thread(target=start_ftp_server, daemon=True).start()
    while True:
        print("\n[1] Process Latest Video")
        print("[2] Start Live Recognition")
        print("[3] Record 5-Minute Video with Recognition")
        print("[4] Exit")
        c = input("Choice: ").strip()
        if c=='1':
            uid = input("user_id: ").strip()
            process_latest_video(uid)
        elif c=='2':
            live_recognition()
        elif c=='3':
            record_and_recognize()
        elif c=='4':
            break
        else:
            print("Invalid choice.")

if __name__=="__main__":
    main()

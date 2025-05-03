# ------------------------- Imports -------------------------

import os, cv2, pickle, shutil, threading, time, datetime, serial, mysql.connector
import serial.tools.list_ports
import face_recognition
import numpy as np
from pathlib import Path
from picamera2 import Picamera2
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from libcamera import Transform

import sendMotionNotif

# ------------------------- Configuration -------------------------

# Function to dynamically find the usb port the Arduino is connected to
def find_arduino_port():
    # Gets all the ports currently in use
	ports = serial.tools.list_ports.comports()

    # Checking each port to see if it is the Arduino port
	for port in ports:
		if ("Arduino" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device): # Found Arduino port
            # Returns the usb port that the Arduino is connected to
			return port.device 
			
	return None

# Arduino variables configuration    
pi_port = find_arduino_port()
baud_rate = 9600
timeout_s = 0.1

# FTP server variables configuration
FTP_USER           = "pi"
FTP_PASSWORD       = "raspberry"

# File names configuration
FTP_DIR            = "ftp_videos"
PROCESSED_DIR      = "processed_videos"
COMMAND_FILE       = "command.txt"

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db",
}

# Doorbell configuration
DOORBELL_ID = 1

# Threshold configuration
MIN_VIDEO_DURATION = 15     # seconds
BRIGHTNESS_THRESHOLD = 32     # mean gray value 0–255

# Door cooldown configuration
OPEN_DOOR_COOLDOWN = 5      # seconds between re‑opening

# ------------------------- Paths & Files -------------------------

# Getting parent directory
base_dir = Path(__file__).parent

# File directories
log_file = base_dir / "log.txt"
ftp_dir = base_dir / FTP_DIR
processed_dir = base_dir / PROCESSED_DIR
command_file = base_dir / COMMAND_FILE

# Ensures that FTP directory and processed videos directory are always present
ftp_dir.mkdir(exist_ok=True)
processed_dir.mkdir(exist_ok=True)

# ------------------------- Hardware Setup -------------------------

# Arduino object creation
arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s)

# Camera creation and configuration
cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"format": "XRGB8888", "size": (640, 480)}, transform=Transform(rotation=180)))


# ------------------------- Global Locks ------------------------- (need help commenting this)

DLIB_LOCK = threading.Lock()  # All dlib calls are now single‑threaded

# ------------------------- Utility Functions -------------------------

# Function that creates and prints a log message to terminal and log_file
def log(msg):
    # Gets current date and time
    now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    # Creates log message
    line = f"{now} | {msg}"

    # Prints log message for debugging
    print(line)

    # Opens log file to append log message
    with log_file.open("a") as f:
        # Adds message and skips to next line
        f.write(line + "\n") 

        # Instantly appends log message
        f.flush()

# Function to send a command to the Arduino
def send_command(cmd):
    try:
        # Sends the command to the Arduino
        arduino.write(bytes(cmd, 'utf-8'))
    except Exception as e: # Catches any error
        # Logs error
        log(f"[ERROR] Sending command {cmd}: {e}")

    # Gives time for Arduino to execute command
    time.sleep(0.05)
    
    # Checks which command was sent
    if   cmd == "0": # Python script startup
        # Logs message
        log("Middleman startup complete.")
    elif cmd == "1": # Open door command
        # Logs message
        log("Phone has requested to open the door.")
    elif cmd == "2": # Close door command
        # Logs message
        log("Phone has requested to close the door.")
    elif cmd == "3": # Known face detected
        # Logs message
        log("Known face detected.")
    elif cmd == "4": # Blocked face detected
        # Logs message
        log("Blocked face detected.")

# Function to read and log any messages from the Arduino
def read():
    try:
        # Reads the Arduino Serial for any new messages
        line = arduino.readline().decode("utf-8", errors="ignore").strip()

        # Message received from Arduino
        if line:
            # Logs message
            log(line)
    except Exception as e: # Catches any error
        # Logs error
        log(f"[ERROR] Reading Arduino: {e}")

# Function to check for commands from command_file
def check_command():
    # Check if command_file exists
    if command_file.is_file(): # Exists

        # Opens command_file
        with command_file.open('r') as f:

            # Reads the data in command_file
            command = f.read().strip()

        # Removes command_file from file directory to not repeat command
        command_file.unlink()

        # Returns command
        return command
    
    # Returns nothing is there is no command_file
    return None

def python_loop():
    while True:
        # Gets command from command_file
        command = check_command()

        # Checks if there is a command
        if command: # There is a command
            send_command(command)

        # Reads and logs any messages sent from the Arduino
        read()

        # Adds small delay to prevent CPU hogging
        time.sleep(0.1)


# ------------------------- dlib‑safe wrappers -------------------------

def dlib_face_locations(img):
    with DLIB_LOCK:
        return face_recognition.face_locations(img)

def dlib_face_encodings(img, locs=None):
    with DLIB_LOCK:
        return face_recognition.face_encodings(img, locs)

# ------------------------- Orientation Helpers -------------------------
ROTATE_CODE = {
    0:   None,
    90:  cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}

def rotate_image(img, angle):
    code = ROTATE_CODE[angle]
    return img if code is None else cv2.rotate(img, code)

def find_faces_multi_orientation(img_rgb):
    """Return encodings for the first rotation (0/90/180/270) that yields faces."""
    for angle in (0, 90, 180, 270):
        test = rotate_image(img_rgb, angle) if angle else img_rgb
        test = np.ascontiguousarray(test)
        locs = dlib_face_locations(test)
        if locs:
            return dlib_face_encodings(test, locs)
    return []

# ------------------------- File‑upload race guard -------------------------

def is_file_complete(path: Path, wait_s: float = 1.0) -> bool:
    """Return True if *path* size stays unchanged for *wait_s* seconds."""
    s1 = path.stat().st_size
    time.sleep(wait_s)
    return s1 == path.stat().st_size

# ------------------------- DB Helpers -------------------------

def store_face_encoding(doorbell_id, profile_name, encoding):
    conn = cur = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO face_profiles (doorbell_id, face_profile_name, face_data) "
            "VALUES (%s, %s, %s)",
            (doorbell_id, profile_name, pickle.dumps(encoding)),
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
    cur.close(); conn.close()
    return encs, names

# ------------------------- Video Processing -------------------------

def extract_encodings_from_video(video_path: str, doorbell_id: int):
    log(f"[INFO] Validating video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        log("[ERROR] Could not open video file."); return

    fps   = cap.get(cv2.CAP_PROP_FPS)
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    dur   = total / fps if fps else 0
    if dur < MIN_VIDEO_DURATION:
        log(f"[ERROR] Video too short ({dur:.1f}s)."); cap.release(); return

    ok, first = cap.read()
    if not ok:
        log("[ERROR] Could not read first frame."); cap.release(); return
    if cv2.cvtColor(first, cv2.COLOR_BGR2GRAY).mean() < BRIGHTNESS_THRESHOLD:
        log("[ERROR] Too dark."); cap.release(); return

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    log(f"[INFO] Video OK ({dur:.1f}s)")

    step   = max(int(total) // 20, 1)
    saved  = 0
    name   = Path(video_path).stem

    for i in range(0, int(total), step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if not ok:
            log(f"[WARN] Bad frame at {i}"); continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = find_faces_multi_orientation(rgb)
        for enc in encs:
            store_face_encoding(doorbell_id, name, enc)
            saved += 1
        if saved >= 20:
            break
    cap.release()
    log(f"[INFO] Stored {saved} encodings for {name}")

# ------------------------- Auto‑processing Thread -------------------------

def has_been_processed(path: Path) -> bool:            # 
    """True if a file with the same name already sits in processed_videos/."""  #
    return (processed_dir / path.name).exists()        # 

def process_latest_video(doorbell_id):
    for mp4 in ftp_dir.glob("*.mp4"):
        if not is_file_complete(mp4):
            continue  # still being uploaded
        if has_been_processed(mp4):                   
            continue  # same-named file already handled once 
        try:
            extract_encodings_from_video(str(mp4), doorbell_id)
            shutil.move(str(mp4), str(processed_dir / mp4.name))
        except Exception as e:
            log(f"[ERROR] Auto-process {mp4.name}: {e}")

def auto_process_loop():
    while True:
        try:
            process_latest_video(DOORBELL_ID)
        except Exception as e:
            log(f"[ERROR] auto_process_loop: {e}")
        time.sleep(5)

# ------------------------- Live Recognition (MAIN THREAD) -------------------------

def run_live_recognition():
    known_encs, known_names = fetch_all_encodings()
    log("[INFO] Running live facial recognition…")
    last_open_time = 0.0

    while True:
        frame = cam.capture_array().copy()
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        rgb   = np.ascontiguousarray(rgb)

        try:
            locs = dlib_face_locations(rgb)
            encs = dlib_face_encodings(rgb, locs)
        except Exception as e:
            log(f"[ERROR] Recognition failed: {e}"); continue

        for (t, r, b, l), enc in zip(locs, encs):
            
            matches = face_recognition.compare_faces(known_encs, enc)  # compare still OK without lock
            name    = "Unknown"
            if known_encs:
                dists = face_recognition.face_distance(known_encs, enc)
                idx   = np.argmin(dists)
                if matches[idx]:
                    name = known_names[idx]

            col = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            t, r, b, l = [x * 4 for x in (t, r, b, l)]
            cv2.rectangle(frame, (l, t), (r, b), col, 2)
            cv2.putText(frame, name, (l + 6, t - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)

            now = time.time()
            if name != "Unknown" and (now - last_open_time) >= OPEN_DOOR_COOLDOWN:
                send_command("3")
                last_open_time = now
            elif name == "Unknown" and (now - last_open_time) >= OPEN_DOOR_COOLDOWN:
                # Send notification
                sendMotionNotif.personAtDoorNotif()

        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ------------------------- FTP Server Thread -------------------------

def start_ftp_server():
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, str(ftp_dir), perm="elradfmw")
    handler = FTPHandler; handler.authorizer = authorizer
    server  = FTPServer(("0.0.0.0", 2121), handler)
    log("[INFO] FTP Server started on port 2121.")
    server.serve_forever()

# ------------------------- Startup & Main loop -------------------------

# Function that sets up and activates all needed components
def startup():
    # Connects to the global arduino object
    global arduino

    # Activates the camera
    cam.start()

    # Sends a command to the Arduino to restart
    send_command("0")

    # Waits for Arduino to reset
    time.sleep(2)
    
    # Finds the port the arduino is in
    port = find_arduino_port()

    # Recreates the arduino object with the new port 
    arduino = serial.Serial(port, baudrate=baud_rate, timeout=timeout_s)

    # Prints message for debugging
    print("Listening for log messages...")

def main():
    # Runs startup sequence
    startup()

    # Starts the ftp server
    threading.Thread(target=start_ftp_server,  daemon=True).start()
    
    # Starts the video processing loop
    threading.Thread(target=auto_process_loop, daemon=True).start()

    # Starts the command and logging loop
    threading.Thread(target=python_loop,       daemon=True).start()

    try:
        # Starts live recognition
        run_live_recognition()
    except KeyboardInterrupt: # User stops the program with ctrl-C
        # Logs shutdown sequence
        log("[INFO] KeyboardInterrupt – shutting down …")
    finally:
        # Stops camera object
        cam.stop()

        # Closes all windows
        cv2.destroyAllWindows()

        # Logs shutdown complete message
        log("[INFO] Clean shutdown complete.")

#----------------------- Running -------------------------
if __name__ == "__main__":
    main()

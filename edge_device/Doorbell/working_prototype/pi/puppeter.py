#########################################################
#
#  Main Code to communicate between Arduino, Pi and App
#
#########################################################

# Library imports
import serial
import threading
import datetime
import time
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers    import FTPHandler
from pyftpdlib.servers     import FTPServer
import os, cv2, pickle, mysql.connector, face_recognition, numpy as np
from picamera2             import Picamera2

# ——————————————————————————————————————————————————————
# Configuration
# ——————————————————————————————————————————————————————

# USB port configurations for ease of testing
my_pc_port   = "COM9" 
lab_port     = "COM4"
pi_port      = "/dev/ttyACM0" # Main one we will be using

# Arduino settings
baud_rate    = 9600
timeout_s    = 0.1

# Directory locations
directory    = Path(__file__).parent
log_file     = directory / "log.txt"
command_file = directory / "command.txt"

cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"format":'XRGB8888',"size":(640,480)}))

isRecord=False

DB_CONFIG = {
    "host":     "localhost",
    "user":     "door_user",
    "password": "door_user_door_user",
    "database": "smart_door_db"
}

COMMAND_FILE = "command.txt"

# ——————————————————————————————————————————————————————
# Setup Arduino serial
# ——————————————————————————————————————————————————————

# Sets the arduino object to read from
arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s) # Change first variable to use different ports

# ——————————————————————————————————————————————————————
# Functions
# ——————————————————————————————————————————————————————

# Function to read arduino messages
def read():
    # Tries to read the Serial from arduino
    line = arduino.readline().decode('utf-8').strip()

    # Checks if there is a message
    if line: # There is a message
        # Returns message
        return line
    else: # There is no message
        # Returns nothing
        return None

# Function to check if there is a command from app or facial recognition
def check_command():
    # Checks if the command_file exists
    if command_file.is_file(): # Command_file exists
        # Reads the contents in the command file
        cmd = command_file.read_text().strip()

        # Deletes the command_file for cleaner look
        command_file.unlink()

        # Returns command
        return cmd

    # Returns nothing if there is no command
    return None

# Function to log a message to a log file
def log(msg):
    # Gets and formats current date and time 
    now   = datetime.datetime.now().strftime("%x %X")

    # Sets up the log message
    entry = f"{now} | {msg}"

    # Prints log message for debugging
    print(entry)
    
    # Opens log file in append mode
    with log_file.open("a") as f:
        # Writes into log file and moves to a new line
        f.write(entry + "\n")

        # Instantly updates the log file
        f.flush()

# Function to send a command to the arduino
def command(cmd):
    # Sends the command to the arduino
    arduino.write(bytes(cmd, 'utf-8'))

    # Gives the system time to run the command
    time.sleep(0.05)

    # Checks which command is sent
    if     cmd == "0": # System startup
        log("Middleman startup complete.")
    elif   cmd == "1": # Manual open door
        log("Phone has requested to open the door.")
    elif cmd == "2": # Manual close door
        log("Phone has requested to close the door.")
    elif cmd == "3": # Detected known face
        log("Known face detected.")
    elif cmd == "4": # Detected blocked face
        log("Blocked face detected.")

def setup():
    # Sends reset command to Arduino
    command("0")

    # Prints starting message for clarity when debugging
    print("Listening for log messages...")
    
def fetch_all_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute("SELECT face_profile_name, face_data FROM face_profiles")
    encs, names = [], []
    for n,b in cur.fetchall():
        names.append(n); encs.append(pickle.loads(b))
    cur.close(); conn.close()
    return encs, names
    
def timer(duration=30, output_path="recorded_video.mp4"):
	global isRecord
	isRecord=True
	
	known_encs, known_names = fetch_all_encodings()
	
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter("recorded_video.mp4", fourcc, 30,(640,480))
    
	cam.start()
	print(f"[INFO] Recording {duration//60}-minute video with recognition...")
	start = time.time()
	while time.time()-start < duration:
		frame = cam.capture_array()
		frame = record_and_recognize(frame, known_encs, known_names)
		out.write(frame)
		cv2.imshow("Recording + Recognition", frame)
		
		if cv2.waitKey(1) & 0xFF == ord("q"):
			break
			
	out.release()
	cam.stop()
	cv2.destroyAllWindows()
	print(f"[INFO] Saved video to {output_path}")
	
	isRecord=False
	
    
def record_and_recognize(frame, known_encs, known_names):
	small = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
	rgb   = cv2.cvtColor(small,cv2.COLOR_BGR2RGB)
	locs  = face_recognition.face_locations(rgb)
	encs  = face_recognition.face_encodings(rgb, locs)
	
	for (t,r,b,l),e in zip(locs,encs):
		name="Unknown"
		if known_encs:
			d = face_recognition.face_distance(known_encs, e)
			m = face_recognition.compare_faces(known_encs, e)
			idx = np.argmin(d)
			if m[idx]: 
				name=known_names[idx]
			
		t,r,b,l=[x*4 for x in (t,r,b,l)]
		col=(0,255,0) if name!="Unknown" else (0,0,255)
		cv2.rectangle(frame,(l,t),(r,b),col,2)
		cv2.putText(frame,name,(l+6,t-6),cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
		
		if name!="Unknown":
			send_command(3)
			time.sleep(0.1)
	
	return frame
	
def send_command(cmd):
    """Write a single-digit command into command.txt for the Arduino."""
    with open(COMMAND_FILE, "w") as f:
        f.write(str(cmd))

# ——————————————————————————————————————————————————————
# Main Code
# ——————————————————————————————————————————————————————

# Starts up Arduino script for syncronized logs
setup()

# Starts loop
while True:
    # Checks if there is a command from app or the facial recogition
    cmd = check_command()

    if cmd: # There is a command
        # Sends command to arduino and logs the command
        command(cmd) 

    # Reads the log message from Arduino to add to logging
    msg = read()

    if msg: # There is a message
        # Logs the message
        log(msg)

        # Checks if the log message is linked to an action
        if msg == "Object is a person.": # Arduino detects a person
            # Checks if the system is already recording
            if not isRecord: # If system is not recording
                # Starts recording and face recognition
                threading.Thread(target=timer, daemon=True).start()

    # Adds a tiny delay to avoid busy-loop
    time.sleep(0.01)

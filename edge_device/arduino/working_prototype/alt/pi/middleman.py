# middleman.py
#########################################################
#
#  Main Code to communicate between Arduino, Pi and App
#
#########################################################

import serial
import threading
import datetime
import time
import os
from pathlib import Path
import face_rec  # assumes face_rec.py is in the same directory

# Port variables
my_pc_port = "COM9"
lab_port   = "COM4"
pi_port    = "/dev/ttyACM0"

# Paths
directory    = Path(__file__).parent
log_file     = directory / "log.txt"
command_file = directory / "command.txt"

# Setup Arduino serial
arduino = serial.Serial(pi_port, baudrate=9600, timeout=0.1)

# Flag to prevent retriggering while recording is active
recording_active = False

print("Listening for log messages...")

def read():
    """Read and return a line from Arduino serial, or None if empty."""
    data = arduino.readline().decode('utf-8').strip()
    return data if data else None

def check_command():
    """If command_file exists, read & remove it, then return its contents."""
    if command_file.is_file():
        cmd = command_file.read_text().strip()
        command_file.unlink()
        return cmd
    return None

def log(msg):
    """Append msg to log.txt with timestamp, and print it."""
    now   = datetime.datetime.now()
    entry = now.strftime("%x %X") + " | " + msg
    print(entry)
    with log_file.open("a") as f:
        f.write(entry + "\n")
        f.flush()

def command_check(cmd):
    """Send cmd to Arduino and log the action."""
    arduino.write(bytes(cmd, 'utf-8'))
    time.sleep(0.05)
    if   cmd == "1":
        log("Phone has opened the door.")
    elif cmd == "2":
        log("Phone has closed the door.")
    elif cmd == "3":
        log("Known face detected.")
    elif cmd == "4":
        log("Blocked face detected.")

def reset_recording_flag():
    """Called after the 5-minute window to allow retriggering."""
    global recording_active
    recording_active = False
    log("Recording window ended; ready for next trigger.")

# Main Loop
while True:
    # 1) Handle any phone‐initiated commands
    cmd = check_command()
    if cmd:
        command_check(cmd)

    # 2) Read any serial messages from Arduino
    msg = read()
    if msg:
        log(f"Arduino → {msg}")

        # 3) Trigger recording+recognition on first person detection
        if msg == "Object is a person.":
            if not recording_active:
                recording_active = True
                log("Triggering 5-minute record_and_recognize")

                # start 5-minute video recording + recognition
                threading.Thread(
                    target=face_rec.record_and_recognize,
                    kwargs={"duration": 300},
                    daemon=True
                ).start()

                # schedule flag reset after 5 minutes
                threading.Timer(300, reset_recording_flag).start()
            else:
                log("Recording in progress; trigger ignored.")

    time.sleep(0.01)
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
pi_port    = "placeholder"

# Getting directory
directory    = Path(__file__).parent

# Setting file path for log.txt
log_file     = directory / "log.txt"

# Setting file to receive commands from
command_file = directory / "command.txt"

# Setting up Arduino connection
arduino = serial.Serial(my_pc_port, baudrate=9600, timeout=0.1)

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
    now = datetime.datetime.now()
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

# Main Loop
while True:
    # 1) Handle any phone‐initiated commands
    cmd = check_command()
    if cmd:
        command_check(cmd)

    # 2) Read any serial messages from Arduino
    log_msg = read()
    if log_msg:
        log(log_msg)

        # 3) Trigger face_rec when Arduino reports a person
        if log_msg == "Object is a person.":
            log("Triggering live_recognition and record_and_recognize for 5 minutes")
            # start live recognition for 5 minutes
            threading.Thread(
                target=face_rec.live_recognition,
                kwargs={"duration": 300},
                daemon=True
            ).start()
            # start 5-minute recording + recognition
            threading.Thread(
                target=face_rec.record_and_recognize,
                kwargs={"duration": 300},
                daemon=True
            ).start()

    time.sleep(0.01)

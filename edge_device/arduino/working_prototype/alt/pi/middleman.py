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
arduino = serial.Serial(my_pc_port, baudrate=9600, timeout=0.1)

print("Listening for log messages...")

def read():
    data = arduino.readline().decode('utf-8').strip()
    return data if data else None

def check_command():
    if command_file.is_file():
        cmd = command_file.read_text().strip()
        command_file.unlink()
        return cmd
    return None

def log(msg):
    now   = datetime.datetime.now()
    entry = now.strftime("%x %X") + " | " + msg
    print(entry)
    with log_file.open("a") as f:
        f.write(entry + "\n")
        f.flush()

def command_check(cmd):
    arduino.write(bytes(cmd, 'utf-8'))
    time.sleep(0.05)
    if   cmd == "1": log("Phone has opened the door.")
    elif cmd == "2": log("Phone has closed the door.")
    elif cmd == "3": log("Known face detected.")
    elif cmd == "4": log("Blocked face detected.")

# Main loop
while True:
    # Handle phone‐initiated commands
    cmd = check_command()
    if cmd:
        command_check(cmd)

    # Read Arduino serial
    msg = read()
    if msg:
        log(f"Arduino → {msg}")

        # Trigger only the recording+recognition function
        if msg == "Object is a person.":
            log("Triggering 5-minute record+recognition")
            threading.Thread(
                target=face_rec.record_and_recognize,
                kwargs={"duration": 300},
                daemon=True
            ).start()

    time.sleep(0.01)
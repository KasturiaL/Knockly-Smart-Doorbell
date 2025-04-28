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

# Script imports
import face_rec 

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
    arduino.write(cmd.encode())

    # Gives the system time to run the command
    time.sleep(0.05)

    # Checks which command is sent
    if   cmd == "1": # Manual open door
        log("Phone has requested to open the door.")
    elif cmd == "2": # Manual close door
        log("Phone has requested to close the door.")
    elif cmd == "3": # Detected known face
        log("Known face detected.")
    elif cmd == "4": # Detected blocked face
        log("Blocked face detected.")

# ——————————————————————————————————————————————————————
# Main Code
# ——————————————————————————————————————————————————————
# Prints starting message for clarity when debugging
print("Listening for log messages...")

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
        log("msg")

        # Checks if the log message is linked to an action
        if msg == "Object is a person.": # Arduino detects a person
            # Checks if the system is already recording
            if not face_rec.is_recording: # If system is not recording
                # Starts recording and face recognition
                face_rec.record_and_recognize()

    # Adds a tiny delay to avoid busy-loop
    time.sleep(0.01)

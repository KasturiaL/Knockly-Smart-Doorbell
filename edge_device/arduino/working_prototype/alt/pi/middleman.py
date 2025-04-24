#########################################################
#
#  Main Code to communicate between Arduino, Pi and App
#
#########################################################


# Importing libraries
import serial
import datetime
import time
import os
from pathlib import Path

# Port variables
my_pc_port = "COM9"
lab_port = "COM4"
pi_port = "placeholder"

# Getting directory
directory = Path(__file__).parent

# Setting file path for log.txt
log_file = directory / "log.txt"

# Setting file to receive commands from
command_file = directory / "command.txt"

# Setting up Arduino connection
arduino = serial.Serial(my_pc_port, baudrate=9600, timeout=.1)

# Debugging
print("Listening for log messages...")

# Function to read from arduino Serial
def read():
    # Reading and cleaning data
    data = arduino.readline().decode('utf-8').strip()

    # Returning data if there is data sent
    if data:
        return data
    else:
        return None

# Function to check for commands from command_file
def check_command():
    # Check if command_file exists
    if command_file.is_file(): # Exists

        # Opens command_file
        with command_file.open('r') as f:

            # Reads the data in command_file
            command = f.read().strip()

        # Removes command_file from file directory to better visability
        os.remove(command_file)

        # Returns command
        return command
    
    # Returns nothing is there is no command_file
    return None

def log(msg):
    # Opening log.txt
    with log_file.open("a") as f:
        # Getting current date and time
        current = datetime.datetime.now()

        # Setting date variable
        date = current.strftime("%x")

        # Setting time variable
        time = current.strftime("%X")

        # Debugging
        print(date + " " + time + " | " + msg)

        # Writing to log.txt
        f.write(date + " " + time + " | " + msg + "\n")

        # Instant write to log.txt
        f.flush()

def command_check(command):
    # Writes command to arduino
    arduino.write(bytes(command, 'utf-8'))
    
    # Gives the system time to execute command
    time.sleep(0.05)

    # Check which command was issues for logging purposes
    if command == "1": # Open door
        # Prints log entry
        log("Phone has opened the door.")
    elif command == "2": # Close door
        # Prints log entry
        log("Phone has closed the door.")
    elif command == "3": # Known face detected
        # Prints log entry
        log("Known face detected.")
    elif command == "4": # Blocked face detected
        # Prints log entry
        log("Blocked face detected.")

# Main Loop
while True:
    # Gets command from command_file
    command = check_command()

    # Checks if there is a command
    if command: # There is a command
        command_check(command)
        
    # Reading Serial message from arduino
    log_msg = read()

    # Check if there is message
    if log_msg != None: # Message
        log(log_msg)
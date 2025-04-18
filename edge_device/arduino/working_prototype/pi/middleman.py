#########################################################
#
#  Main Code to communicate between Arduino, Pi and App
#
#########################################################


# Importing Libraries
import serial
import time
import os

# Port variable
# Change this when using on raspberry pi due to different port names
usb_port = 'COM9'

# Setting file to receive commands from
command_file = "command.txt"

# Setting up Arduino connection
arduino = serial.Serial(usb_port, baudrate=9600, timeout=.1)

# Debugging
print("Listening for commands...")

# Function to check for commands from command_file
def check_command():
    # Check if command_file exists
    if os.path.exists(command_file): # Exists

        # Opens command_file
        with open(command_file, 'r') as f:

            # Reads the data in command_file
            command = f.read().strip()

        # Removes command_file from file directory to better visability
        os.remove(command_file)

        # Returns command
        return command
    
    # Returns nothing is there is no command_file
    return None

# Main Loop
while True:

    # Gets command from command_file
    command = check_command()

    # Checks if there is a command
    if command: # There is a command

        # Writes command to arduino
        arduino.write(bytes(command, 'utf-8'))
        
        # Gives the system time to execute command
        time.sleep(0.05)

        # Check which command was issues for logging purposes
        if command == "1": # Open door
            # Prints log entry
            print("Door opened.")
        elif command == "2": # Close door
            # Prints log entry
            print("Door closed.")
        elif command == "3": # Known face detected
            # Prints log entry
            print("Known face detected.")
        elif command == "4": # Blocked face detected
            # Prints log entry
            print("Blocked face detected.")
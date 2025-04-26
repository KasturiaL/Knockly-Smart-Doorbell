# Importing libraries
import serial
import datetime
from pathlib import Path

# Getting directory
directory = Path(__file__).parent

# Setting file path for log.txt
path = directory / "log.txt"

# Set usb port here
usb_port = 'COM9'

# Setting for arduino communication (keep as same settings as arduino)
arduino = serial.Serial(usb_port, baudrate=9600, timeout=.1)

# Debugging
print("Listening for commands...")

# Function to read from arduino Serial
def read():
    # Reading and cleaning data
    data = arduino.readline().decode('utf-8').strip()

    # Returning data if there is data sent
    if data:
        return data
    else:
        return None

# Opening log.txt
with path.open("a") as f:
    # Main loop
    while True:
        # Reading Serial message from arduino
        log_msg = read()

        # Check if there is message
        if log_msg != None: # Message
            # Getting current date and time
            current = datetime.datetime.now()

            # Setting date variable
            date = current.strftime("%x")

            # Setting time variable
            time = current.strftime("%X")

            # Debugging
            print(date + " " + time + " | " + log_msg)

            # Writing to log.txt
            f.write(date + " " + time + " | " + log_msg + "\n")

            # Instant write to log.txt
            f.flush()
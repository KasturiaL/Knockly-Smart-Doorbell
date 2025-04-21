import serial
import datetime
import os
from pathlib import Path

directory = Path(__file__).parent
path = directory / "logger.txt"

usb_port = 'COM9'

arduino = serial.Serial(usb_port, baudrate=9600, timeout=.1)

print("Listening for commands...")

def read():
    # Reading and cleaning data
    data = arduino.readline().decode('utf-8').strip()

    # Returning data if there is data sent
    return data if data else None

with path.open("a") as f:
    while True:
        log_msg = read()
        if log_msg != None:
            current = datetime.datetime.now()

            date = current.strftime("%x")

            time = current.strftime("%X")

            print(date + " " + time + " | " + log_msg)
            f.write(date + " " + time + " | " + log_msg + "\n")
            f.flush()
# Importing Libraries
import serial
import time

# Setting up arduino connection setup
# IMPORTANT: Arduino IDE cannot be open during this process or the system will say the port cannot be accessed
# (no worries, it's just a busy port situation)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) # use the same settings in python_to_arduino.ino

def write_read(data):
    arduino.write(bytes(data, 'utf-8'))

    # Waiting a while for arduino to run
    time.sleep(0.05)

    # Reading data from arduino serial
    data = arduino.readline()
    return data

def read():
    data = arduino.readline().decode('utf-8').strip()
    return data if data else None

def python_input():
    num = input("Enter a number: ") # Taking input from user

    # Sending data to arduino
    value = write_read(num)

    return value

while True:
    value = read()
    if value:  # Only print if value is not None or empty
        print(value)

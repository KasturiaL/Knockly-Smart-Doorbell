# Importing Libraries
import serial
import time

# Setting up arduino connection setup
# IMPORTANT: Arduino IDE cannot be open during this process or the system will say the port cannot be accessed
# (no worries, it's just a busy port situation)
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=.1) # use the same settings in python_to_arduino.ino

def write_read(data):
    arduino.write(bytes(data, 'utf-8'))

    # Waiting a while for arduino to run
    time.sleep(0.05)

    # Reading data from arduino serial
    data = arduino.readline()
    return data


while True:
    num = input("Enter a number: ") # Taking input from user

    # Sending data to arduino
    value = write_read(num)
    
    print(value) # printing the value

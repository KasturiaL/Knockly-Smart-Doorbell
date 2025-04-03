# Importing libraries
import serial
import time

# Setting up Arduino connection
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=.1)

# Setting loop
while True:
    # Getting input from python (by user for now)
    # 1 = Open door
    # 2 = Close door
    num = input("Please pick between 1 and 2: ")

    # Sending input to arduino to process
    arduino.write(bytes(num, 'utf-8'))

    # Giving time for arduino to run its code
    time.sleep(0.05)

    # Logging
    if num == "1":
        print("Door opened.")
    elif num == "2":
        print("Door closed.")
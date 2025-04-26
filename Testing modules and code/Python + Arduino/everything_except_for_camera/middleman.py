# Importing Libraries
import serial
import time
import win32pipe, win32file

pipe_name = r'\\.\pipe\doorpipe'

# Setting up Arduino connection
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=.1)

print("Listening for commands...")

def write_read(data):
    arduino.write(bytes(data, 'utf-8'))

    # Waiting a while for arduino to run
    time.sleep(0.05)

    # Reading data from arduino serial
    data = arduino.readline()
    return data

def read():
    # Reading and cleaning data
    data = arduino.readline().decode('utf-8').strip()

    # Returning data if there is data sent
    return data if data else None

while True:
    pipe = win32pipe.CreateNamedPipe(
        pipe_name,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None
    )

    win32pipe.ConnectNamedPipe(pipe, None)
    print("Pipe connected.")

    # Setting loop
    while True:
        try:
            result, data = win32file.ReadFile(pipe, 64)
            command = data.decode('utf-8').strip()

            # Sending input to arduino to process
            arduino.write(bytes(command, 'utf-8'))

            # Giving time for arduino to run its code
            time.sleep(0.05)

            # Logging
            if command == "1":
                print("Door opened.")
            elif command == "2":
                print("Door closed.")
        except Exception as e:
            print("Error detected: ", e)
            break
    
    win32file.CloseHandle(pipe)
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
from pathlib import Path
import face_rec  # assumes face_rec.py is in the same directory

# ——————————————————————————————————————————————————————
# Configuration
# ——————————————————————————————————————————————————————
my_pc_port   = "COM9"       # adjust as needed
lab_port     = "COM4"
pi_port      = "/dev/ttyACM0"
baud_rate    = 9600
timeout_s    = 0.1

directory    = Path(__file__).parent
log_file     = directory / "log.txt"
command_file = directory / "command.txt"

# ——————————————————————————————————————————————————————
# Setup Arduino serial
# ——————————————————————————————————————————————————————
arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s)
print("Listening for log messages...")

# ——————————————————————————————————————————————————————
# State
# ——————————————————————————————————————————————————————
record_thread = None

# ——————————————————————————————————————————————————————
# Helpers
# ——————————————————————————————————————————————————————
def read():
    """Non-blocking read from Arduino serial. Returns str or None."""
    line = arduino.readline().decode('utf-8', errors='ignore').strip()
    return line if line else None

def check_command():
    """Check for phone commands dropped into command.txt."""
    if command_file.is_file():
        cmd = command_file.read_text().strip()
        command_file.unlink()
        return cmd
    return None

def log(msg):
    """Timestamp + append to log.txt + print."""
    now   = datetime.datetime.now().strftime("%x %X")
    entry = f"{now} | {msg}"
    print(entry)
    with log_file.open("a") as f:
        f.write(entry + "\n")
        f.flush()

def command_check(cmd):
    """Forward phone command to Arduino and log it."""
    arduino.write(cmd.encode())
    time.sleep(0.05)
    if   cmd == "1":
        log("Phone has opened the door.")
    elif cmd == "2":
        log("Phone has closed the door.")
    elif cmd == "3":
        log("Known face detected.")
    elif cmd == "4":
        log("Blocked face detected.")

# ——————————————————————————————————————————————————————
# Main Loop
# ——————————————————————————————————————————————————————
while True:
    # 1) Handle any phone-initiated commands
    cmd = check_command()
    if cmd:
        command_check(cmd)

    # 2) Read any messages from the Arduino
    msg = read()
    if msg:
        log(f"Arduino → {msg}")

        # 3) When Arduino says "Object is a person.", start recording+recognition
        if msg == "Object is a person.":
            # if no thread running or it has finished, start a new one
            if record_thread is None or not record_thread.is_alive():
                log("Triggering 30-second record_and_recognize")
                record_thread = threading.Thread(
                    target=face_rec.record_and_recognize,
                    kwargs={"duration": 30},   # 30s for testing
                    daemon=True
                )
                record_thread.start()
            else:
                log("Recording in progress; trigger ignored.")

    # tiny sleep to avoid busy-loop
    time.sleep(0.01)

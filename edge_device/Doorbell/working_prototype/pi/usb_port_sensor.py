import serial.tools.list_ports
import time

def find_arduino_port():
	ports = serial.tools.list_ports.comports()
	for port in ports:
		if ("Arduino" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device):
			return port.device
			
	return None
	
pi_port = find_arduino_port()
baud_rate = 9600
timeout_s = 0.1

arduino = serial.Serial(pi_port, baudrate=baud_rate, timeout=timeout_s)
def log(msg: str) -> None:
    print(msg)
	
def send_command(cmd: str) -> None:
    """Relay a single‑character command to command.txt *and* the Arduino."""
    try:
        arduino.write(bytes(cmd, 'utf-8'))
    except Exception as e:
        log(f"[ERROR] Sending command {cmd}: {e}")
    time.sleep(0.05)
    if   cmd == "0": log("Middleman startup complete.")
    elif cmd == "1": log("Phone has opened the door.")
    elif cmd == "2": log("Phone has closed the door.")
    elif cmd == "3": log("Known face detected – door opened.")
    elif cmd == "4": log("Blocked face detected – door kept shut.")
    
def read():
    try:
        line = arduino.readline().decode("utf-8", errors="ignore").strip()
        if line:
            log(f"Arduino: {line}")
    except Exception as e:
        log(f"[ERROR] Reading Arduino: {e}")

def setup():
    global arduino

    send_command("0")

    time.sleep(2)
    
    port = find_arduino_port()

    arduino = serial.Serial(port, baudrate=baud_rate, timeout=timeout_s)

    print("Listening for log messages...")
    
def main():
	setup()
	
	while True:
		read()

		time.sleep(0.1)
	
if __name__ == "__main__":
    main()

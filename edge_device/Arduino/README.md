# Arduino

## Setup

To be able to ultilize this code, you will require these equipment:

1. Arduino Base Shield
2. DF Robot Expansion Shield (Arduino Leonardo)
3. USB to Micro-USB
4. LED Button x 2
5. Servo Motor
6. Ultrasonic Ranger
7. Buzzer
8. Short axle

You will need to install Arduino IDE (https://www.arduino.cc/en/software/) to be able to send the code into the Arduino.

You will need to install the module in these ports on the Arduino to run the code without any editing:

1. D2 - Ultrasonic ranger
2. D4 - LED Button
3. D6 - Servo Motor
4. D7 - Buzzer
5. D8 - LED Button

It is best to install the short axle section of the motor aligned parallel to the motor and extended section along the bulk of the motor for the intended outcome

## Usage

While the system is in use, the ranger must be placed sensor down so that the system will not trigger the alarm function (or change the disableAlarm flag to true).

The message outputs will be sent to the Serial Monitor in the Arduino IDE if you want to see them.


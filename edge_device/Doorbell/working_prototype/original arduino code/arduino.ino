// Library imports
#include <Servo.h>
#include <Ultrasonic.h>
#include <Wire.h>

// Pin variables initialization (Add one to port number)
const int manualButtonPin = 1;
const int doorbellButtonPin = 4;

// Port variables initialization
const int motionPort = 2;
Ultrasonic personSensor(3);
const int buzzerPort = 5;
Ultrasonic doorSensor(6);
const int motorPort = 8;

// State variables initialization
bool manualButtonState;
bool doorbellButtonState;
bool motionState;

// Flag variables initialization
bool wasIdleLastLoop = false;
bool disableAlarm = true;
bool objectDetected = false;
bool personDetected = false;

// Time variables initialization
unsigned long objectStart = 0;

// Integer variables initialization
int doorDistance;
int objectDistance;
int overrideCommand;

// Object creation
Servo door;

void setup() {
  // Buttons

  // Button pin modes
  pinMode(manualButtonPin, INPUT);
  pinMode(doorbellButtonPin, INPUT);

  // Motor

  // Attaching motor to port
  door.attach(motorPort);
  // Sets the door at a "closed" position
  door.write(90);

  // PIR motion sensor

  // PIR motion sensor pin mode
  pinMode(motionPort, INPUT);

  // Buzzer

  // Buzzer pin mode
  pinMode(buzzerPort, OUTPUT);
  // No sound on activation
  noTone(buzzerPort);

  // Python <-> Arduino

  // Setting serial baudrate
	Serial.begin(9600); 
	// Setting max serial data wait time 
	Serial.setTimeout(1);
}

void loop() {
  // Reading data from modules

  // Getting state of manual override button  
  manualButtonState = analogRead(manualButtonPin);
  // Getting state of doorbell button 
  doorbellButtonState = analogRead(doorbellButtonPin);
  // Getting distance measured by doorSensor
  doorDistance = doorSensor.read(CM);
  // Getting state of PIR motion sensor
  motionState = digitalRead(motionPort);
  // Getting distance mesured by personSensor
  objectDistance = personSensor.read(CM);

  // Bootleg method to avoid fully covered ranger getting max distance when both transmitter and reciever are covered
  if (doorDistance == 357) { // Max distance
    // Sets as no distance
    doorDistance = 0;
  }

  // Phone command check

  // Detects if there is data in Serial sent by Python code
  if (Serial.available() > 0) { // Data detected
    // Runs function
    override();

    // Changing flag
    wasIdleLastLoop = false;
  }

  // Manual override button check

  // Detects if the manual override button is pressed
  if (manualButtonState == LOW) { // Button pressed
    // Runs function
    open_close();

    // Changing flag
    wasIdleLastLoop = false;
    delay(1000);
  }

  // Doorbell button check

  // Detects if the doorbell button is pressed
  if (doorbellButtonState == LOW) { // Button pressed
    // Runs function
    doorbell();
    
    // Changing flag
    wasIdleLastLoop = false;
  }

  // Door sensor check

  // Detects if door is open and alarm is not disabled
  if (doorDistance >= 6 && disableAlarm == false) { // Open door and alarm not disabled
    // Runs function
    alarm();
    
    // Changing flag
    wasIdleLastLoop = false;
  }

  person_detector(objectDistance, motionState, objectDetected);

  // Idle state

  // Detects if last action was idle()
  if (wasIdleLastLoop == false) { // Last action is not idle()
    // Runs function
    idle();
    
    // Changing flag back to avoid spam
    wasIdleLastLoop = true;
  }
  
}

// Function for opening and closing door after a period of time
void open_close() {
  // Runs function
  open();

  // Waits 5 seconds for user to enter
  delay(5000);

  // Runs function
  close();
}

// Function that sets the system at an idle state
void idle() {
  // Keeps the door closed
  door.write(90);

  // Prints log to Serial
  Serial.println("Door idle."); 
}



// Function that reads commands from python to execute actions
void override() {
  // Translates the serial data as integers
  overrideCommand = Serial.readString().toInt();

  // Checks which command is sent
  if (overrideCommand == 1) { // Open command
    // Runs function
    open();

    // Disables alarm
    disableAlarm = true;
  } else if (overrideCommand == 2){ // Close command
    // Runs function
    close();

    // Enables alarm
    disableAlarm = false;
  }

  // Clears Serial for next command
  Serial.read();
}

// Function that closes the door
void close() {

  // Closes the door
  door.write(90);

  // Prints log to Serial
  Serial.println("Door closed.");
}

// Function that opens the door
void open() {
  // Opens the door
  door.write(0);

  // Prints log to Serial
  Serial.println("Door opened.");
}

// Function that rings the alarm
void alarm(){
  // Prints log to Serial
  Serial.println("Alarm rung.");

  // Alarm segment
  for (int count = 0; count < 10; count++) { // Loops chord 10 times
    // Plays a high note for 0.1 second
    tone(buzzerPort, 100);
    delay(100);

    // Plays no sound for 0.1 second
    noTone(buzzerPort);
    delay(100);
  }
}  

// Function that rings the doorbell
void doorbell() {
  // Prints log to Serial
  Serial.println("Doorbell rung.");
  
  // Doorbell segment
  for (int count = 0; count < 3; count++) { // Loops chord 3 times
    // Plays high note for 0.5 seconds
    tone(buzzerPort, 100);
    delay(500);

    // Plays low note for 0.5 seconds
    tone(buzzerPort, 50);
    delay(500);

    // Plays no note for 0.5 seconds
    noTone(buzzerPort);
    delay(500);
  }

  // Stops buzzer from ringing all the time
  noTone(buzzerPort);
}

// Function that detects if a person is near
void person_detector(int distance, bool motion, bool &objectDetected) {
  if (motion && distance <= 10) { // Check if there is object near
    if (objectDetected == false) { // Only activate if flag is true for less spam
      // Prints log to Serial
      Serial.println("Object detected.");

      // Changes flag
      objectDetected = true;

      // Records time for future comparison
      objectStart = millis();
    }
  }

  if (objectDetected == true && (millis() - objectStart >= 3000)) { // When 3 seconds have passed (> for better checking and objectDetected for less spam)
    if (distance <= 10) { // Object still near ranger
      // Prints log to Serial
      Serial.println("Person.");

      // Reset flags
      objectDetected = false;
    } else { // Object left range of ranger
      // Prints log to Serial
      Serial.println("Object left.");

      // Reset flags
      objectDetected = false;
    }
  }

  // Gives system time so log messages will not be put in the wrong sequence
  delay(500);
}

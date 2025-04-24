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
bool recordLoop = false;

// Time variables initialization
unsigned long objectStart = 0;
unsigned long recordStart = 0;
int recordtime = 300000;

// Integer variables initialization
int doorDistance;
int objectDistance;
int overrideCommand;

// Object creation
Servo door;


// Test variables
int recordtest = 3000;

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

  person_detector(objectDistance, motionState, recordLoop, objectDetected);

  // Idle state

  // Detects if last action was idle()
  if (wasIdleLastLoop == false) { // Last action is not idle()
    // Runs function
    idle();
    
    // Changing flag back to avoid spam
    wasIdleLastLoop = true;
  }

  delay(1);
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

    // Changing flag
    wasIdleLastLoop = false;
  } else if (overrideCommand == 3){ // Known face detected
    // Open and close door
    open_close();

    // Changing flag
    wasIdleLastLoop = false;
  } else if (overrideCommand == 4){ // Blocked face detected
    // Start long alarm
    for (int count = 0; count < 5; count++) {
      alarm();
    }

    // Changing flag
    wasIdleLastLoop = false;
  }

  // Clears Serial for next command
  Serial.read();

  delay(500);
}

// Function that closes the door
void close() {
  // Prints log to Serial
  Serial.println("Door closed.");

  // Closes the door
  door.write(90);
}

// Function that opens the door
void open() {
  // Prints log to Serial
  Serial.println("Door opened.");

  // Opens the door
  door.write(0);
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
void person_detector(int distance, bool motion, bool &recordLoop, bool &objectDetected) {
  // Check if object is near and if is detected before
  if (motion && distance <= 10 && objectDetected == false) { // Object near and is detected before this
    // Prints log to Serial
    Serial.println("Object detected.");

    // Changes objectDetected flag
    objectDetected = true;

    // Records time for future comparison
    objectStart = millis();
  }

  // Check if three second has passed and if object is still near
  if (objectDetected == true && (millis() - objectStart >= 3000)) { // 3 seconds have passed
    if (distance <= 10) { // Object still near ranger
      // Prints log to Serial
      Serial.println("Object is a person.");

      // Reset flag
      objectDetected = false;

      // Check if recording is running
      if (recordLoop == false) { // Recording has not started
        // Prints log to Serial
        Serial.println("Recording started.");

        // Changes recordLoop flag
        recordLoop = true;

        // Records time for future comparison
        recordStart = millis();
      }

    } else { // Object left range of ranger
      // Prints log to Serial
      Serial.println("Object left.");

      // Reset flag
      objectDetected = false;
    }
  }
    
  if (recordLoop == true && millis() - recordStart >= 60000) {
    // Prints log to Serial
    Serial.println("Recording complete.");

    // Reset flag
    recordLoop = false;
  }
  
}

// Adds Servo library to access the functions
#include <Servo.h>

// Setting variables
const int motorPin = 4; // Set port here becuase easier to see
int x;

Servo motor; // Creates a Servo object to run the functions

void setup() {
  // Attaching the motor to a pin
  motor.attach(motorPin);

  // Sets the door at a "closed" position
  motor.write(90);

  // Setting arduino settings
  Serial.begin(9600);
  Serial.setTimeout(1);
}

void loop() {
  // Detects if there is data in Serial
  while(!Serial.available());

  // Translates the serial data as integers
  x = Serial.readString().toInt();

  if (x == 1) { // Open the door
    open();
  } else if (x == 2){ // Close the door
    close();
  }
}

void close() {
    // Closes the door
    motor.write(90);

    // Debugging / Logging
    Serial.println("Door closed.");
}

void open() {
    // Opens the door
    motor.write(0);

    // Debugging / Logging
    Serial.println("Door opended.");
}

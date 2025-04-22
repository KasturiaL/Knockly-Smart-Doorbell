// Adds Servo library to access the functions
#include <Servo.h>

// Assigns the pin to connect to the button (Current = D2)
const int buttonPin = 3; // Add one because it needs the pin, not the port

const int motorPin = 4; // Set port here becuase easier to see

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)
Servo motor; // Creates a Servo object to run the functions

void setup() {
  // Assigning the pin mode for the button (making in as input for the motor)
  pinMode(buttonPin, INPUT);

  // Attaching the motor to a pin
  motor.attach(motorPin);

  // Sets the door at a "open" position
  motor.write(0);
}

void loop() {
  // Reads the state of the button  
  buttonState = digitalRead(buttonPin);

  if (buttonState == LOW) { // Button pressed
    door();
  } else {
    motor.write(0);
  }
}

void door() {
    // Closes the door
    motor.write(90);

    // Debugging / Logging
    Serial.println("Door opened.");
}
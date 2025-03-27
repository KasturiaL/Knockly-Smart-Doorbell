// Adds Servo library to access the functions
#include <Servo.h>

// Assigns the pin to connect to the button (Current = D")
const int buttonPin = 3; // Add one because it needs the pin, not the port

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)
Servo myServo; // Creates a Servo object to run the functions

void setup() {
  // Assigning hte pin mode for the button (making in as input for the motor)
  pinMode(buttonPin, INPUT);

  // Attaching the motor to a pin
  myServo.attach(4);

  // Logging purposes
  while (!Serial) { };
    Serial.begin(9600);

  // Sets the door at a "closed" position
  myServo.write(90);
}

void loop() {
  // Reads the state of the button  
  buttonState = digitalRead(buttonPin);

  // Debugging
  Serial.println(buttonState);

  if (buttonState == LOW) { // Button pressed
    // Opens the door
    myServo.write(0);

    // Debugging
    Serial.println("Door opened.");

    // Waits 5 seconds for user to enter
    delay(5000);

    // Closes the door
    myServo.write(90);

    // Debugging
    Serial.println("Door closed.");
  }

  // Keeps the door closed (maybe a basic way to "lock" the door)
  myServo.write(90);
}

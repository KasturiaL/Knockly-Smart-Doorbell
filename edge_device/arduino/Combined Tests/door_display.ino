// Adds libraries to access the functions
#include <Servo.h>
#include <rgb_lcd.h>

// Assigns the pin to connect to the button (Current = D2)
const int buttonPin = 3; // Add one because it needs the pin, not the port

const int motorPin = 4; // Set port here becuase easier to see

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)
bool wasIdleLastLoop = false; // Tracks if idle() was called last loop

Servo motor; // Creates a Servo object to run the functions
rgb_lcd lcd; // Creates a lcd object to run the display

// Setting up display colour
const int colorR = 0;
const int colorG = 255;
const int colorB = 0;

void setup() {
  // Assigning hte pin mode for the button (making in as input for the motor)
  pinMode(buttonPin, INPUT);

  // Attaching the motor to a pin
  motor.attach(motorPin);

  // Sets the door at a "closed" position
  motor.write(90);

  // Sets up the LCD's number of columns and rows:
  lcd.begin(16, 2);
    
  // Sets up the LCD's colour:
  lcd.setRGB(colorR, colorG, colorB);

  // Print a message to the LCD.
  lcd.print("Hello!");
}

void loop() {
  // Reads the state of the button  
  buttonState = digitalRead(buttonPin);

  if (buttonState == LOW) { // Button pressed
    door();
    wasIdleLastLoop = false;
    delay(1000);
  }

  if (wasIdleLastLoop == false) { // Last action is not idle()
    // Run idle function
    idle();
    
    // Change flag to avoid constant trigger
    wasIdleLastLoop = true;
  }
  
}

void door() {
  // Opens the door
    motor.write(0);

    // Displays message to lcd
    displaymsg("Door opened.");

    // Waits 5 seconds for user to enter
    delay(5000);

    // Closes the door
    motor.write(90);

    // Displays message to lcd
    displaymsg("Door closed.");
}

void idle() {
  // Keeps the door closed (maybe a basic way to "lock" the door)
  motor.write(90);

  // Displays message to lcd
  displaymsg("Hello!");
}

void displaymsg(String msg) {
  // Clears previous message
  lcd.clear();

  // set the cursor to column 0, line 0
  lcd.setCursor(0, 0);

  // Displays message to lcd
  lcd.print(msg);
}

// Potential improvements
// 1. Better idle handling if possible (current is fine, but can be improved if time allows)
// TO DO
// 1. Logging method dependent per 5-10 seconds to be less annoying for log checking(can be done on python through raspberry pi if needing more space for arduino code)
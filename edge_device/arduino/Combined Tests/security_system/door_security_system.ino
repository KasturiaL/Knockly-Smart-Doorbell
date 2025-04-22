// Adding libraries
#include <Servo.h>
#include <rgb_lcd.h>
#include <Ultrasonic.h>

// Ranger initialization
Ultrasonic ultrasonic(3);

// Distance variable initialization
int distance;

// Assigns the pin to connect to the button (Current = D2)
const int buttonPin = 3; // Add one because it needs the pin, not the port

// Buzzer pin
const int buzzerPin = 4;

// Motor pin
const int motorPin = 5;

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)
bool wasIdleLastLoop = false; // Tracks if idle() was called last loop
bool intruderDetected = false; // Tracks if an intruder was detected

Servo motor; // Creates a Servo object to run the functions
rgb_lcd lcd; // Creates a lcd object to run the display

// Setting up display colour
const int colorR = 0;
const int colorG = 255;
const int colorB = 0;

// Color for alarm (red)
const int alarmColorR = 255;
const int alarmColorG = 0;
const int alarmColorB = 0;

void setup() {
  
  // Assigning the pin mode for the button
  pinMode(buttonPin, INPUT);
  
  // Buzzer initialization
  pinMode(buzzerPin, OUTPUT);
  
  // Sets the buzzer to make no sound on activation
  noTone(buzzerPin);

  // Attaching the motor to a pin
  motor.attach(motorPin);

  // Sets the door at a "closed" position
  motor.write(90);

  // Sets up the LCD's number of columns and rows:
  lcd.begin(16, 2);
    
  // Sets up the LCD's colour:
  lcd.setRGB(colorR, colorG, colorB);

  // Print a message to the LCD.
  lcd.print("Door Security");
  lcd.setCursor(0, 1);
  lcd.print("System Active");
  
  // Initialize Serial
  Serial.begin(9600);
  
  delay(2000);
  lcd.clear();
  lcd.print("Hello!");
}

void loop() {
  // Read ultrasonic sensor
  distance = ultrasonic.read(CM);
  
  // Bootleg method to avoid fully covered ranger getting max distance
  if (distance == 357) {
    distance = 0;
  }
  
  // Debugging
  Serial.print("Distance in CM: ");
  Serial.println(distance);
  
  // Reads the state of the button  
  buttonState = digitalRead(buttonPin);

  // Check for intruder (if distance is 6cm or more)
  if (distance >= 6) {
    intruderAlert();
    wasIdleLastLoop = false;
  } 
  else if (buttonState == LOW) { // Button pressed
    door();
    wasIdleLastLoop = false;
    delay(1000);
  }
  else if (wasIdleLastLoop == false) { // Last action is not idle()
    // Run idle function
    idle();
    
    // Change flag to avoid constant trigger
    wasIdleLastLoop = true;
  }
  
  delay(500); // Short delay for stability
}

void door() {
  // Opens the door
  motor.write(0);

  // Displays message to lcd
  displaymsg("Door opened.", colorG);

  // Waits 5 seconds for user to enter
  delay(5000);

  // Closes the door
  motor.write(90);

  // Displays message to lcd
  displaymsg("Door closed.", colorG);
}

void idle() {
  // Keeps the door closed (maybe a basic way to "lock" the door)
  motor.write(90);

  // Displays message to lcd with normal color
  displaymsg("Hello!", colorG);
  
  // Make sure buzzer is off
  noTone(buzzerPin);
}

void intruderAlert() {
  // Make sure door is closed
  motor.write(90);
  
  // Display intruder alert message with alarm color
  displaymsg("INTRUDER ALERT!", alarmColorR);
  
  // Sound the alarm
  for (int count = 0; count < 5; count++) {
    tone(buzzerPin, 100); // Higher tone
    delay(200);
    tone(buzzerPin, 50);  // Lower tone
    delay(200);
  }
  
  // Log the intrusion
  Serial.println("Intruder detected!");
}

void displaymsg(String msg, int color) {
  // Clears previous message
  lcd.clear();
  
  // Set color based on message type (green for normal, red for alert)
  if (color == colorG) {
    lcd.setRGB(colorR, colorG, colorB); // Normal green
  } else {
    lcd.setRGB(alarmColorR, alarmColorG, alarmColorB); // Alarm red
  }

  // set the cursor to column 0, line 0
  lcd.setCursor(0, 0);

  // Displays message to lcd
  lcd.print(msg);
}
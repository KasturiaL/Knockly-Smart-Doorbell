// Importing lcd library
#include <rgb_lcd.h>

// Setting up lcd object
rgb_lcd lcd;

// Setting up lcd colour
const int colorR = 0;
const int colorG = 255;
const int colorB = 0;

// Variable initialization
int x = 0; 

// Assigns the pin to connect to the button (Current = D2)
const int buttonPin = 3; // Add one because it needs the pin, not the port

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)

void setup() { 
	// Assigning the pin mode for the button (making in as input for the motor)
  pinMode(buttonPin, INPUT);

	// set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
    
	// Setting up lcd colour
  lcd.setRGB(colorR, colorG, colorB);

	// Setting serial baudrate
	Serial.begin(9600); 
	// Setting max serial data wait time 
	Serial.setTimeout(1); 
} 

void loop() {
    buttonState = digitalRead(buttonPin); // Read button state

    if (buttonState == LOW) { // If button is pressed
      x++; // Increment variable

      // Clearing old data
      lcd.clear();

      // Set cursor to first column, first row
      lcd.setCursor(0, 0); 

      // Display counter on LCD
      lcd.print(x);        

      // Send data to serial (to be read by python)
      Serial.println(x); 
    }
}

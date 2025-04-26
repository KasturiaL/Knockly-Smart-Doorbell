// Importing lcd library
#include <rgb_lcd.h>

// Setting up lcd object
rgb_lcd lcd;

// Setting up lcd colour
const int colorR = 0;
const int colorG = 255;
const int colorB = 0;

// Variable initialization
int x; 

void setup() { 
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
	while (!Serial.available());
	// set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
	lcd.setCursor(0, 0);

	// Reads string as a integer
	x = Serial.readString().toInt(); 
			
	// Prints integer data on lcd screen
	lcd.print(x); 

	// prints data to serial, which gets sent to 
	Serial.print(x);
} 

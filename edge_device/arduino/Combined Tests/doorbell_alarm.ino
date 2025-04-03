// Adding library
#include <Ultrasonic.h>

// Ranger initialization
Ultrasonic ultrasonic(3);

// Distance variable initialization
int distance;

// Assigns the pin to connect to the button (Current = D5)
const int buttonPin = 6; // Add one because it needs the pin, not the port

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)

void setup(){
  // Button pin initialization
  pinMode(buttonPin, INPUT);

  // Buzzer initialization
  pinMode(4, OUTPUT);

  // Sets the buzzer to make no sound on activation
  noTone(4);
}

void loop(){
  // Pass CM as a parameter to get the distance in centimetres
  distance = ultrasonic.read(CM);

  // Reads the state of the button  
  buttonState = digitalRead(buttonPin);

  // Bootleg method to avoid fully covered ranger getting max distance
  if (distance == 357) {
    distance = 0;
  }

  // If button pressed
  if (buttonState == LOW) {
    delay(50); 
    // Logging
    Serial.println("Doorbell rung.");
    
    // Repeat 10 times
    for (int count = 0; count < 3; count++) {
      tone(4, 100);
      delay(500);
      tone(4, 50);
      delay(500);
      noTone(4);
      delay(500);
    }

    // Stops buzzer from ringing all the time
    noTone(4);
  } else {
    noTone(4);
  }
  
  // Debugging
  Serial.print("Distance in CM: ");
  Serial.println(distance);
  delay(1000);

  // if ranger senses distance equal or over 6 centimetres
  if (distance >= 6) {
    // Repeat 10 times
    for (int count = 0; count < 10; count++) {
      tone(4, 100); // Send 1KHz sound signal...
      delay(100);         // ...for 1 sec
      noTone(4);     // Stop sound...
      delay(100);         // ...for 1sec
    }
  }
}

// TO DO
// 1. Issue of doorbell not ringing because the loop is too fast and is going over the ranger for longer periods of time
// 2. (potential issue) Arduino file size is concerning
// 3. Change all the individual modules into functions in arduino code so that loop and setup functions can be cleaner.
// 4. Button somehow lights up with the buzzer when alarm conditions are met
// Assigns the pin to connect to the button (Current = D")
const int buttonPin = 3; // Add one because it needs the pin, not the port

int buttonState; // Initializes a values for the state of the button (HIGH = not pressed, LOW = pressed)

int loopcount = 0;

void setup(){
  // Button pin initialization
  pinMode(buttonPin, INPUT);

  // Buzzer initialization
  pinMode(4, OUTPUT);

  noTone(4);
}

void loop(){
  // Reads the state of the button  
  buttonState = digitalRead(buttonPin);

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
    // checking loopcount for less serial clogging
    if (loopcount == 10000) {
      // Logging
      Serial.println("Doorbell idle.");

      loopcount = 0;
    }
  }

  loopcount = loopcount + 1;
}

// TO DO
// 1. Figure out how the components connect in pins or ports
// 2. Add more readability to the variables and stuff (for future ease)
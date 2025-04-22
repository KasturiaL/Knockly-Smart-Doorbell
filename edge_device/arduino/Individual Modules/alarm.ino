// Adding library
#include <Ultrasonic.h>

// Ranger initialization
Ultrasonic ultrasonic(3);

// Distance variable initialization
int distance;


void setup(){
  // Buzzer initialization
  pinMode(4, OUTPUT);

  // Sets the buzzer to make no sound on activation
  noTone(4);
}

void loop(){
  // Pass CM as a parameter to get the distance in centimetres
  distance = ultrasonic.read(CM);

  // Bootleg method to avoid fully covered ranger getting max distance
  if (distance == 357) {
    distance = 0;
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

// TO DO (optional)
// 1. Find out how to refine distance sensing properties for better door closed detection
// 2. Find out how to better handle max distance issue
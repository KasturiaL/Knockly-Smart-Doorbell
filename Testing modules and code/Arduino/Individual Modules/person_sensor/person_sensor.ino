#include <Ultrasonic.h>

const int motionPin = 2;
int counter;
int distance;
int motion;

Ultrasonic ultrasonic(3);

void setup() {
  pinMode(motionPin, INPUT);

  Serial.begin(9600);
}

void loop() {
  motion = digitalRead(motionPin);

  if (motion == HIGH) {
    for (int loop = 0;loop < 5; loop++) {
      distance = ultrasonic.read(CM);

      if (distance <= 40) {
        counter++;
        delay(1000);
      } else {
        counter = 0;
        break;
      }
    }

    if (counter == 5) {
      Serial.println("Object detected.");
      counter = 0;
    } else {
      Serial.println("Unknown object moved away");
    }
  } else {
    Serial.println("Nothing detected.");
  }

  delay(1000);
}

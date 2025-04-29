#include <avr/wdt.h>

const int manualButtonPin = 1;

bool manualButtonState;

void setup() {
  pinMode(manualButtonPin, INPUT);

  Serial.begin(9600);
}

void loop() {
  manualButtonState = analogRead(manualButtonPin);

  if (manualButtonState == LOW) {
    reset();
  }
}

void reset() {
  Serial.println("Rebooting in 2 seconds...");

  delay(1000);
  wdt_enable(WDTO_1S);  // Reset after 1 second
  while (1);            // Lock CPU so it resets
}

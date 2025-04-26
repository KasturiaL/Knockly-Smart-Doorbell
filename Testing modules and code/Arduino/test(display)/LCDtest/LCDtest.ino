#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x30, 16, 2);

void setup() {
  lcd.begin(16,2);
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("Hello!");
}

void loop() {
  // put your main code here, to run repeatedly:

}

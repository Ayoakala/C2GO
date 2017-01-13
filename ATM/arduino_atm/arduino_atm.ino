#include <LiquidCrystal.h>
#include <Servo.h>

Servo myservo;

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600);
  myservo.attach(9);
  lcd.begin(32, 2);
  lcd.print("Scan QR.");
}
 
void loop() {
  if (Serial.available()) {
    delay(100); //wait some time for the data to fully be read
    myservo.write(140);
    delay(300);
    myservo.write(90);
    lcd.clear();
    while (Serial.available() > 0) {
      char c = Serial.read();
      lcd.write(c);
    }
    
  }
}
  




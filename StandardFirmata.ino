#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Define components
Servo trapdoor;
LiquidCrystal_I2C lcd(0x3F, 16, 2); // Change 0x27 to 0x3F if your screen is blank

const int SERVO_PIN = 9;

void setup() {
  // Start Serial communication at 9600 baud
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Bin Ready");
  lcd.setCursor(0, 1);
  lcd.print("Waiting for AI...");
  
  // Attach Servo
  trapdoor.attach(SERVO_PIN);
  trapdoor.write(90); // Start in middle position
}

void loop() {
  // Check if Python sent a command
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Clear buffer to prevent "bouncing" signals
    while(Serial.available() > 0) { Serial.read(); } 

    // Handle the decision
    if (command == 'p') {
      lcd.clear();
      lcd.print("Detected: PLASTIC");
      lcd.setCursor(0, 1);
      lcd.print("Routing: YES");
      trapdoor.write(45); // Move to Plastic bin
      delay(2500);        // Hold open for 2.5 seconds
      trapdoor.write(90); // Reset
      lcd.clear();
      lcd.print("Smart Bin Ready");
    } 
    else if (command == 'n') {
      lcd.clear();
      lcd.print("Detected: REJECT");
      lcd.setCursor(0, 1);
      lcd.print("Routing: NO");
      trapdoor.write(135); // Move to Reject bin
      delay(2500);         // Hold open for 2.5 seconds
      trapdoor.write(90);  // Reset
      lcd.clear();
      lcd.print("Smart Bin Ready");
    }
  }
}
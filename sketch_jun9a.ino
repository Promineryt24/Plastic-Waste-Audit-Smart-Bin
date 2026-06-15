#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize components
// Note: If screen is blank, try address 0x3F instead of 0x27
LiquidCrystal_I2C lcd(0x27, 16, 2); 
Servo trapdoor;

const int SERVO_PIN = 9;

void setup() {
  // Start Serial at 9600 for communication with Python
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Bin Ready");
  lcd.setCursor(0, 1);
  lcd.print("Waiting for AI...");
  
  // Initialize Servo
  trapdoor.attach(SERVO_PIN);
  trapdoor.write(90); // Default middle position
}

void loop() {
  // Listen for commands from Python
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Clear the buffer to prevent repetitive triggers
    while(Serial.available() > 0) { Serial.read(); }

    if (command == 'p') {
      // PLASTIC PATH
      lcd.clear();
      lcd.print("Detected: PLASTIC");
      lcd.setCursor(0, 1);
      lcd.print("Routing to YES");
      
      trapdoor.write(45); // Move to Plastic Bin
      delay(2500);        // Wait for item to fall
      trapdoor.write(90); // Reset
      
      lcd.clear();
      lcd.print("Smart Bin Ready");
      lcd.setCursor(0, 1);
      lcd.print("Waiting for AI...");
    } 
    else if (command == 'n') {
      // REJECT PATH
      lcd.clear();
      lcd.print("Detected: REJECT");
      lcd.setCursor(0, 1);
      lcd.print("Routing to NO");
      
      trapdoor.write(135); // Move to Reject Bin
      delay(2500);         // Wait for item to fall
      trapdoor.write(90);  // Reset
      
      lcd.clear();
      lcd.print("Smart Bin Ready");
      lcd.setCursor(0, 1);
      lcd.print("Waiting for AI...");
    }
  }
}
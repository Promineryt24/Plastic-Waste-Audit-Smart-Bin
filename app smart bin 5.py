import cv2
import time
import random
import csv
import requests
import serial
from datetime import datetime

# ==========================================
# 1. SETUP: BLYNK & ARDUINO
# ==========================================
# REPLACE with your actual Blynk Auth Token from your Device Info
BLYNK_AUTH_TOKEN = 'edovbjnsWowWsU6EL-Pdwi9RN021Q7Qy' 
PORT = 'COM4' # <-- IMPORTANT: Ensure this matches your Arduino port in Device Manager

print(f"🔌 Connecting to Arduino on port {PORT}...")
try:
    # We use Serial instead of pyfirmata for better stability with Servo/LCD
    arduino = serial.Serial(PORT, 9600, timeout=1)
    time.sleep(2) # Give Arduino time to reboot after connecting
    print("✅ Arduino Connected!")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    print("Make sure the Arduino IDE is CLOSED before running this.")
    exit()

# ==========================================
# 2. DATA HANDLING (CSV & Blynk)
# ==========================================
def get_mock_weight():
    """Generates a random weight between 10g and 60g for simulation."""
    return round(random.uniform(10.0, 60.0), 1)

def save_data_locally(item_type, weight, status):
    """Saves the audit data to a local CSV file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('app_smart_bin_audit.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([now, item_type, f"{weight}g", status])
    print(f"💾 Saved to CSV: {item_type} | {weight}g")

def send_data_to_blynk(item_type, weight):
    """Pushes data to Blynk Virtual Pins V1 (Weight) and V2 (Material)."""
    print("☁️ Pushing to Blynk Cloud...")
    try:
        url_weight = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH_TOKEN}&V1={weight}"
        url_material = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH_TOKEN}&V2={item_type}"
        
        requests.get(url_weight, timeout=5)
        requests.get(url_material, timeout=5)
        print("✅ [Blynk SUCCESS] Dashboard Updated!")
    except Exception as e:
        print(f"❌ [Blynk ERROR] Network failed: {e}")

def display_status(item_type, weight):
    print("\n" + "="*40)
    if item_type == "Plastic":
        print(f"✅ SUCCESS: {weight}g of Recyclable Plastic Sorted!")
    else:
        print(f"❌ REJECTED: {weight}g of Non-Viable Waste.")
    print("="*40 + "\n")

# ==========================================
# 3. MAIN AI & LOGIC LOOP
# ==========================================
def main():
    cap = cv2.VideoCapture(0) # Open webcam
    
    print("\n🎥 Smart Bin Vision System Active.")
    print("Commands: Press 'p' for Plastic, 'n' for Reject, 'q' to Quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
            
        cv2.putText(frame, "App Smart Bin - Active", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Waiting for Input...", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
        cv2.imshow('Smart Bin Camera Feed', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Shutting down...")
            break
            
        # --- PLASTIC LOGIC ---
        elif key == ord('p'):
            print("\n[AI DETECTED]: Rigid Plastic")
            weight = get_mock_weight()
            
            # 1. Trigger Arduino (Moves Servo + Updates LCD)
            arduino.write(b'p') 
            
            # 2. Audit Data & Sync to Cloud
            save_data_locally("Plastic", weight, "ACCEPTED")
            send_data_to_blynk("Plastic", weight)
            display_status("Plastic", weight)
            
            time.sleep(2.5) # Wait for mechanical movement
            
        # --- REJECT LOGIC ---
        elif key == ord('n'):
            print("\n[AI DETECTED]: Reject Material")
            weight = get_mock_weight()
            
            # 1. Trigger Arduino
            arduino.write(b'n')
            
            # 2. Audit Data & Sync to Cloud
            save_data_locally("Reject", weight, "REJECTED")
            send_data_to_blynk("Reject", weight)
            display_status("Reject", weight)
            
            time.sleep(2.5)

    cap.release()
    cv2.destroyAllWindows()
    arduino.close()

if __name__ == '__main__':
    main()

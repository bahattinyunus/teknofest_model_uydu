import sys
import time
from telemetry import TelemetryHandler

def main():
    print("==========================================")
    print("   TEKNOFEST MODEL UYDU YER İSTASYONU     ")
    print("        SİSTEM BAŞLATILIYOR...            ")
    print("==========================================")
    
    # Initialize components
    try:
        telemetry = TelemetryHandler()
        print("[INFO] Telemetry Module: ONLINE")
        
        print("[INFO] Establishing Serial Connection... (SIMULATION MODE)")
        time.sleep(1)
        print("[SUCCESS] Link Established.")
        
        print("\n[READY] Listening for data packets...")
        # Placeholder for main loop
        while True:
            # Simulate receiving data
            packet = telemetry.read_packet_simulation()
            print(f"[RX] {packet}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[INFO] System Shutdown Initiated.")
        sys.exit(0)

if __name__ == "__main__":
    main()

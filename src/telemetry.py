import random
import time
import os
import csv
from logger import logger
from security import DataIntegrity

class TelemetryHandler:
    def __init__(self, port="COM3", baudrate=9600, log_to_csv=True):
        self.port = port
        self.baudrate = baudrate
        self.connection_status = False
        self.log_to_csv = log_to_csv
        self.csv_file = "logs/telemetry.csv"

        if self.log_to_csv:
            self._init_csv()

    def _init_csv(self):
        """Initializes the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["team_id", "timestamp", "pressure", "altitude", "speed", "battery", "checksum"])
            logger.info(f"Telemetry CSV initialized: {self.csv_file}")

    def connect(self):
        """
        Establishes connection to the serial port.
        """
        # Placeholder for pyserial connection logic
        self.connection_status = True
        return True

    def read_packet_simulation(self):
        """
        Generates a dummy telemetry packet for testing.
        Format: <TEAM_ID>,<TIMESTAMP>,<PRESSURE>,<ALITITUDE>,<SPEED>,<BATTERY_LEVEL>,<CHECKSUM>
        """
        team_id = 12345
        timestamp = time.strftime("%H:%M:%S")
        pressure = round(random.uniform(980.0, 1020.0), 2)
        altitude = round(random.uniform(0.0, 500.0), 2)
        speed = round(random.uniform(0.0, 15.0), 2)
        battery = round(random.uniform(10.0, 12.6), 1)
        
        raw_data = f"{team_id},{timestamp},{pressure},{altitude},{speed},{battery}"
        checksum = DataIntegrity.calculate_crc32(raw_data)
        
        return f"{raw_data},{checksum}"

    def parse_packet(self, packet_str):
        """
        Parses a raw CSV packet string into a dictionary and validates integrity.
        """
        try:
            data = packet_str.split(',')
            if len(data) < 7:
                raise ValueError("Incomplete packet received.")

            raw_data = ",".join(data[:6])
            received_checksum = data[6]

            if not DataIntegrity.verify_crc32(raw_data, received_checksum):
                logger.error(f"Checksum mismatch! Received: {received_checksum}")
                return {"error": "Checksum mismatch"}

            parsed_data = {
                "team_id": int(data[0]),
                "timestamp": data[1],
                "pressure": float(data[2]),
                "altitude": float(data[3]),
                "speed": float(data[4]),
                "battery": float(data[5]),
                "checksum": received_checksum
            }

            if self.log_to_csv:
                self._log_to_csv(parsed_data)

            return parsed_data
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            return {"error": str(e)}

    def _log_to_csv(self, data):
        """Appends a packet to the CSV log file."""
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data["team_id"], data["timestamp"], data["pressure"],
                    data["altitude"], data["speed"], data["battery"],
                    data["checksum"]
                ])
        except Exception as e:
            logger.error(f"Failed to log to CSV: {e}")

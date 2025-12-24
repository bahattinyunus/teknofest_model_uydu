import random
import time

class TelemetryHandler:
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection_status = False

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
        Format: <TEAM_ID>,<TIMESTAMP>,<PRESSURE>,<ALITITUDE>,<SPEED>,<BATTERY_LEVEL>
        """
        team_id = 12345
        timestamp = time.strftime("%H:%M:%S")
        pressure = round(random.uniform(980.0, 1020.0), 2)
        altitude = round(random.uniform(0.0, 500.0), 2)
        speed = round(random.uniform(0.0, 15.0), 2)
        battery = round(random.uniform(10.0, 12.6), 1)
        
        return f"{team_id},{timestamp},{pressure},{altitude},{speed},{battery}"

    def parse_packet(self, packet_str):
        """
        Parses a raw CSV packet string into a dictionary.
        """
        try:
            data = packet_str.split(',')
            return {
                "team_id": int(data[0]),
                "timestamp": data[1],
                "pressure": float(data[2]),
                "altitude": float(data[3]),
                "speed": float(data[4]),
                "battery": float(data[5])
            }
        except Exception as e:
            return {"error": str(e)}

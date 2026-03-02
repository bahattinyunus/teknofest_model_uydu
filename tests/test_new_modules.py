import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logger import SatelliteLogger
from security import DataIntegrity
from resilience import SystemHealthMonitor
from telemetry import TelemetryHandler

def test_logger_creation():
    log_file = "logs/test_satellite.log"
    logger = SatelliteLogger(name="TestLogger", log_file=log_file)
    logger.info("Test message")
    assert os.path.exists(log_file)

def test_security_crc32():
    data = "test_data"
    checksum = DataIntegrity.calculate_crc32(data)
    assert DataIntegrity.verify_crc32(data, checksum)
    assert not DataIntegrity.verify_crc32(data, "wrong_checksum")

def test_security_encryption():
    cmd = "ACTIVATE_PAYLOAD"
    encrypted = DataIntegrity.encrypt_command(cmd)
    assert encrypted != cmd
    assert DataIntegrity.decrypt_command(encrypted) == cmd

def test_health_monitor():
    health = SystemHealthMonitor()
    report = health.check_health()
    assert "cpu_usage" in report
    assert "memory_usage" in report
    assert report["status"] in ["HEALTHY", "WARNING"]

def test_telemetry_csv_logging():
    csv_path = "logs/test_telemetry.csv"
    if os.path.exists(csv_path):
        os.remove(csv_path)
    
    handler = TelemetryHandler(log_to_csv=True)
    handler.csv_file = csv_path
    handler._init_csv()
    
    packet = handler.read_packet_simulation()
    parsed = handler.parse_packet(packet)
    
    assert os.path.exists(csv_path)
    with open(csv_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2 # Header + 1 Data

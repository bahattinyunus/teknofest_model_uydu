import pytest
import os
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzer import TelemetryAnalyzer
from commands import SatelliteCommandProcessor

def test_analyzer_statistics():
    csv_path = "logs/test_analysis.csv"
    data = {
        "team_id": [12345, 12345],
        "timestamp": ["12:00:00", "12:00:01"],
        "pressure": [1013.25, 1013.20],
        "altitude": [100.0, 110.0],
        "speed": [5.0, 10.0],
        "battery": [12.0, 11.9],
        "checksum": ["abc", "def"]
    }
    os.makedirs("logs", exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    
    analyzer = TelemetryAnalyzer(csv_path=csv_path)
    stats = analyzer.analyze()
    
    assert int(stats["total_packets"]) == 2
    assert float(stats["max_altitude"]) == 110.0
    assert float(stats["max_speed"]) == 10.0
    assert float(stats["min_battery"]) == 11.9
    
    analyzer.generate_report("logs/test_report.md")
    assert os.path.exists("logs/test_report.md")
    
    # Cleanup
    if os.path.exists(csv_path): os.remove(csv_path)
    if os.path.exists("logs/test_report.md"): os.remove("logs/test_report.md")

def test_command_matching():
    processor = SatelliteCommandProcessor()
    
    # Exact match
    assert processor.process_natural_language("ayrılmayı başlat") == "TRIGGER_SEPARATION"
    
    # Case insensitive
    assert processor.process_natural_language("SISTEMI KAPAT") == "SHUTDOWN_SYSTEM"
    
    # Unknown command
    assert processor.process_natural_language("kahve yap") is None

def test_secure_command():
    processor = SatelliteCommandProcessor(secret_key="MY_KEY")
    
    # Valid auth
    assert processor.secure_execute("ayrılma", "MY_KEY") is True
    
    # Invalid auth
    assert processor.secure_execute("ayrılma", "WRONG_KEY") is False

if __name__ == "__main__":
    try:
        print("Running test_analyzer_statistics...")
        test_analyzer_statistics()
        print("Running test_command_matching...")
        test_command_matching()
        print("Running test_secure_command...")
        test_secure_command()
        print("All v1.4.0 manual tests passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

import pandas as pd
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from logger import logger

class TelemetryAnalyzer:
    """
    Analyzes telemetry data from CSV logs to generate mission summaries.
    """
    def __init__(self, csv_path="logs/telemetry.csv"):
        self.csv_path = csv_path

    def analyze(self) -> dict:
        """Processes the CSV file and returns a statistics dictionary."""
        if not os.path.exists(self.csv_path):
            logger.error(f"Analysis failed: {self.csv_path} not found.")
            return {}

        try:
            df = pd.read_csv(self.csv_path)
            if df.empty:
                return {}

            stats = {
                "total_packets": len(df),
                "max_altitude": df["altitude"].max() if "altitude" in df.columns else 0.0,
                "avg_speed": df["speed"].mean() if "speed" in df.columns else 0.0,
                "max_speed": df["speed"].max() if "speed" in df.columns else 0.0,
                "min_battery": df["battery"].min() if "battery" in df.columns else 0.0,
            }
            return stats
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {}

    def generate_report(self, output_path="logs/mission_report.md"):
        """Generates a Markdown report of the mission."""
        stats = self.analyze()
        if not stats:
            return

        report = f"""# 🚀 Görev Analiz Raporu

## 📊 Genel İstatistikler
- **Toplam Paket Sayısı:** {stats['total_packets']}
- **Maksimum İrtifa:** {stats['max_altitude']:.2f} m
- **Ortalama Hız:** {stats['avg_speed']:.2f} m/s
- **Maksimum Hız:** {stats['max_speed']:.2f} m/s
- **Minimum Pil Seviyesi:** {stats['min_battery']:.2f} V
"""
        if stats.get("avg_pressure"):
            report += f"- **Ortalama Basınç:** {stats['avg_pressure']:.2f} hPa\n"

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Mission report generated: {output_path}")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")

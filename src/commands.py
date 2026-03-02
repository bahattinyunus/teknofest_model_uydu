import difflib
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from logger import logger
from security import DataIntegrity

class SatelliteCommandProcessor:
    """
    Processes natural language and coded commands for the satellite.
    Supports basic NLP matching and security verification.
    """
    
    COMMAND_MAP = {
        "TRIGGER_SEPARATION": ["ayrılmayı başlat", "ayrılma", "payload release", "separate"],
        "SHUTDOWN_SYSTEM": ["sistemi kapat", "kapat", "shutdown", "power off"],
        "GET_STATUS": ["durum raporu", "statü", "status", "report"],
        "REBOOT_MCU": ["yeniden başlat", "reset", "reboot"],
    }

    def __init__(self, secret_key="TEKNOFEST_2025"):
        self.secret_key = secret_key

    def process_natural_language(self, text: str) -> str | None:
        """Matches input text to a known command using string similarity."""
        text = text.lower().strip()
        
        best_match = None
        highest_ratio = 0.0
        
        for cmd, aliases in self.COMMAND_MAP.items():
            for alias in aliases:
                ratio = difflib.SequenceMatcher(None, text, alias).ratio()
                if ratio > highest_ratio and ratio > 0.6:  # Lowered threshold for v1.4.0
                    highest_ratio = ratio
                    best_match = cmd
        
        if best_match:
            logger.info(f"Command identified: {best_match} (Match confidence: {highest_ratio:.2f})")
        return best_match

    def secure_execute(self, command_text: str, auth_code: str) -> bool:
        """Executes a command only if the auth_code is valid."""
        # Simple auth: check if auth_code is the MD5/SHA256 of the secret_key (placeholder)
        # For simplicity, we just check if it matches the key for now
        if auth_code == self.secret_key:
            cmd = self.process_natural_language(command_text)
            if cmd:
                logger.info(f"Executing SECURE command: {cmd}")
                return True
        else:
            logger.warning("Unauthorized command attempt detected!")
        return False

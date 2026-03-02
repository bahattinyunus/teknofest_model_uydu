import logging
import os
from logging.handlers import RotatingFileHandler

class SatelliteLogger:
    """
    Professional logging system for the TEKNOFEST Model Satellite.
    Supports console coloring and rotating file logs.
    """
    
    # ANSI Color Codes
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, name="Satellite", log_file="logs/satellite.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers if re-initialized
        if not self.logger.handlers:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            # File Handler (Rotating)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
            )
            file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)

            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)

    def _format_msg(self, msg, color=""):
        return f"{color}{msg}{self.RESET}" if color else msg

    def info(self, msg):
        self.logger.info(self._format_msg(msg, self.GREEN))

    def debug(self, msg):
        self.logger.debug(self._format_msg(msg, self.BLUE))

    def warning(self, msg):
        self.logger.warning(self._format_msg(msg, self.YELLOW))

    def error(self, msg):
        self.logger.error(self._format_msg(msg, self.BOLD + self.RED))

    def critical(self, msg):
        self.logger.critical(self._format_msg(msg, self.BOLD + self.RED))

# Global instance for easy access
logger = SatelliteLogger()

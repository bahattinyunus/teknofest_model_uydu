import time
import psutil
from logger import logger

class SystemHealthMonitor:
    """
    Monitors system resource usage and health of core components.
    Automatically logs warnings if thresholds are exceeded.
    """

    def __init__(self, cpu_threshold=80.0, mem_threshold=80.0):
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.start_time = time.time()
        logger.info("Health Monitor Initialized.")

    def get_uptime(self) -> float:
        """Returns system uptime in seconds."""
        return time.time() - self.start_time

    def check_health(self) -> dict:
        """Performs a full health check of the system."""
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        
        health_report = {
            "cpu_usage": cpu_usage,
            "memory_usage": mem_usage,
            "uptime": self.get_uptime(),
            "status": "HEALTHY"
        }

        if cpu_usage > self.cpu_threshold:
            logger.warning(f"High CPU Usage Detected: {cpu_usage}%")
            health_report["status"] = "WARNING"

        if mem_usage > self.mem_threshold:
            logger.warning(f"High Memory Usage Detected: {mem_usage}%")
            health_report["status"] = "WARNING"

        return health_report

    def log_heartbeat(self):
        """Logs a periodic heartbeat for system status."""
        report = self.check_health()
        logger.debug(f"HEARTBEAT | CPU: {report['cpu_usage']}% | MEM: {report['memory_usage']}% | Uptime: {report['uptime']:.1f}s")

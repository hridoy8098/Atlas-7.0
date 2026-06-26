import platform
import psutil
import datetime

from .disk_health import DiskHealth
from .driver_checker import DriverChecker
from .gaming_mode import GamingMode
from .internet_speed import InternetSpeed
from .ram_optimizer import RAMOptimizer
from .startup_manager import StartupManager
from .system_metrics import SystemMetrics
from .temp_monitor import TempMonitor


class PCHealthReport:
    def __init__(self):
        self.disk = DiskHealth()
        self.drivers = DriverChecker()
        self.gaming = GamingMode()
        self.internet = InternetSpeed()
        self.ram = RAMOptimizer()
        self.startup = StartupManager()
        self.metrics = SystemMetrics()
        self.temp = TempMonitor()

    def generate_system_info(self):
        try:
            uname = platform.uname()
            return {
                "system": uname.system,
                "node_name": uname.node,
                "release": uname.release,
                "version": uname.version,
                "machine": uname.machine,
                "processor": uname.processor,
                "boot_time": datetime.datetime.fromtimestamp(
                    psutil.boot_time()
                ).isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_full_report(self):
        try:
            report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "system_info": self.generate_system_info(),
                "disk_health": self.disk.health_check(),
                "disk_partitions": self.disk.get_disk_partitions(),
                "drivers": self.drivers.get_driver_info(),
                "gaming_mode": self.gaming.get_status(),
                "memory": self.metrics.get_memory(),
                "cpu": self.metrics.get_cpu(),
                "temperature": self.temp.get_temperature(),
                "startup_programs": self.startup.list_startup_programs(),
                "process_count": self.ram.get_process_count(),
            }
            report["overall_health"] = self._assess_health(report)
            return report
        except Exception as e:
            return {"error": str(e)}

    def _assess_health(self, report):
        try:
            score = 100
            issues = []

            disk = report.get("disk_health", {})
            if not disk.get("healthy", True):
                score -= 20
                issues.extend(disk.get("issues", []))

            memory = report.get("memory", {})
            mem_percent = memory.get("percent", 0)
            if mem_percent > 90:
                score -= 15
                issues.append("Memory usage critical")
            elif mem_percent > 80:
                score -= 10
                issues.append("Memory usage high")

            temp = report.get("temperature", {})
            temps = temp if isinstance(temp, list) else [temp]
            for t in temps:
                if isinstance(t, dict) and t.get("current", 0) > 80:
                    score -= 10
                    issues.append(f"High temperature on {t.get('label', 'unknown')}")

            return {
                "score": max(score, 0),
                "issues": issues,
                "status": "Good" if score >= 80 else "Fair" if score >= 50 else "Poor",
            }
        except Exception as e:
            return {"score": 0, "issues": [str(e)], "status": "Error"}

    def quick_health(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "boot_time": datetime.datetime.fromtimestamp(
                psutil.boot_time()
            ).isoformat(),
        }

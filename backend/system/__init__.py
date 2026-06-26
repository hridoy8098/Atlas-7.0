"""System modules: disk health, drivers, gaming, internet speed, PC health, RAM, startup, metrics, temperature"""

from .disk_health import DiskHealth
from .driver_checker import DriverChecker
from .gaming_mode import GamingMode
from .internet_speed import InternetSpeed
from .pc_health_report import PCHealthReport
from .ram_optimizer import RAMOptimizer
from .startup_manager import StartupManager
from .system_metrics import SystemMetrics
from .temp_monitor import TempMonitor

__all__ = ["DiskHealth", "DriverChecker", "GamingMode", "InternetSpeed",
           "PCHealthReport", "RAMOptimizer", "StartupManager", "SystemMetrics", "TempMonitor"]

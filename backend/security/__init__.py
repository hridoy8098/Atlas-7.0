"""Security modules: breaches, fake screen, malware, network, passwords, privacy, watermark, self-destruct, 2FA"""

from .breach_detector import BreachDetector
from .fake_screen import FakeScreen
from .malware_scanner import MalwareScanner
from .network_monitor import NetworkMonitor
from .password_manager import PasswordManager
from .privacy_mode import PrivacyMode
from .screen_watermark import ScreenWatermark
from .self_destruct import SelfDestruct
from .two_fa_manager import TwoFAManager

__all__ = ["BreachDetector", "FakeScreen", "MalwareScanner", "NetworkMonitor",
           "PasswordManager", "PrivacyMode", "ScreenWatermark", "SelfDestruct", "TwoFAManager"]

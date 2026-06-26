import getpass
import os
import platform
import random
import socket
import sys
import time


class ScreenWatermark:
    def __init__(self, user_info: str = None):
        self.user_info = user_info or self._default_user_info()
        self._active = False
        self._opacity = 0.15
        self._position = "bottom-right"

    def _default_user_info(self) -> str:
        user = getpass.getuser()
        host = socket.gethostname()
        ip = self._get_ip()
        return f"{user}@{host} | {ip}"

    def _get_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def enable(self, user_info: str = None):
        if user_info:
            self.user_info = user_info
        self._active = True

    def disable(self):
        self._active = False

    def is_active(self) -> bool:
        return self._active

    def set_opacity(self, opacity: float):
        self._opacity = max(0.0, min(1.0, opacity))

    def set_position(self, position: str):
        valid = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if position in valid:
            self._position = position

    def get_watermark_text(self) -> str:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"CONFIDENTIAL | {self.user_info} | {timestamp}"

    def get_config(self) -> dict:
        return {
            "active": self._active,
            "user_info": self.user_info,
            "opacity": self._opacity,
            "position": self._position,
        }

import os
import random
import sys
import time


class FakeScreen:
    BSOD_LINES = [
        "A problem has been detected and Windows has been shut down to prevent damage to your computer.",
        "",
        "DRIVER_IRQL_NOT_LESS_OR_EQUAL",
        "",
        "If this is the first time you've seen this stop error screen,",
        "restart your computer. If this screen appears again, follow",
        "these steps:",
        "",
        "Check to make sure any new hardware or software is properly installed.",
        "If this is a new installation, ask your hardware or software manufacturer",
        "for any Windows updates you might need.",
        "",
        "Technical information:",
        "",
        "*** STOP: 0x000000D1 (0x0000000C, 0x00000002, 0x00000000, 0xF86B5A89)",
        "",
    ]

    MAC_BLACK_SCREEN = [
        "Your computer has been locked.",
        "Please contact your system administrator.",
        "",
        "Serial Number: XXXXXXXXXXXX",
    ]

    def __init__(self, screen_type: str = "bsod", duration: int = 30):
        self.screen_type = screen_type
        self.duration = duration
        self._active = False

    def _build_bsod(self) -> str:
        lines = self.BSOD_LINES + [
            "",
            f"*** {os.uname().nodename if hasattr(os, 'uname') else 'PC'}",
            f"*** Address 0x{random.getrandbits(32):08X} base at 0x{random.getrandbits(32):08X}",
        ]
        width = 80
        border = "=" * width
        body = "\n".join(line.center(width) for line in lines)
        return f"{border}\n{body}\n{border}"

    def _build_mac_lock(self) -> str:
        width = 60
        border = "-" * width
        lines = self.MAC_BLACK_SCREEN + [
            "",
            f"IP Address: 192.168.{random.randint(0, 255)}.{random.randint(1, 254)}",
            f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        body = "\n".join(line.center(width) for line in lines)
        return f"{border}\n{body}\n{border}"

    def display(self):
        self._active = True
        if self.screen_type == "bsod":
            output = self._build_bsod()
        elif self.screen_type == "mac_lock":
            output = self._build_mac_lock()
        else:
            output = self._build_bsod()
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(output)
        sys.stdout.flush()

    def dismiss(self):
        self._active = False
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def is_active(self) -> bool:
        return self._active

    def remaining_time(self) -> int:
        return self.duration if self._active else 0

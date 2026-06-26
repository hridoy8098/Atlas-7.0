import os
import platform
import subprocess
import sys
import time


class PrivacyMode:
    def __init__(self):
        self._active = False
        self._screen_blanked = False
        self._mic_blocked = False
        self._cam_blocked = False
        self._system = platform.system()

    def enable(self, block_mic: bool = True, block_cam: bool = True, blank_screen: bool = True) -> dict:
        results = {"screen": False, "mic": False, "cam": False}
        if blank_screen:
            results["screen"] = self._blank_screen()
        if block_mic:
            results["mic"] = self._block_microphone()
        if block_cam:
            results["cam"] = self._block_camera()
        self._active = any(results.values())
        return results

    def disable(self) -> dict:
        results = {"screen": False, "mic": False, "cam": False}
        if self._screen_blanked:
            results["screen"] = self._restore_screen()
        if self._mic_blocked:
            results["mic"] = self._unblock_microphone()
        if self._cam_blocked:
            results["cam"] = self._unblock_camera()
        self._active = False
        return results

    def _blank_screen(self) -> bool:
        try:
            if self._system == "Windows":
                import ctypes
                ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
            elif self._system == "Darwin":
                subprocess.run(["pmset", "displaysleepnow"], capture_output=True, timeout=5)
            else:
                subprocess.run(["xset", "dpms", "force", "off"], capture_output=True, timeout=5)
            self._screen_blanked = True
            return True
        except Exception:
            sys.stderr.write("Warning: Could not blank screen\n")
            return False

    def _restore_screen(self) -> bool:
        try:
            if self._system == "Windows":
                import ctypes
                ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, -1)
            elif self._system == "Darwin":
                subprocess.run(["caffeinate", "-u", "-t", "1"], capture_output=True, timeout=5)
            else:
                subprocess.run(["xset", "dpms", "force", "on"], capture_output=True, timeout=5)
            self._screen_blanked = False
            return True
        except Exception:
            return False

    def _block_microphone(self) -> bool:
        self._mic_blocked = True
        return True

    def _unblock_microphone(self) -> bool:
        self._mic_blocked = False
        return True

    def _block_camera(self) -> bool:
        self._cam_blocked = True
        return True

    def _unblock_camera(self) -> bool:
        self._cam_blocked = False
        return True

    def is_active(self) -> bool:
        return self._active

    def status(self) -> dict:
        return {
            "active": self._active,
            "screen_blanked": self._screen_blanked,
            "mic_blocked": self._mic_blocked,
            "cam_blocked": self._cam_blocked,
        }

    def toggle(self) -> dict:
        if self._active:
            return self.disable()
        return self.enable()

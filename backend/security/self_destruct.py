import hashlib
import os
import random
import shutil
import sys
import threading
import time


class SelfDestruct:
    def __init__(self, confirm_phrase: str = "DESTROY"):
        self.confirm_phrase = confirm_phrase
        self._armed = False
        self._countdown = 10
        self._aborted = False
        self._lock = threading.Lock()

    def arm(self, countdown: int = 10):
        self._countdown = max(1, countdown)
        self._armed = True
        self._aborted = False

    def disarm(self) -> bool:
        with self._lock:
            if self._armed:
                self._armed = False
                self._aborted = True
                return True
            return False

    def is_armed(self) -> bool:
        return self._armed

    def _secure_delete_file(self, filepath: str, passes: int = 3):
        if not os.path.isfile(filepath):
            return
        try:
            size = os.path.getsize(filepath)
            with open(filepath, "wb") as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(size))
                    f.flush()
                    os.fsync(f.fileno())
            os.remove(filepath)
        except (OSError, PermissionError):
            try:
                os.remove(filepath)
            except (OSError, PermissionError):
                pass

    def _secure_delete_directory(self, directory: str):
        if not os.path.isdir(directory):
            return
        for root, dirs, files in os.walk(directory, topdown=False):
            for fname in files:
                self._secure_delete_file(os.path.join(root, fname))
            for dname in dirs:
                try:
                    os.rmdir(os.path.join(root, dname))
                except OSError:
                    pass
        try:
            os.rmdir(directory)
        except OSError:
            pass

    def secure_delete(self, path: str, passes: int = 3) -> dict:
        if not os.path.exists(path):
            return {"success": False, "error": "Path does not exist"}
        try:
            if os.path.isfile(path):
                self._secure_delete_file(path, passes)
            else:
                self._secure_delete_directory(path)
            return {"success": True, "path": path, "passes": passes}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _emergency_shutdown(self):
        system = sys.platform
        try:
            if system == "win32":
                os.system("shutdown /s /t 0 /f")
            elif system == "darwin":
                os.system("sudo shutdown -h now")
            else:
                os.system("sudo shutdown -h now")
        except Exception:
            pass

    def execute(self, confirm_phrase: str, secure_paths: list = None) -> dict:
        if confirm_phrase != self.confirm_phrase:
            return {"success": False, "error": "Invalid confirm phrase"}
        if not self._armed:
            return {"success": False, "error": "Not armed"}
        results = {"secure_deletions": [], "emergency_shutdown": False}
        if secure_paths:
            for path in secure_paths:
                results["secure_deletions"].append(self.secure_delete(path))
        for i in range(self._countdown, 0, -1):
            with self._lock:
                if self._aborted:
                    return {"success": False, "error": "Aborted", "partial": results}
            time.sleep(1)
        self._emergency_shutdown()
        results["emergency_shutdown"] = True
        self._armed = False
        return {"success": True, **results}

    def get_status(self) -> dict:
        return {
            "armed": self._armed,
            "countdown": self._countdown,
            "aborted": self._aborted,
        }

import platform
import subprocess
import os


class GamingMode:
    def __init__(self):
        self.system = platform.system()
        self._active = False

    def _run_powershell(self, command):
        try:
            cmd = ["powershell", "-Command", command]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            return str(e)

    def enable(self):
        try:
            if self.system == "Windows":
                self._run_powershell(
                    "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
                )
                self._run_powershell(
                    "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name 'AppCaptureEnabled' -Value 0"
                )
            self._active = True
            return {"success": True, "message": "Gaming mode enabled"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def disable(self):
        try:
            if self.system == "Windows":
                self._run_powershell(
                    "powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2f"
                )
                self._run_powershell(
                    "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR' -Name 'AppCaptureEnabled' -Value 1"
                )
            self._active = False
            return {"success": True, "message": "Gaming mode disabled"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def is_active(self):
        return {"gaming_mode": self._active}

    def get_status(self):
        try:
            plan = ""
            if self.system == "Windows":
                output = self._run_powershell(
                    "powercfg /getactivescheme"
                )
                plan = output
            return {
                "active": self._active,
                "power_plan": plan,
                "system": self.system,
            }
        except Exception as e:
            return {"active": self._active, "system": self.system, "error": str(e)}

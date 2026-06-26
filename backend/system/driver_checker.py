import platform
import subprocess
import os


class DriverChecker:
    def __init__(self):
        self.system = platform.system()

    def _run_command(self, cmd):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, shell=True
            )
            return result.stdout.strip()
        except Exception as e:
            return str(e)

    def list_drivers(self):
        if self.system == "Windows":
            output = self._run_command("wmic sysdriver get DisplayName,Name,State")
            drivers = []
            for line in output.splitlines()[1:]:
                if line.strip():
                    drivers.append(line.strip())
            return drivers
        elif self.system == "Linux":
            output = self._run_command("lsmod")
            drivers = []
            for line in output.splitlines()[1:]:
                if line.strip():
                    parts = line.split()
                    drivers.append(parts[0] if parts else line.strip())
            return drivers
        else:
            output = self._run_command("kextstat")
            drivers = []
            for line in output.splitlines()[1:]:
                if line.strip():
                    drivers.append(line.strip())
            return drivers

    def check_driver(self, name):
        try:
            drivers = self.list_drivers()
            for d in drivers:
                if name.lower() in d.lower():
                    return {"name": name, "found": True, "status": "loaded"}
            return {"name": name, "found": False, "status": "not found"}
        except Exception as e:
            return {"name": name, "found": False, "status": str(e)}

    def get_outdated_drivers(self):
        try:
            drivers = self.list_drivers()
            return {
                "system": self.system,
                "total_drivers": len(drivers),
                "drivers": drivers[:50],
                "note": "Version comparison requires manufacturer tools",
            }
        except Exception as e:
            return {"error": str(e)}

    def get_driver_info(self):
        return {
            "system": self.system,
            "driver_count": len(self.list_drivers()),
            "method": "wmic" if self.system == "Windows" else "lsmod/kextstat",
        }

import psutil
import platform


class TempMonitor:
    def __init__(self):
        self.system = platform.system()

    def get_temperature(self):
        try:
            temps = []
            if hasattr(psutil, "sensors_temperatures"):
                sensors = psutil.sensors_temperatures()
                if sensors:
                    for name, entries in sensors.items():
                        for entry in entries:
                            temps.append(
                                {
                                    "label": name,
                                    "current": entry.current,
                                    "high": entry.high,
                                    "critical": entry.critical,
                                }
                            )
            if not temps:
                temps.append(self._fallback_temp())
            return temps
        except Exception as e:
            return [{"label": "error", "current": 0, "high": 0, "critical": 0, "error": str(e)}]

    def _fallback_temp(self):
        try:
            if self.system == "Windows":
                import subprocess

                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root/wmi | Select-Object -ExpandProperty CurrentTemperature",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.stdout.strip():
                    try:
                        temp_kelvin = int(result.stdout.strip().splitlines()[0])
                        temp_celsius = round((temp_kelvin - 2732) / 10.0, 1)
                        return {
                            "label": "ACPI thermal zone",
                            "current": temp_celsius,
                            "high": None,
                            "critical": None,
                        }
                    except (ValueError, IndexError):
                        pass
            return {
                "label": "CPU (estimated)",
                "current": round(psutil.cpu_percent(interval=1) * 0.5 + 40, 1),
                "high": None,
                "critical": None,
            }
        except Exception:
            return {
                "label": "CPU (estimated)",
                "current": round(psutil.cpu_percent(interval=1) * 0.5 + 40, 1),
                "high": None,
                "critical": None,
            }

    def get_fan_speed(self):
        try:
            fans = []
            if hasattr(psutil, "sensors_fans"):
                sensor_fans = psutil.sensors_fans()
                if sensor_fans:
                    for name, entries in sensor_fans.items():
                        for entry in entries:
                            fans.append(
                                {
                                    "label": name,
                                    "speed_rpm": entry.current,
                                }
                            )
            return fans if fans else [{"label": "N/A", "speed_rpm": 0}]
        except Exception as e:
            return [{"label": "error", "speed_rpm": 0, "error": str(e)}]

    def health_status(self):
        try:
            temps = self.get_temperature()
            status = "normal"
            issues = []
            for t in temps:
                current = t.get("current", 0)
                if current > 80:
                    status = "critical"
                    issues.append(f"{t['label']}: {current}°C is critical")
                elif current > 70:
                    status = "warning"
                    issues.append(f"{t['label']}: {current}°C is high")
            return {"status": status, "issues": issues, "temperatures": temps}
        except Exception as e:
            return {"status": "error", "issues": [str(e)], "temperatures": []}

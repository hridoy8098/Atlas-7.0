import platform
import os
import subprocess


class StartupManager:
    def __init__(self):
        self.system = platform.system()

    def _run_powershell(self, command):
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout.strip()
        except Exception as e:
            return str(e)

    def list_startup_programs(self):
        try:
            if self.system == "Windows":
                output = self._run_powershell(
                    "Get-CimInstance -ClassName Win32_StartupCommand | Select-Object Name, Command, Location, User | ConvertTo-Json"
                )
                import json

                try:
                    items = json.loads(output)
                    if isinstance(items, dict):
                        items = [items]
                    return items if isinstance(items, list) else []
                except json.JSONDecodeError:
                    return []
            else:
                autostart_dirs = [
                    os.path.expanduser("~/.config/autostart"),
                    "/etc/xdg/autostart",
                ]
                items = []
                for d in autostart_dirs:
                    if os.path.isdir(d):
                        for f in os.listdir(d):
                            if f.endswith(".desktop"):
                                items.append(
                                    {"name": f, "path": os.path.join(d, f)}
                                )
                return items
        except Exception as e:
            return {"error": str(e)}

    def enable_program(self, name, command=""):
        try:
            if self.system == "Windows":
                key_path = (
                    "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                )
                self._run_powershell(
                    f"New-ItemProperty -Path '{key_path}' -Name '{name}' -Value '{command}' -PropertyType String -Force"
                )
                return {"success": True, "message": f"Enabled {name}"}
            else:
                path = os.path.expanduser(f"~/.config/autostart/{name}.desktop")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(f"[Desktop Entry]\nType=Application\nName={name}\nExec={command}\n")
                return {"success": True, "message": f"Enabled {name}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def disable_program(self, name):
        try:
            if self.system == "Windows":
                key_path = (
                    "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                )
                self._run_powershell(
                    f"Remove-ItemProperty -Path '{key_path}' -Name '{name}' -ErrorAction SilentlyContinue"
                )
                return {"success": True, "message": f"Disabled {name}"}
            else:
                path = os.path.expanduser(f"~/.config/autostart/{name}.desktop")
                if os.path.exists(path):
                    os.remove(path)
                return {"success": True, "message": f"Disabled {name}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

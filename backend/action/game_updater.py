# backend/action/game_updater.py
import json
import os
import subprocess
import sys
import platform
from pathlib import Path


_OS = platform.system()


def _get_steam_path() -> str:
    if _OS == "Windows":
        candidates = [
            r"C:\Program Files (x86)\Steam",
            r"C:\Program Files\Steam",
            os.path.expanduser(r"~\AppData\Roaming\Steam"),
        ]
        for c in candidates:
            if Path(c).exists():
                return c
    elif _OS == "Darwin":
        candidates = [
            os.path.expanduser("~/Library/Application Support/Steam"),
            "/Applications/Steam.app",
        ]
        for c in candidates:
            if Path(c).exists():
                return c
    else:
        candidates = [
            os.path.expanduser("~/.steam/steam"),
            os.path.expanduser("~/.local/share/Steam"),
            "/usr/share/steam",
        ]
        for c in candidates:
            if Path(c).exists():
                return c
    return ""


def _get_epic_path() -> str:
    if _OS == "Windows":
        candidates = [
            r"C:\Program Files (x86)\Epic Games\Launcher",
            os.path.expanduser(r"~\AppData\Local\EpicGames\Launcher"),
        ]
        for c in candidates:
            if Path(c).exists():
                return c
    return ""


def check_steam_installed() -> bool:
    return bool(_get_steam_path())


def check_epic_installed() -> bool:
    return bool(_get_epic_path())


def launch_steam() -> str:
    if _OS == "Windows":
        steam_exe = Path(_get_steam_path()) / "Steam.exe"
        if steam_exe.exists():
            subprocess.Popen([str(steam_exe)])
            return "Launching Steam..."
        steam_exe = Path(_get_steam_path()) / "steamapps" / "steam.exe"
        if steam_exe.exists():
            subprocess.Popen([str(steam_exe)])
            return "Launching Steam..."
    elif _OS == "Darwin":
        steam_app = "/Applications/Steam.app"
        if Path(steam_app).exists():
            subprocess.Popen(["open", steam_app])
            return "Launching Steam..."
    else:
        for cmd in ["steam", "steam-runtime"]:
            if subprocess.run(["which", cmd], capture_output=True).returncode == 0:
                subprocess.Popen([cmd])
                return f"Launching {cmd}..."
    return "Steam not found on this system."


def launch_epic() -> str:
    if _OS != "Windows":
        return "Epic Games Launcher is only supported on Windows."

    epic_exe = Path(_get_epic_path()) / "Portal" / "Binaries" / "Win64" / "EpicGamesLauncher.exe"
    if epic_exe.exists():
        subprocess.Popen([str(epic_exe)])
        return "Launching Epic Games Launcher..."
    return "Epic Games Launcher not found."


def check_game_updates() -> str:
    lines = []
    steam_path = _get_steam_path()
    if steam_path:
        lines.append(f"✅ Steam found: {steam_path}")
        steamapps = Path(steam_path) / "steamapps"
        if steamapps.exists():
            acf_files = list(steamapps.glob("appmanifest_*.acf"))
            if acf_files:
                lines.append(f"   {len(acf_files)} game(s) installed")
                for acf in sorted(acf_files)[:10]:
                    try:
                        content = acf.read_text(encoding="utf-8", errors="ignore")
                        name_match = __import__("re").search(r'"name"\s+"([^"]+)"', content)
                        if name_match:
                            lines.append(f"   - {name_match.group(1)}")
                    except Exception:
                        pass
                if len(acf_files) > 10:
                    lines.append(f"   ... and {len(acf_files) - 10} more")
            else:
                lines.append("   No games found in steamapps.")
    else:
        lines.append("❌ Steam not found on this system.")

    epic_path = _get_epic_path()
    if epic_path:
        lines.append(f"✅ Epic Games Launcher found: {epic_path}")
    else:
        lines.append("❌ Epic Games Launcher not found.")

    return "\n".join(lines) if lines else "No game platforms detected."


def installed_games() -> str:
    games = []

    steam_path = _get_steam_path()
    if steam_path:
        steamapps = Path(steam_path) / "steamapps"
        if steamapps.exists():
            import re
            for acf in sorted(steamapps.glob("appmanifest_*.acf")):
                try:
                    content = acf.read_text(encoding="utf-8", errors="ignore")
                    name = re.search(r'"name"\s+"([^"]+)"', content)
                    appid = re.search(r'"appid"\s+"(\d+)"', content)
                    if name:
                        g = name.group(1)
                        if appid:
                            g += f" (appid: {appid.group(1)})"
                        games.append(g)
                except Exception:
                    pass

    if games:
        return f"Found {len(games)} installed game(s):\n" + "\n".join(games[:30])
    return "No installed games detected."


def game_updater(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if not action:
        return "No action specified for game_updater."

    if player:
        player.write_log(f"[GameUpdater] {action}")

    try:
        if action == "check":
            return check_game_updates()
        elif action == "installed":
            return installed_games()
        elif action == "launch_steam":
            return launch_steam()
        elif action == "launch_epic":
            return launch_epic()
        elif action == "status":
            lines = []
            lines.append(f"Steam installed: {check_steam_installed()}")
            lines.append(f"Epic installed: {check_epic_installed()}")
            return "\n".join(lines)
        else:
            return f"Unknown action: '{action}'. Use: check, installed, launch_steam, launch_epic, status."
    except Exception as e:
        return f"Game updater error: {e}"

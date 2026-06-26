# backend/action/open_app.py
import os
import re
import shutil
import subprocess
import sys
import platform
from pathlib import Path

_OS = platform.system()


_KNOWN_APPS: dict[str, dict[str, list[str]]] = {
    "chrome": {
        "Darwin":  ["/Applications/Google Chrome.app"],
        "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
        "Linux":   ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"],
    },
    "firefox": {
        "Darwin":  ["/Applications/Firefox.app"],
        "Windows": [r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"],
        "Linux":   ["firefox"],
    },
    "edge": {
        "Darwin":  ["/Applications/Microsoft Edge.app"],
        "Windows": [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe")],
        "Linux":   ["microsoft-edge", "microsoft-edge-stable"],
    },
    "vscode": {
        "Darwin":  ["/Applications/Visual Studio Code.app"],
        "Windows": [r"C:\Program Files\Microsoft VS Code\Code.exe",
                    os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe")],
        "Linux":   ["code"],
    },
    "spotify": {
        "Darwin":  ["/Applications/Spotify.app"],
        "Windows": [os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe"),
                    r"C:\Program Files\Spotify\Spotify.exe"],
        "Linux":   ["spotify"],
    },
    "discord": {
        "Darwin":  ["/Applications/Discord.app"],
        "Windows": [os.path.expanduser(r"~\AppData\Local\Discord\Update.exe"),
                    os.path.expanduser(r"~\AppData\Local\Discord\app-*\Discord.exe")],
        "Linux":   ["discord"],
    },
    "slack": {
        "Darwin":  ["/Applications/Slack.app"],
        "Windows": [os.path.expanduser(r"~\AppData\Local\slack\slack.exe")],
        "Linux":   ["slack"],
    },
    "zoom": {
        "Darwin":  ["/Applications/zoom.us.app"],
        "Windows": [os.path.expanduser(r"~\AppData\Roaming\Zoom\bin\Zoom.exe")],
        "Linux":   ["zoom"],
    },
    "notion": {
        "Darwin":  ["/Applications/Notion.app"],
        "Windows": [os.path.expanduser(r"~\AppData\Local\Programs\Notion\Notion.exe")],
        "Linux":   ["notion", "notion-snap"],
    },
    "obsidian": {
        "Darwin":  ["/Applications/Obsidian.app"],
        "Windows": [os.path.expanduser(r"~\AppData\Local\Obsidian\Obsidian.exe")],
        "Linux":   ["obsidian"],
    },
    "terminal": {
        "Darwin":  ["/Applications/Utilities/Terminal.app"],
        "Windows": ["cmd.exe", r"C:\Windows\System32\cmd.exe"],
        "Linux":   ["gnome-terminal", "konsole", "xterm"],
    },
    "calculator": {
        "Darwin":  ["/System/Applications/Calculator.app"],
        "Windows": ["calc.exe"],
        "Linux":   ["gnome-calculator", "kcalc", "qalculate-gtk"],
    },
    "file_explorer": {
        "Darwin":  ["Finder"],
        "Windows": ["explorer.exe"],
        "Linux":   ["nautilus", "thunar", "dolphin", "nemo"],
    },
    "settings": {
        "Darwin":  ["/System/Applications/System Settings.app"],
        "Windows": ["ms-settings:"],
        "Linux":   ["gnome-control-center", "xfce4-settings-manager", "kcmshell5"],
    },
}


def _find_app_path(app_key: str) -> str | None:
    app_key = app_key.lower().strip()
    if app_key not in _KNOWN_APPS:
        return None

    candidates = _KNOWN_APPS[app_key].get(_OS, [])

    for path in candidates:
        if "*" in path:
            from glob import glob
            matches = sorted(glob(path))
            if matches:
                return matches[-1]
        if shutil.which(path):
            return path
        p = Path(path)
        if p.exists():
            return str(p)

    return None


def _launch_via_registry(app_name: str) -> str | None:
    if _OS != "Windows":
        return None
    try:
        import winreg
        app_name_lower = app_name.lower()
        reg_map = {
            "chrome": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            "firefox": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
            "edge": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
            "vscode": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Code.exe",
        }
        key_path = reg_map.get(app_name_lower)
        if not key_path:
            return None
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        val = winreg.QueryValue(key, None)
        winreg.CloseKey(key)
        exe = val.strip().strip('"').split('"')[0].split(" --")[0].strip()
        if Path(exe).exists():
            return exe
    except Exception:
        pass
    return None


def _open_app(app_name: str, url: str = "") -> str:
    app_lower = app_name.lower().strip()

    app_key_map = {
        "youtube": "chrome",
        "gmail": "chrome",
        "github": "chrome",
        "facebook": "chrome",
        "chatgpt": "chrome",
        "whatsapp": "chrome",
    }

    key = app_key_map.get(app_lower, app_lower)
    app_path = _find_app_path(key) or _launch_via_registry(key)

    if app_path:
        try:
            if app_path.endswith(":") and _OS == "Windows":
                subprocess.Popen(["start", app_path], shell=True)
            elif _OS == "Darwin" and app_path.endswith(".app"):
                subprocess.Popen(["open", "-a", app_path])
            elif _OS == "Windows" and (
                app_path.endswith("explorer.exe") or app_path == "explorer.exe"
            ):
                subprocess.Popen(["explorer.exe"])
            else:
                subprocess.Popen([app_path])

            if url:
                return f"Opened {app_name} with {url}"
            return f"Opened {app_name}"
        except Exception as e:
            return f"Could not open {app_name}: {e}"

    if _OS == "Darwin":
        try:
            subprocess.run(["open", "-a", app_name.capitalize()], capture_output=True, timeout=5)
            return f"Opened {app_name} (by name)"
        except Exception:
            pass

    if _OS == "Windows":
        try:
            subprocess.Popen(["start", app_name], shell=True)
            return f"Opened {app_name} (via start)"
        except Exception as e:
            return f"Could not open {app_name}: {e}"

    try:
        if shutil.which(app_name):
            subprocess.Popen([app_name])
            return f"Opened {app_name} (via PATH)"
    except Exception:
        pass

    try:
        subprocess.Popen(["xdg-open", app_name])
        return f"Opened {app_name} (via xdg-open)"
    except Exception:
        pass

    return f"Could not find or open: {app_name}"


def _build_url_for_app(app_name: str, query: str) -> str:
    url_map = {
        "youtube": "https://www.youtube.com/results?search_query={}",
        "gmail": "https://mail.google.com/mail/?view=cm&fs=1&su={}",
        "github": "https://github.com/search?q={}",
        "chatgpt": "https://chat.openai.com/?q={}",
        "google": "https://www.google.com/search?q={}",
    }
    template = url_map.get(app_name.lower().strip())
    if template and query:
        return template.format(query.replace(" ", "+"))
    if app_name.lower().strip() == "youtube":
        return "https://www.youtube.com"
    return ""


def open_app(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    app_name = params.get("app_name", "").strip() or params.get("app", "").strip()
    url = params.get("url", "").strip()
    query = params.get("query", "").strip()

    if not app_name:
        return "Please specify an app name to open."

    if player:
        player.write_log(f"[OpenApp] {app_name}")

    if not url and query:
        url = _build_url_for_app(app_name, query)

    auto_map = {
        "youtube": "chrome",
        "gmail": "chrome",
        "github": "chrome",
        "facebook": "chrome",
        "chatgpt": "chrome",
        "whatsapp": "chrome",
        "google": "chrome",
        "maps": "chrome",
    }

    final_app = auto_map.get(app_name.lower(), app_name)

    if url and final_app.lower() in ("chrome", "firefox", "edge", "browser"):
        browser_path = _find_app_path(final_app)
        if browser_path:
            try:
                if not url.startswith("http"):
                    url = "https://" + url
                subprocess.Popen([browser_path, url])
                return f"Opened {url} in {final_app}"
            except Exception as e:
                return f"Could not open {url} in {final_app}: {e}"
        return f"Browser '{final_app}' not found."

    return _open_app(app_name, url)

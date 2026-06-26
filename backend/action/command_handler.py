# backend/action/command_handler.py — Action Command Handler (Single-step Actions)
# ভয়েস কমান্ড থেকে সরাসরি action module এ রাউট করে

from typing import Dict, Any, Optional, Callable
import importlib


ACTION_MODULE_MAP = {
    "open_app":            ("backend.action.open_app",            "open_app"),
    "app_open":            ("backend.action.open_app",            "open_app"),
    "web_search":          ("backend.action.web_search",          "web_search"),
    "browser_control":     ("backend.action.browser_control",     "browser_control"),
    "file_controller":     ("backend.action.file_controller",     "file_controller"),
    "file_processor":      ("backend.action.file_processor",      "file_processor"),
    "cmd_control":         ("backend.action.cmd_control",         "cmd_control"),
    "code_helper":         ("backend.action.code_helper",         "code_helper"),
    "computer_control":    ("backend.action.computer_control",    "computer_control"),
    "computer_settings":   ("backend.action.computer_settings",   "computer_settings"),
    "desktop_control":     ("backend.action.desktop",             "desktop_control"),
    "desktop":             ("backend.action.desktop",             "desktop_control"),
    "dev_agent":           ("backend.action.dev_agent",           "dev_agent"),
    "flight_finder":       ("backend.action.flight_finder",       "flight_finder"),
    "game_updater":        ("backend.action.game_updater",        "game_updater"),
    "reminder":            ("backend.action.reminder",            "reminder"),
    "youtube_video":       ("backend.action.youtube_video",       "youtube_video"),
    "weather_report":      ("backend.action.weather_report",      "weather_action"),
    "send_message":        ("backend.action.send_message",        "send_message"),
    "screen_process":      ("backend.action.screen_processor",    "screen_process"),
}


SPEAK_REQUIRED_ACTIONS = {"code_helper", "dev_agent", "game_updater", "flight_finder"}


def handle_action_command(
    intent: str,
    parameters: Dict[str, Any],
    speak: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Action intent + parameters নিয়ে সরাসরি action module call করে
    
    Args:
        intent: action identifier (e.g. "open_app", "web_search")
        parameters: action parameters dict
        speak: voice output callback
    
    Returns:
        {"success": bool, "message": str, "action": str}
    """
    intent_clean = intent.lower().replace("action_", "").replace("voice_", "")

    mod_info = ACTION_MODULE_MAP.get(intent_clean)
    if not mod_info:
        return {
            "success": False,
            "message": f"Unknown action: '{intent}'",
            "action": "unknown",
        }

    module_path, func_name = mod_info

    try:
        mod = importlib.import_module(module_path)
        func = getattr(mod, func_name)

        kwargs = {"parameters": parameters}
        if func_name in SPEAK_REQUIRED_ACTIONS:
            kwargs["speak"] = speak

        result = func(**kwargs)
        msg = str(result)[:500] if result else "Done."

        if speak and msg and msg not in ("Done.", "Completed.", ""):
            speak(msg)

        return {
            "success": True,
            "message": msg,
            "action": intent_clean,
        }

    except Exception as e:
        err_msg = f"Action '{intent_clean}' failed: {str(e)}"
        print(f"[ActionHandler] {err_msg}")
        if speak:
            speak(f"That action failed, sir.")
        return {
            "success": False,
            "message": err_msg,
            "action": "error",
        }


def is_action_intent(intent: str) -> bool:
    intent_clean = intent.lower().replace("action_", "").replace("voice_", "")
    return intent_clean in ACTION_MODULE_MAP


ACTION_KEYWORDS = [
    "open", "launch", "start", "search", "browser", "file", "folder",
    "code", "computer", "desktop", "flight", "game", "remind", "youtube",
    "weather", "message", "screen", "wallpaper", "ব্রাউজার", "ফাইল",
    "ওপেন", "সার্চ", "রিমাইন্ড", "আবহাওয়া", "স্ক্রিন",
]


def is_action_command(command: str) -> bool:
    cmd_lower = command.lower()
    return any(kw in cmd_lower for kw in ACTION_KEYWORDS)

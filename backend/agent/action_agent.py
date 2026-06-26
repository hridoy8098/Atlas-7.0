# backend/agent/action_agent.py
from typing import Dict, List
from .base_agent import BaseAgent


class ActionAgent(BaseAgent):
    """Bridge agent — routes voice intents to action modules in backend/action/"""

    def __init__(self):
        super().__init__(
            name="Action Agent",
            description="Routes voice commands to system action modules (browser, computer, desktop, files, code, youtube, flights, games, reminders, search)"
        )

    def get_capabilities(self) -> List[str]:
        return [
            "browser_control", "code_helper", "computer_control", "computer_settings",
            "desktop", "dev_agent", "file_controller", "file_processor",
            "flight_finder", "game_updater", "open_app", "reminder",
            "web_search", "youtube_video",
        ]

    def handle(self, intent: str, entities: Dict) -> Dict:
        module_name = intent.replace("action_", "").replace("voice_", "")
        params = entities.get("parameters", entities)

        module_map = {
            "browser_control":     ("backend.action.browser_control",     "browser_control"),
            "code_helper":         ("backend.action.code_helper",         "code_helper"),
            "computer_control":    ("backend.action.computer_control",    "computer_control"),
            "computer_settings":   ("backend.action.computer_settings",   "computer_settings"),
            "desktop":             ("backend.action.desktop",             "desktop_control"),
            "dev_agent":           ("backend.action.dev_agent",           "dev_agent"),
            "file_controller":     ("backend.action.file_controller",     "file_controller"),
            "file_processor":      ("backend.action.file_processor",      "file_processor"),
            "flight_finder":       ("backend.action.flight_finder",       "flight_finder"),
            "game_updater":        ("backend.action.game_updater",        "game_updater"),
            "open_app":            ("backend.action.open_app",            "open_app"),
            "reminder":            ("backend.action.reminder",            "reminder"),
            "web_search":          ("backend.action.web_search",          "web_search"),
            "youtube_video":       ("backend.action.youtube_video",       "youtube_video"),
        }

        mod_info = module_map.get(module_name)
        if not mod_info:
            return {
                "success": False,
                "message": f"Unknown action module: '{module_name}'",
                "action": "unknown",
            }

        module_path, func_name = mod_info
        try:
            import importlib
            mod = importlib.import_module(module_path)
            func = getattr(mod, func_name)

            player = entities.get("_player")
            response = entities.get("_response")
            session_memory = entities.get("_session_memory")
            speak = entities.get("_speak")

            kwargs = {"parameters": params, "response": response, "player": player, "session_memory": session_memory}
            if func_name in ("code_helper", "dev_agent"):
                kwargs["speak"] = speak

            result = func(**kwargs)

            return {
                "success": True,
                "message": str(result)[:500],
                "action": module_name,
                "full_result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Action '{module_name}' failed: {e}",
                "action": "error",
            }

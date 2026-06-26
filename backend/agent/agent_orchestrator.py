# backend/agent/agent_orchestrator.py
# Atlas 7.0 - Agent Orchestrator (Optimized)

from typing import Dict, Any, List
import time

# Import all agents
from .pc_agent import PCAgent
from .file_agent import FileAgent
from .web_agent import WebAgent
from .media_agent import MediaAgent
from .productivity_agent import ProductivityAgent
from .security_agent import SecurityAgent
from .app_agent import AppAgent
from .terminal_agent import TerminalAgent
from .automation_agent import automation_agent
from .ml_agent import ml_agent
from .action_agent import ActionAgent
from .browser_agent import BrowserAgent


class AgentOrchestrator:
    def __init__(self):
        # ← FIXED: Lazy loading + singleton pattern
        self._agent_classes = {
            "pc": PCAgent,
            "file": FileAgent,
            "web": WebAgent,
            "media": MediaAgent,
            "productivity": ProductivityAgent,
            "security": SecurityAgent,
            "app": AppAgent,
            "terminal": TerminalAgent,
            "automation": lambda: automation_agent,  # Already instantiated
            "ml": lambda: ml_agent,  # ML Agent singleton
            "action": ActionAgent,
            "browser": BrowserAgent,
        }
        self._agents = {}  # Cache for instantiated agents
        self._metrics = {"total_requests": 0, "fallback_count": 0}
        
        # Pre-instantiate commonly used agents
        self._get_agent("web")
        self._get_agent("app")
        self._get_agent("productivity")
        
        print(f"✅ Agent Orchestrator Loaded with {len(self._agent_classes)} agents")

    def _get_agent(self, key: str):
        """Lazy loading with caching"""
        if key not in self._agents:
            agent = self._agent_classes[key]()
            self._agents[key] = agent
        return self._agents[key]

    def execute(self, intent: str, entities: Dict, original_command: str = "") -> Dict:
        """
        Smart Agent Routing — Fixed & Optimized
        """
        if not intent and not original_command:
            return {"success": False, "message": "No command detected"}

        self._metrics["total_requests"] += 1
        start_time = time.time()
        
        intent_lower = intent.lower()
        cmd_lower = original_command.lower()

        # ========== DIRECT INTENT MAPPING (Primary) ==========
        intent_map = {
            # App Agent
            "open_app": "app", "app_open": "app",

            # PC Agent
            "pc_optimize": "pc", "pc_clean": "pc", "pc_shutdown": "pc",
            "pc_restart": "pc", "pc_lock": "pc", "pc_sleep": "pc",
            "pc_battery": "pc", "pc_status": "pc", "pc_wifi": "pc",
            "pc_bluetooth": "pc", "process_manager": "pc", "startup_apps": "pc",

            # File Agent
            "file_organize": "file", "file_search": "file", "file_create": "file",
            "file_delete": "file", "file_copy": "file", "file_move": "file",
            "file_rename": "file", "file_backup": "file",

            # Web Agent
            "web_search": "web", "web_research": "web", "web_summarize": "web",
            "web_translate": "web", "web_bookmark": "web", "web_history": "web",
            "open_url": "web", "open_website": "web",

            # Media Agent — ← FIXED: removed duplicate "youtube" entry
            "media_youtube": "media", "media_music": "media", "media_video": "media",
            "media_image": "media", "media_meme": "media", "media_download": "media",
            "media_subtitle": "media", "media_convert": "media",
            "play_youtube": "media", "play_music": "media",
            "generate_image": "media", "generate_meme": "media",

            # Productivity Agent
            "productivity_task": "productivity", "productivity_show_tasks": "productivity",
            "productivity_pomodoro": "productivity", "productivity_reminder": "productivity",
            "productivity_calendar": "productivity", "productivity_note": "productivity",
            "productivity_alarm": "productivity",
            "add_task": "productivity", "new_task": "productivity",
            "show_tasks": "productivity", "pomodoro": "productivity",
            "focus_mode": "productivity", "task": "productivity",
            "todo": "productivity", "reminder": "productivity",

            # Security Agent
            "security_lock": "security", "security_privacy": "security",
            "security_breach": "security", "security_password": "security",
            "security_scan": "security", "security_firewall": "security",
            "privacy_mode": "security", "enable_privacy": "security",
            "check_breach": "security",

            # Terminal Agent
            "terminal_run": "terminal", "terminal_git": "terminal",
            "terminal_pip": "terminal", "terminal_npm": "terminal",
            "git_status": "terminal", "git_pull": "terminal",
            "git_push": "terminal", "git_commit": "terminal",
            "pip_install": "terminal", "npm_install": "terminal",

            # ML Agent
            "ml_load": "ml", "ml_clean": "ml", "ml_analyze": "ml",
            "ml_classify": "ml", "ml_regress": "ml", "ml_nlp": "ml",
            "ml_auto": "ml", "ml_predict": "ml", "ml_models": "ml",
            "ml_delete": "ml", "ml_export": "ml", "ml_plot": "ml",
            "load_dataset": "ml", "clean_data": "ml", "analyze_data": "ml",
            "train_classifier": "ml", "train_regressor": "ml",
            "auto_ml": "ml", "predict": "ml",
            "list_models": "ml", "delete_model": "ml",

            # Automation Agent
            "api_test": "automation", "bug_find": "automation",
            "clipboard": "automation", "doc_write": "automation",
            "file_organize_auto": "automation", "git_assist": "automation",
            "news_analyze": "automation", "price_track": "automation",
            "screen_auto": "automation", "social_monitor": "automation",
            "whatsapp_bot": "automation",

            # Browser Agent (Playwright browser automation)
            "browser_open_url": "browser", "browser_search_web": "browser",
            "browser_click": "browser", "browser_type": "browser",
            "browser_type_password": "browser", "browser_scroll": "browser",
            "browser_fill_form": "browser", "browser_get_text": "browser",
            "browser_press_key": "browser", "browser_close": "browser",
            "browser_new_tab": "browser", "browser_switch_tab": "browser",
            "browser_go_back": "browser", "browser_go_forward": "browser",
            "browser_refresh": "browser", "browser_screenshot": "browser",
            "browser_smart_interact": "browser",

            # Action Agent (voice command action modules)
            "action_browser_control": "action", "action_code_helper": "action",
            "action_computer_control": "action", "action_computer_settings": "action",
            "action_desktop": "action", "action_dev_agent": "action",
            "action_file_controller": "action", "action_file_processor": "action",
            "action_flight_finder": "action", "action_game_updater": "action",
            "action_open_app": "action", "action_reminder": "action",
            "action_web_search": "action", "action_youtube_video": "action",
            "voice_browser": "action", "voice_computer": "action",
            "voice_desktop": "action", "voice_files": "action",
            "voice_code": "action", "voice_youtube": "action",
            "voice_flights": "action", "voice_games": "action",
            "voice_reminder": "action", "voice_search": "action",
        }

        # Try direct intent mapping first
        if intent_lower in intent_map:
            agent_key = intent_map[intent_lower]
            agent = self._get_agent(agent_key)
            result = agent.handle(intent, entities)
            result["_routing_time"] = round(time.time() - start_time, 3)
            return result

        # ========== KEYWORD FALLBACK (Secondary) ==========
        self._metrics["fallback_count"] += 1

        # Keyword-to-agent mapping with priority scores
        keyword_map = [
            (["app", "open ", "launch ", "start ", "run ", "load ",
              "chrome", "vscode", "gmail", "github", "facebook", 
              "whatsapp", "chatgpt", "spotify", "discord", "notion",
              "খোল", "চালু", "ওপেন", "লঞ্চ", "শুরু"], "app"),
            
            (["optimize", "clean", "boost", "speed", "shutdown",
              "restart", "lock", "sleep", "battery", "wifi", "bluetooth",
              "process", "startup", "ফাস্ট", "পরিষ্কার", "শাটডাউন"], "pc"),
            
            (["organize", "file", "folder", "directory", "search file",
              "create file", "delete file", "copy file", "move file",
              "rename", "backup", "ফাইল", "ফোল্ডার", "গোছাও"], "file"),
            
            (["research", "search google", "summarize", "translate",
              "bookmark", "history", "খুঁজ", "সার্চ", "ব্যাখ্যা"], "web"),
            
            (["youtube", "music", "video", "image", "meme", "download",
              "subtitle", "convert", "গান", "ভিডিও", "ছবি", "মিম"], "media"),
            
            (["pomodoro", "task", "todo", "reminder", "calendar",
              "note", "alarm", "টাস্ক", "পোমোডোরো", "ক্যালেন্ডার"], "productivity"),
            
            (["privacy", "breach", "password", "scan", "virus",
              "firewall", "প্রাইভেসি", "পাসওয়ার্ড", "ভাইরাস"], "security"),
            
            (["terminal", "git ", "pip ", "npm ", "run command",
              "টার্মিনাল", "গিট", "পিপ"], "terminal"),
            
            (["api test", "bug", "clipboard", "write doc", "screenshot",
              "whatsapp", "হোয়াটসঅ্যাপ", "স্ক্রিনশট"], "automation"),
            
            (["load dataset", "train model", "classify", "predict",
              "machine learning", "ml ", "dataset", "analyze data",
              "ডেটাসেট", "মডেল ট্রেন", "প্রেডিক্ট"], "ml"),

            (["browser", "browser control", "website", "navigation", "webpage",
              "ব্রাউজার"], "action"),

            (["computer control", "mouse", "keyboard", "click", "type", "scroll",
              "screenshot", "কম্পিউটার", "মাউস", "কিবোর্ড"], "action"),

            (["desktop", "wallpaper", "organize desktop", "clean desktop",
              "ডেস্কটপ"], "action"),

            (["file process", "merge csv", "rename files", "resize images",
              "pdf", "csv to json", "json to csv", "word count"], "action"),

            (["flight", "airport", "airplane", "fly", "travel", "ফ্লাইট",
              "বিমান"], "action"),

            (["game", "steam", "epic", "gaming", "গেম", "গেমিং"], "action"),

            (["remind", "reminder", "remember", "remind me", "notify",
              "রিমাইন্ডার", "মনে করিয়ে"], "action"),

            (["search web", "web search", "look up", "fetch url",
              "summarize website", "ওয়েব সার্চ"], "action"),

            (["play video", "watch video",
              "ভিডিও দেখ"], "action"),

            (["weather", "time", "date", "news", "আবহাওয়া", "সময়", "খবর"], "web"),
            
            (["hello", "hi", "hey", "thanks", "help", "হ্যালো", "হাই", "হেল্প"], "chat"),
        ]

        for keywords, agent_key in keyword_map:
            if any(word in cmd_lower for word in keywords):
                if agent_key == "chat":
                    return {
                        "success": True,
                        "message": "👋 Hello! I'm Atlas 7.0. How can I help you today?",
                        "action": "chat"
                    }
                agent = self._get_agent(agent_key)
                result = agent.handle(intent, entities)
                result["_routing_time"] = round(time.time() - start_time, 3)
                return result

        # ========== FALLBACK ==========
        return {
            "success": False,
            "message": "🤔 I didn't understand that command. Try: 'open youtube', 'optimize pc', 'organize downloads', 'research AI', or say 'help' for more options.",
            "action": "unknown",
            "original_command": original_command,
            "suggestion": self._get_suggestion(cmd_lower)
        }

    def _get_suggestion(self, cmd: str) -> str:
        """Suggest closest matching command"""
        # Simple suggestion logic
        if any(x in cmd for x in ["open", "খোল"]):
            return "Try: 'open chrome' or 'open youtube'"
        elif any(x in cmd for x in ["search", "খুঁজ"]):
            return "Try: 'search AI news' or 'research Python'"
        return "Say 'help' for all available commands"

    def get_all_capabilities(self) -> Dict:
        """সব Agent এর capability দেখায়"""
        return {
            name: agent.get_capabilities() 
            for name, agent in self._agents.items()
        }

    def get_agent_status(self) -> Dict:
        """Get all agent status with metrics"""
        return {
            "status": "active",
            "agents_loaded": list(self._agents.keys()),
            "total_agents": len(self._agent_classes),
            "metrics": self._metrics,
            "platform": "Atlas 7.0"
        }


# Singleton Instance
agent_orchestrator = AgentOrchestrator()
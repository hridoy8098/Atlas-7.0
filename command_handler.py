# backend/command_handler.py — Atlas 7.0 Agent Command Handler
# এটি AgentOrchestrator এর সাথে কানেক্ট করে

from typing import Dict, Any
from backend.agent.agent_orchestrator import agent_orchestrator
from backend.core.ai_engine import ai_engine
from backend.core.memory import memory_manager
from backend.core.language import language_detector
from backend.core.intent_classifier import classify_intent


def handle_agent_command(command: str, parsed: Dict) -> str:
    """
    Agent Orchestrator এর মাধ্যমে কমান্ড হ্যান্ডেল করে
    """
    intent = parsed.get('intent', '')
    entities = parsed.get('entities', {})
    original_command = command.strip()

    print(f"🤖 Agent Handler → Intent: {intent} | Command: {original_command}")

    # Orchestrator এ পাঠানো
    result = agent_orchestrator.execute(intent, entities, original_command)

    if result.get("success", False):
        message = result.get("message", "Command executed successfully.")
        return message
    else:
        # যদি কোনো Agent না মিলে তাহলে AI এর কাছে পাঠাবে
        return handle_ai_fallback(command)


def handle_ai_fallback(command: str) -> str:
    """AI দিয়ে সাধারণ উত্তর"""
    try:
        response = ai_engine.chat(
            f"User said: {command}\nBe helpful and practical.",
            system_prompt="You are Atlas, a helpful voice assistant. Reply in natural language only. Keep it concise, friendly, and practical."
        )
        return response
    except:
        return "দুঃখিত, এই কমান্ডটি এখনো প্রসেস করতে পারছি না।"


def is_agent_command(parsed: Dict) -> bool:
    """চেক করে এটা Agent এর কমান্ড কিনা"""
    if not parsed or 'intent' not in parsed:
        return False

    intent = parsed.get('intent', '').lower()
    command = parsed.get('original_command', '').lower() if 'original_command' in parsed else ""

    # All agent intents
    agent_intents = [
        # App
        "open_app", "app_open",
        # PC
        "pc_optimize", "pc_clean", "pc_shutdown", "pc_restart", "pc_lock", 
        "pc_sleep", "pc_battery", "pc_status", "pc_wifi", "pc_bluetooth",
        "process_manager", "startup_apps",
        # File
        "file_organize", "file_search", "file_create", "file_delete",
        "file_copy", "file_move", "file_rename", "file_backup",
        # Web
        "web_search", "web_research", "web_summarize", "web_translate",
        "web_bookmark", "web_history", "open_url", "open_website",
        # Media
        "media_youtube", "media_music", "media_video", "media_image",
        "media_meme", "media_download", "media_subtitle", "media_convert",
        "youtube", "play_youtube", "play_music", "generate_image", "generate_meme",
        # Productivity
        "productivity_task", "productivity_show_tasks", "productivity_pomodoro",
        "productivity_reminder", "productivity_calendar", "productivity_note",
        "productivity_alarm", "add_task", "new_task", "show_tasks", "pomodoro",
        "focus_mode", "task", "todo", "reminder",
        # Security
        "security_lock", "security_privacy", "security_breach", "security_password",
        "security_scan", "security_firewall", "privacy_mode", "enable_privacy",
        "check_breach",
        # Terminal
        "terminal_run", "terminal_git", "terminal_pip", "terminal_npm",
        "git_status", "git_pull", "git_push", "git_commit",
        "pip_install", "npm_install",
        # ML
        "ml_load", "ml_clean", "ml_analyze", "ml_classify", "ml_regress",
        "ml_nlp", "ml_auto", "ml_predict", "ml_models", "ml_delete",
        "ml_export", "ml_plot", "load_dataset", "clean_data", "analyze_data",
        "train_classifier", "train_regressor", "auto_ml", "predict",
        "list_models", "delete_model",
        # Browser
        "browser_open_url", "browser_search_web", "browser_click", "browser_type",
        "browser_type_password", "browser_scroll", "browser_fill_form", "browser_get_text",
        "browser_press_key", "browser_close", "browser_new_tab", "browser_switch_tab",
        "browser_go_back", "browser_go_forward", "browser_refresh",
        "browser_screenshot", "browser_smart_interact",
        # Action
        "action_browser_control", "action_code_helper", "action_computer_control",
        "action_computer_settings", "action_desktop", "action_dev_agent",
        "action_file_controller", "action_file_processor", "action_flight_finder",
        "action_game_updater", "action_open_app", "action_reminder",
        "action_web_search", "action_youtube_video",
        "voice_browser", "voice_computer", "voice_desktop", "voice_files",
        "voice_code", "voice_youtube", "voice_flights", "voice_games",
        "voice_reminder", "voice_search",
        # Automation
        "api_test", "bug_find", "clipboard", "doc_write",
        "file_organize_auto", "git_assist", "news_analyze", "price_track",
        "screen_auto", "social_monitor", "whatsapp_bot",
    ]

    # Check if intent is an agent intent
    if intent in agent_intents:
        return True

    # Fallback: check keywords in command
    agent_keywords = [
        "open", "youtube", "chrome", "vscode", "gmail", "github",
        "facebook", "whatsapp", "chatgpt", "spotify", "discord",
        "optimize", "clean", "boost", "speed", "tune",
        "shutdown", "restart", "lock", "sleep", "system status",
        "battery", "wifi", "bluetooth", "process", "startup",
        "organize", "downloads", "file", "folder", "search file",
        "research", "search google", "search web", "google",
        "summarize", "translate", "bookmark",
        "video", "music", "image", "meme", "download",
        "pomodoro", "task", "reminder", "calendar", "note", "alarm",
        "privacy", "breach", "password", "scan", "firewall",
        "terminal", "git", "pip", "npm", "run command",
        "weather", "time", "date", "news",
        "খোল", "চালু", "ফাস্ট", "পরিষ্কার", "শাটডাউন",
        "বন্ধ", "রিস্টার্ট", "লক", "ব্যাটারি", "ওয়াইফাই",
        "গোছাও", "ফাইল", "খুঁজ", "গান", "ভিডিও", "ছবি",
        "টাস্ক", "কাজ", "পোমোডোরো", "রিমাইন্ডার", "নোট",
        "প্রাইভেসি", "নিরাপত্তা", "টার্মিনাল", "আবহাওয়া", "সময়"
    ]

    return any(keyword in intent or keyword in command for keyword in agent_keywords)


def get_command_response(command: str) -> dict:
    """
    Main entry point for processing user commands
    """
    command = command.strip()
    if not command:
        return {"response": "কিছু বলুন...", "success": False}

    # Step 1: Classify intent using AI + fallback
    parsed = classify_intent(command)
    parsed['original_command'] = command

    # Step 2: Route to appropriate handler
    if is_agent_command(parsed):
        response_text = handle_agent_command(command, parsed)
    else:
        response_text = handle_ai_fallback(command)

    # Step 3: Save to memory
    try:
        memory_manager.add_to_short_term("user", command)
        memory_manager.add_to_short_term("assistant", response_text)
    except:
        pass

    # Step 4: Detect language
    try:
        lang = language_detector.detect(command)
    except:
        lang = "unknown"

    return {
        "response": response_text,
        "language": lang,
        "intent": parsed.get('intent', 'unknown'),
        "confidence": parsed.get('confidence', 0),
        "method": parsed.get('method', 'unknown'),
        "entities": parsed.get('entities', {}),
        "success": True
    }


def get_agent_status() -> Dict:
    """Agent System এর স্ট্যাটাস"""
    try:
        capabilities = agent_orchestrator.get_all_capabilities()
        agent_status = agent_orchestrator.get_agent_status()
        return {
            "status": "active",
            "agents_loaded": agent_status.get("agents_loaded", []),
            "total_agents": agent_status.get("total_agents", 0),
            "capabilities": capabilities,
            "platform": "Atlas 7.0"
        }
    except Exception as e:
        return {"status": "error", "message": f"Agent system not loaded: {str(e)}"}


print("✅ Agent Handler Loaded Successfully")
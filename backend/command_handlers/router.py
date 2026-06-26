"""
Atlas 7.0 — Command Router
Intelligent routing, intent chaining, fallback orchestration, batch processing.
"""

from typing import Dict, Any, List, Optional, Callable
import time
import re
from .base_handler import BaseCommandHandler, CommandResponse, CommandStatus


class CommandRouter:
    def __init__(self):
        self._handlers: Dict[str, BaseCommandHandler] = {}
        self._fallback_handlers: List[Callable] = []
        self._chaining_rules: Dict[str, List[str]] = {}
        self._intent_aliases: Dict[str, str] = {}
        self._metrics = {"total_routed": 0, "fallbacks": 0, "chains_executed": 0}

    def register(self, name: str, handler: BaseCommandHandler):
        self._handlers[name] = handler
        return self

    def unregister(self, name: str):
        return self._handlers.pop(name, None)

    def get(self, name: str) -> Optional[BaseCommandHandler]:
        return self._handlers.get(name)

    def list_handlers(self) -> List[str]:
        return list(self._handlers.keys())

    def add_fallback(self, handler: Callable):
        self._fallback_handlers.append(handler)

    def add_alias(self, alias: str, canonical: str):
        self._intent_aliases[alias] = canonical

    def add_chain(self, first_intent: str, chain: List[str]):
        self._chaining_rules[first_intent] = chain

    def _resolve_alias(self, intent: str) -> str:
        intent_lower = intent.lower().strip()
        return self._intent_aliases.get(intent_lower, intent)

    def _detect_handler_by_intent(self, intent: str) -> Optional[BaseCommandHandler]:
        intent_lower = intent.lower()

        for name, handler in self._handlers.items():
            if intent_lower in handler._handlers:
                return handler

        prefix_match = intent_lower.split("_")[0] if "_" in intent_lower else intent_lower
        bn_prefix_map = {
            "auth": "auth", "agent": "agent", "action": "action", "advanced": "advanced",
            "analytics": "analytics", "automation": "automation", "bangladesh": "bangladesh",
            "core": "core", "fun": "fun", "life": "life", "media": "media",
            "productivity": "productivity", "security": "security", "study": "study",
            "system": "system", "vision": "vision", "agent2": "agent2",
        }
        mapped = bn_prefix_map.get(prefix_match)
        if mapped and mapped in self._handlers:
            return self._handlers[mapped]

        for name, handler in self._handlers.items():
            caps = handler.get_capabilities()
            if any(intent_lower in c or c in intent_lower for c in caps):
                return handler

        return None

    def route(self, intent: str, entities: Dict, handler_hint: str = "") -> CommandResponse:
        self._metrics["total_routed"] += 1
        intent = self._resolve_alias(intent)

        if handler_hint and handler_hint in self._handlers:
            handler = self._handlers[handler_hint]
        else:
            handler = self._detect_handler_by_intent(intent)

        if not handler:
            for fb in self._fallback_handlers:
                try:
                    result = fb(intent, entities)
                    if result:
                        return result
                except Exception:
                    continue
            self._metrics["fallbacks"] += 1
            return CommandResponse.fail(
                message=f"No handler found for '{intent}' | '{intent}' এর জন্য কোনো হ্যান্ডলার নেই",
                action=intent, available_handlers=self.list_handlers()
            )

        result = handler.handle(intent, entities)

        if intent in self._chaining_rules:
            self._metrics["chains_executed"] += 1
            chain_results = [result]
            for next_intent in self._chaining_rules[intent]:
                chain_result = self.route(next_intent, entities)
                chain_results.append(chain_result)
            result.metadata["chain"] = [r.to_dict() for r in chain_results]

        return result

    def route_batch(self, commands: List[Dict]) -> List[CommandResponse]:
        return [self.route(cmd.get("intent", ""), cmd.get("entities", {}),
                           cmd.get("handler_hint", "")) for cmd in commands]

    def route_text(self, text: str, context: Dict = None) -> CommandResponse:
        from backend.core.intent_classifier import classify_intent
        parsed = classify_intent(text)
        intent = parsed.get("intent", "unknown")
        entities = parsed.get("entities", {})
        if context:
            entities["_context"] = context
        entities["_original_text"] = text
        return self.route(intent, entities)

    def get_metrics(self) -> Dict:
        return dict(self._metrics)


class BanglaCommandRouter(CommandRouter):
    def __init__(self):
        super().__init__()
        self._setup_bangla_aliases()

    def _setup_bangla_aliases(self):
        bn_aliases = {
            "পিন_ভেরিফাই": "pin_verify", "পিন_সেট": "pin_set", "পিন_চেঞ্জ": "pin_change",
            "ফেস_রেজিস্টার": "face_register", "ফেস_ভেরিফাই": "face_verify",
            "ভয়েস_রেজিস্টার": "voice_register", "ভয়েস_ভেরিফাই": "voice_verify",
            "লগইন": "login", "লগআউট": "logout", "সেশন_ক্রিয়েট": "session_create",
            "লক_স্ক্রিন": "lock_screen", "আনলক_স্ক্রিন": "unlock_screen",
            "ওয়েব_সার্চ": "web_search", "ওয়েব_রিসার্চ": "web_research",
            "ফাইল_সার্চ": "file_search", "ফাইল_ক্রিয়েট": "file_create",
            "ফাইল_ডিলিট": "file_delete", "ফাইল_মুভ": "file_move",
            "পিসি_অপটিমাইজ": "pc_optimize", "পিসি_ক্লিন": "pc_clean",
            "পিসি_শাটডাউন": "pc_shutdown", "পিসি_রিস্টার্ট": "pc_restart",
            "অ্যাপ_ওপেন": "app_open", "অ্যাপ_ক্লোজ": "app_close",
            "মিউজিক_প্লে": "music_play", "মিউজিক_স্টপ": "music_stop",
            "ভিডিও_ডাউনলোড": "video_download", "ইমেজ_জেনারেট": "image_generator",
            "মেম_জেনারেট": "meme_generator", "ক্যালকুলেট": "math_solver",
            "অনুবাদ": "web_translate", "সারাংশ": "ai_summarize",
            "নোট_নেওয়া": "productivity_note", "টাস্ক_যোগ": "add_task",
            "রিমাইন্ডার_সেট": "reminder_set", "ক্যাপসুল_ক্রিয়েট": "capsule_create",
            "ওয়ার্কআউট_লগ": "workout_log", "মুড_লগ": "mood_tracker_log",
            "স্লিপ_লগ": "sleep_log", "জার্নাল_লিখুন": "journal_write",
            "পিডিএফ_পড়ুন": "pdf_read", "ইমেইল_পাঠান": "email_send",
            "ক্যালেন্ডার_দেখুন": "calendar_view", "উপস্থাপনা_তৈরি": "presentation_create",
            "কোর্স_খুঁজুন": "youtube_ai_search", "ফ্ল্যাশকার্ড_তৈরি": "flashcard_create",
            "পরীক্ষা_প্রস্তুতি": "exam_prep", "নামাজের_সময়": "prayer_calendar_today",
            "শেয়ার_দর": "bd_stock_market", "মুদ্রা_রূপান্তর": "bd_currency_convert",
            "বাংলা_ওসিআর": "bangla_ocr", "নিউজ_দেখুন": "bd_news_top",
            "কিউআর_জেনারেট": "qr_generate", "ওসিআর_স্ক্যান": "ocr_scanner",
            "অবজেক্ট_ডিটেক্ট": "object_detect", "বডি_ল্যাঙ্গুয়েজ": "body_language_detect",
            "মালওয়্যার_স্ক্যান": "malware_scan", "ব্রিচ_চেক": "breach_check",
            "পাসওয়ার্ড_সেভ": "pwd_save", "পাসওয়ার্ড_জেনারেট": "pwd_generate",
            "ড্রিম_এনালাইজ": "dream_analyze", "ডিবেট_স্টার্ট": "debate_start",
            "কুইজ_স্টার্ট": "quiz_start", "ইন্টারভিউ_স্টার্ট": "interview_start",
            "গল্প_তৈরি": "story_create", "ভাষা_টিউটর": "language_tutor_lesson",
            "বিএমআই_ক্যালকুলেট": "bmi_calculate", "চোখের_বিশ্রাম": "eye_rest_start",
            "পোস্টার_চেক": "posture_check", "স্ট্রেস_চেক": "stress_check",
            "গেমিং_মোড": "gaming_mode_enable", "র‍্যাম_অপ্টিমাইজ": "ram_optimize",
            "স্টার্টআপ_লিস্ট": "startup_list", "ড্রাইভার_আপডেট": "driver_update",
            "স্পিড_টেস্ট": "internet_speed_test", "ডিস্ক_হেলথ": "disk_health_check",
            "অটোমেশন_এপিআই": "api_tester_run", "অটোমেশন_বাগ": "bug_finder_scan",
            "ক্লিপবোর্ড_পড়ুন": "clipboard_read", "হোয়াটসঅ্যাপ_পাঠান": "whatsapp_send",
            "প্ল্যানার_তৈরি": "planner_create", "এক্সিকিউটর_রান": "executor_run",
            "টাস্ক_কিউ_স্ট্যাটাস": "task_queue_status",
            # Browser commands
            "ব্রাউজার_খোল": "browser_open_url", "ওয়েবসাইট_খোল": "browser_open_url",
            "সাইট_খোল": "browser_open_url", "ইউআরএল_খোল": "browser_open_url",
            "গুগল_সার্চ": "browser_search_web", "ওয়েব_সার্চ": "browser_search_web",
            "অনলাইন_সার্চ": "browser_search_web",
            "ক্লিক": "browser_click", "বাটন_চাপ": "browser_click",
            "টাইপ": "browser_type", "লেখ": "browser_type",
            "পাসওয়ার্ড_দাও": "browser_type_password",
            "স্ক্রল": "browser_scroll", "নিচে_যাও": "browser_scroll", "উপরে_যাও": "browser_scroll",
            "ফর্ম_পূরণ": "browser_fill_form",
            "পেজ_পড়": "browser_get_text", "টেক্সট_দেখ": "browser_get_text",
            "এন্টার_চাপ": "browser_press_key", "কী_চাপ": "browser_press_key",
            "ব্রাউজার_বন্ধ": "browser_close", "ট্যাব_বন্ধ": "browser_close",
            "নতুন_ট্যাব": "browser_new_tab",
            "ট্যাব_সুইচ": "browser_switch_tab",
            "পিছনে_যাও": "browser_go_back", "পেছনে_যাও": "browser_go_back",
            "সামনে_যাও": "browser_go_forward",
            "রিফ্রেশ": "browser_refresh",
            "স্ক্রিনশট": "browser_screenshot", "ছবি_তুল": "browser_screenshot",
        }
        for bn, en in bn_aliases.items():
            self.add_alias(bn, en)


router = BanglaCommandRouter()

from typing import Dict, List
from pathlib import Path  # ← FIXED: moved to top
from .base_agent import BaseAgent
from backend.automation import (
    api_tester, bug_finder, clipboard_manager, doc_writer,
    file_organizer, git_assistant, news_analyzer, price_tracker,
    screen_automation, social_monitor, whatsapp_bot
)


class AutomationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Automation Agent",
            description="Automation tools: API testing, bug finding, clipboard, documents, file organize, git, news, price tracking, screen, social, WhatsApp"
        )

    def get_capabilities(self) -> List[str]:
        return [
            "api_test", "bug_find", "clipboard", "doc_write",
            "file_organize", "git_assist", "news_analyze", "price_track",
            "screen_auto", "social_monitor", "whatsapp"
        ]

    def handle(self, intent: str, entities: Dict) -> Dict:
        cmd = entities.get("original_command", "").lower()

        if "api" in intent or ("test" in cmd and "api" in cmd):
            url = entities.get("url", entities.get("query", ""))
            method = entities.get("method", "GET").upper()
            return api_tester.test_endpoint(url, method)

        if "bug" in intent or ("bug" in cmd or "review" in cmd):
            code = entities.get("code", entities.get("query", ""))
            lang = entities.get("language", "python")
            return bug_finder.analyze_code(code, lang)

        if "clipboard" in intent or ("clipboard" in cmd or "copy" in cmd or "paste" in cmd):
            if "paste" in cmd or " দেখ" in cmd:
                return clipboard_manager.paste()
            if "clear" in cmd or "মুছ" in cmd or "পরিষ্কার" in cmd:
                return clipboard_manager.clear()
            if "history" in cmd or "ইতিহাস" in cmd:
                return clipboard_manager.history()
            text = entities.get("text", entities.get("query", ""))
            if text:
                return clipboard_manager.copy(text)
            return clipboard_manager.paste()

        if "doc" in intent or ("write" in cmd or "document" in cmd or "generate" in cmd or "লেখ" in cmd):
            topic = entities.get("topic", entities.get("query", "untitled"))
            doc_type = entities.get("type", "general")
            return doc_writer.generate(topic, doc_type)

        if "organize" in intent or ("organize" in cmd or "arrange" in cmd or "clean" in cmd or "গোছাও" in cmd):
            folder = entities.get("folder", entities.get("path", ""))
            if not folder:
                folder = str(Path.home() / "Downloads")
            return file_organizer.organize(folder)

        if "git" in intent or ("git" in cmd or "commit" in cmd or "push" in cmd or "pull" in cmd):
            repo = entities.get("repo", entities.get("path", "."))
            if "commit" in cmd and "smart" not in cmd:
                msg = entities.get("message", entities.get("query", "Update"))
                return git_assistant.commit(msg, repo)
            if "smart" in cmd or "auto commit" in cmd:
                return git_assistant.smart_commit(repo)
            if "push" in cmd:
                return git_assistant.push(repo)
            if "pull" in cmd:
                return git_assistant.pull(repo)
            if "branch" in cmd or "branches" in cmd:
                return git_assistant.branch(repo)
            if "log" in cmd or "history" in cmd:
                return git_assistant.log(repo)
            return git_assistant.status(repo)

        if "news" in intent or ("news" in cmd or "headline" in cmd or "সংবাদ" in cmd):
            category = entities.get("category", "general")
            return news_analyzer.fetch_news(category)

        if "price" in intent or ("price" in cmd or "track" in cmd or "দাম" in cmd):
            name = entities.get("name", entities.get("query", ""))
            url = entities.get("url", "")
            if url:
                target = entities.get("target_price")
                target = float(target) if target else None
                return price_tracker.track_item(name, url, target)
            return price_tracker.get_all_items()

        if "screen" in intent or ("screenshot" in cmd or "screen" in cmd or "স্ক্রিনশট" in cmd or "স্ক্রিন" in cmd):
            if "ocr" in cmd or "text" in cmd or "লেখা" in cmd:
                return screen_automation.ocr_screen()
            return screen_automation.capture_screenshot()

        if "social" in intent or ("social" in cmd or "mention" in cmd or "সোশ্যাল" in cmd):
            keyword = entities.get("keyword", entities.get("query", ""))
            if keyword:
                return social_monitor.check_mentions(keyword)
            return social_monitor.get_analytics()

        if "whatsapp" in intent or ("whatsapp" in cmd or "wa" in cmd or "হোয়াটস" in cmd):
            msg = entities.get("message", entities.get("query", ""))
            recipient = entities.get("recipient", entities.get("contact", "Unknown"))
            if "auto reply" in cmd or "auto-reply" in cmd:
                enabled = "off" not in cmd and "disable" not in cmd and "বন্ধ" not in cmd
                return whatsapp_bot.set_auto_reply(enabled, msg)
            if msg:
                return whatsapp_bot.send_message(recipient, msg)
            return whatsapp_bot.get_logs()

        return {"success": False, "message": f"AutomationAgent: Cannot handle '{intent}'"}


automation_agent = AutomationAgent()
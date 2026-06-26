"""
Atlas 7.0 — Browser Command Handler (Playwright-powered)
Full browser automation: navigation, search, click, type, scroll, form fill, content reading.
"""

import re
import time
from urllib.parse import urlparse
from typing import Dict, Optional

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


_BN_MAP = {
    "open": "খোল", "browser": "ব্রাউজার", "search": "খুঁজ", "google": "গুগল",
    "youtube": "ইউটিউব", "facebook": "ফেসবুক", "website": "ওয়েবসাইট",
    "click": "ক্লিক", "type": "টাইপ", "scroll": "স্ক্রল", "press": "চাপ",
    "close": "বন্ধ", "tab": "ট্যাব", "back": "পিছনে", "forward": "সামনে",
    "refresh": "রিফ্রেশ", "download": "ডাউনলোড", "form": "ফর্ম",
    "fill": "পূরণ", "text": "টেক্সট", "read": "পড়", "extract": "এক্সট্র্যাক্ট",
    "url": "লিংক", "link": "লিংক", "button": "বাটন", "input": "ইনপুট",
    "password": "পাসওয়ার্ড", "email": "ইমেইল", "login": "লগইন",
}


class BrowserCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__(name="browser", description="Playwright-powered browser automation")
        self._register_all()

    def _register_all(self):
        self._register("browser_open_url", self.browser_open_url, priority=CommandPriority.HIGH)
        self._register("browser_search_web", self.browser_search_web, priority=CommandPriority.HIGH)
        self._register("browser_click", self.browser_click)
        self._register("browser_type", self.browser_type)
        self._register("browser_type_password", self.browser_type_password)
        self._register("browser_scroll", self.browser_scroll)
        self._register("browser_fill_form", self.browser_fill_form)
        self._register("browser_get_text", self.browser_get_text)
        self._register("browser_press_key", self.browser_press_key)
        self._register("browser_close", self.browser_close)
        self._register("browser_new_tab", self.browser_new_tab)
        self._register("browser_switch_tab", self.browser_switch_tab)
        self._register("browser_go_back", self.browser_go_back)
        self._register("browser_go_forward", self.browser_go_forward)
        self._register("browser_refresh", self.browser_refresh)
        self._register("browser_screenshot", self.browser_screenshot)
        self._register("browser_smart_interact", self.browser_smart_interact)

    # ─── helpers ──────────────────────────────────────────

    def _call_browser(self, action: str, **params) -> dict:
        try:
            from backend.action.browser_control import browser_control
            parameters = {"action": action, **params}
            result_text = browser_control(parameters)
            return {"success": True, "message": result_text}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _bilingual(self, en: str, bn: str = None) -> CommandResponse:
        if bn is None:
            bn = en
        return CommandResponse.ok(message=f"{en} | {bn}")

    def _bn_parse(self, text: str) -> str:
        for en_word, bn_word in _BN_MAP.items():
            text = re.sub(bn_word, en_word, text, flags=re.IGNORECASE)
        return text

    def _extract_url(self, text: str) -> Optional[str]:
        text = self._bn_parse(text)
        url_pattern = re.compile(r'(https?://[^\s]+)|(?:www\.[^\s]+)')
        match = url_pattern.search(text)
        if match:
            raw = match.group(0)
            if not raw.startswith("http"):
                raw = "https://" + raw
            return raw
        domain_pattern = re.compile(r'\b([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|bd|io|ai|app|dev|co|uk|ca|info)\b)')
        match = domain_pattern.search(text)
        if match:
            return "https://" + match.group(1)
        return None

    def _extract_query(self, text: str, remove_words: list = None) -> str:
        text = self._bn_parse(text)
        if remove_words:
            for word in remove_words:
                text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(search|find|look up|open|navigate|go to|browse|visit|show me|take me to)\b',
                      '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(for|about|on|regarding|related to)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[^\w\s.?!]', '', text).strip()
        return text

    def _extract_selector_type(self, text: str) -> str:
        text = text.lower()
        if any(w in text for w in ["button", "btn", "বাটন"]):
            return "button"
        if any(w in text for w in ["link", "লিংক"]):
            return "link"
        if any(w in text for w in ["input", "field", "textbox", "box", "ইনপুট"]):
            return "textbox"
        if any(w in text for w in ["search", "সার্চ"]):
            return "searchbox"
        if any(w in text for w in ["image", "img", "picture", "ছবি"]):
            return "img"
        return "text"

    def _browser_action(self, action: str, entities: dict, params: dict) -> CommandResponse:
        result = self._call_browser(action, **params)
        msg = result.get("message", f"Browser {action} completed")
        bn_msg = entities.get("_bn_message", msg)
        if result.get("success"):
            return CommandResponse.ok(message=f"{msg} | {bn_msg}", action=action, data=params)
        return CommandResponse.fail(
            message=f"Browser {action} failed: {result.get('message')}",
            action=action, data=params
        )

    # ─── 1. OPEN URL ───────────────────────────────────────

    def browser_open_url(self, entities: dict) -> CommandResponse:
        url = entities.get("url") or self._extract_url(entities.get("_raw", ""))
        if not url:
            return self._bilingual("Please provide a URL or website name | একটি URL বা ওয়েবসাইটের নাম দিন")

        known_sites = {
            "youtube": "https://youtube.com", "google": "https://google.com",
            "facebook": "https://facebook.com", "github": "https://github.com",
            "gmail": "https://mail.google.com", "chatgpt": "https://chatgpt.com",
            "reddit": "https://reddit.com", "twitter": "https://x.com",
            "x.com": "https://x.com", "instagram": "https://instagram.com",
            "linkedin": "https://linkedin.com", "amazon": "https://amazon.com",
            "netflix": "https://netflix.com", "spotify": "https://spotify.com",
            "stackoverflow": "https://stackoverflow.com", "wikipedia": "https://wikipedia.org",
            "whatsapp": "https://web.whatsapp.com", "telegram": "https://web.telegram.org",
            "discord": "https://discord.com", "medium": "https://medium.com",
        }
        domain = urlparse(url).netloc.lower().replace("www.", "") if url.startswith("http") else url.lower().strip()
        if domain in known_sites:
            url = known_sites[domain]
        elif not url.startswith("http"):
            url = "https://" + url

        result = self._call_browser("go_to", url=url)
        if result.get("success"):
            return CommandResponse.ok(
                message=f"Opened {url} | {url} খোলা হয়েছে",
                action="browser_open_url", data={"url": url}
            )
        return CommandResponse.fail(
            message=f"Could not open {url} | {url} খোলা সম্ভব হয়নি",
            action="browser_open_url", data={"url": url}
        )

    # ─── 2. SEARCH WEB ─────────────────────────────────────

    def browser_search_web(self, entities: dict) -> CommandResponse:
        query = entities.get("query") or entities.get("q") or self._extract_query(
            entities.get("_raw", ""), remove_words=["search", "google", "web"]
        )
        if not query:
            return self._bilingual("What should I search for? | কী সার্চ করব?")

        engine = entities.get("engine", "google")
        if engine not in ("google", "bing", "duckduckgo"):
            engine = "google"

        result = self._call_browser("search", query=query, engine=engine)
        if result.get("success"):
            return CommandResponse.ok(
                message=f"Searched {engine} for '{query}' | '{query}' এর জন্য {engine} এ সার্চ করা হয়েছে",
                action="browser_search_web", data={"query": query, "engine": engine}
            )
        return CommandResponse.fail(
            message=f"Search failed: {result.get('message')} | সার্চ ব্যর্থ হয়েছে",
            action="browser_search_web", data={"query": query}
        )

    # ─── 3. CLICK ──────────────────────────────────────────

    def browser_click(self, entities: dict) -> CommandResponse:
        selector = entities.get("selector")
        text = entities.get("text")
        description = entities.get("description") or self._extract_query(
            entities.get("_raw", ""), remove_words=["click", "press", "tap", "ক্লিক"]
        )

        if not selector and not text and not description:
            return self._bilingual("What should I click on? | কীসে ক্লিক করব?")

        if description and not text:
            text = description

        result = self._call_browser("click", selector=selector, text=text)
        if result.get("success"):
            target = text or selector or description
            return CommandResponse.ok(
                message=f"Clicked on '{target}' | '{target}' এ ক্লিক করা হয়েছে",
                action="browser_click", data={"selector": selector, "text": text}
            )
        return CommandResponse.fail(
            message=f"Could not click: {result.get('message')} | ক্লিক করা সম্ভব হয়নি",
            action="browser_click", data={"selector": selector, "text": text}
        )

    # ─── 4. TYPE TEXT ──────────────────────────────────────

    def browser_type(self, entities: dict) -> CommandResponse:
        selector = entities.get("selector")
        text = entities.get("text") or entities.get("value")
        description = entities.get("description", "")

        if not text:
            return self._bilingual("What text should I type? | কী টাইপ করব?")

        clear_first = entities.get("clear_first", True)

        result = self._call_browser("type", selector=selector, text=text, clear_first=clear_first)
        if result.get("success"):
            target = description or selector or "focused field"
            return CommandResponse.ok(
                message=f"Typed '{text[:50]}' into {target} | {target} এ '{text[:50]}' টাইপ করা হয়েছে",
                action="browser_type", data={"text": text, "selector": selector}
            )
        return CommandResponse.fail(
            message=f"Could not type: {result.get('message')} | টাইপ করা সম্ভব হয়নি",
            action="browser_type", data={"text": text, "selector": selector}
        )

    def browser_type_password(self, entities: dict) -> CommandResponse:
        selector = entities.get("selector")
        entities["text"] = "********"
        result = self._call_browser("type", selector=selector, text=entities.get("value", ""), clear_first=True)
        if result.get("success"):
            return CommandResponse.ok(
                message="Password entered securely | পাসওয়ার্ড নিরাপদে প্রবেশ করানো হয়েছে",
                action="browser_type_password"
            )
        return CommandResponse.fail(
            message=f"Could not type password: {result.get('message')}",
            action="browser_type_password"
        )

    # ─── 5. SCROLL ─────────────────────────────────────────

    def browser_scroll(self, entities: dict) -> CommandResponse:
        direction = entities.get("direction", "down")
        amount = entities.get("amount", 500)

        raw = entities.get("_raw", "").lower()
        if any(w in raw for w in ["up", "উপর"]):
            direction = "up"
        elif any(w in raw for w in ["down", "নিচ", "নীচ"]):
            direction = "down"
        if any(w in raw for w in ["bottom", "end", "শেষ", "সব"]):
            amount = 10000
        elif any(w in raw for w in ["top", "start", "beginning", "শুরু"]):
            direction = "up"
            amount = 10000
        elif any(w in raw for w in ["little", "tiny", "small", "একটু", "সামান্য"]):
            amount = 150

        result = self._call_browser("scroll", direction=direction, amount=amount)
        if result.get("success"):
            dir_bn = "উপর" if direction == "up" else "নিচ"
            return CommandResponse.ok(
                message=f"Scrolled {direction} | {dir_bn} দিকে স্ক্রল করা হয়েছে",
                action="browser_scroll", data={"direction": direction, "amount": amount}
            )
        return CommandResponse.fail(
            message=f"Could not scroll: {result.get('message')}",
            action="browser_scroll"
        )

    # ─── 6. FILL FORM ──────────────────────────────────────

    def browser_fill_form(self, entities: dict) -> CommandResponse:
        fields = entities.get("fields")
        if not fields or not isinstance(fields, dict):
            return self._bilingual("Please provide form fields to fill | ফর্ম ফিল করার জন্য ফিল্ড দিন")

        result = self._call_browser("fill_form", fields=fields)
        count = len(fields)
        if result.get("success"):
            return CommandResponse.ok(
                message=f"Filled {count} form field(s) | {count}টি ফর্ম ফিল্ড পূরণ করা হয়েছে",
                action="browser_fill_form", data={"filled": count}
            )
        failed_count = result.get("message", "").count("FAIL")
        return CommandResponse.fail(
            message=f"Filled {count - failed_count}/{count} fields. {result.get('message')}",
            action="browser_fill_form"
        )

    # ─── 7. GET PAGE TEXT ──────────────────────────────────

    def browser_get_text(self, entities: dict) -> CommandResponse:
        result = self._call_browser("get_text")
        if result.get("success"):
            text = result.get("message", "")
            preview = text[:500] + "..." if len(text) > 500 else text
            return CommandResponse.ok(
                message=f"Page content read ({len(text)} chars) | পেজের কন্টেন্ট পড়া হয়েছে",
                action="browser_get_text",
                data={"text": text, "preview": preview}
            )
        return CommandResponse.fail(
            message=f"Could not read page: {result.get('message')}",
            action="browser_get_text"
        )

    # ─── 8. PRESS KEY ──────────────────────────────────────

    def browser_press_key(self, entities: dict) -> CommandResponse:
        key = entities.get("key") or entities.get("keys")
        if not key:
            raw = entities.get("_raw", "").lower()
            key_map = {
                "enter": "Enter", "return": "Enter",
                "escape": "Escape", "esc": "Escape",
                "tab": "Tab",
                "space": "Space", "スペース": "Space",
                "delete": "Delete", "del": "Delete",
                "backspace": "Backspace",
                "arrow up": "ArrowUp", "up": "ArrowUp",
                "arrow down": "ArrowDown", "down": "ArrowDown",
                "arrow left": "ArrowLeft", "left": "ArrowLeft",
                "arrow right": "ArrowRight", "right": "ArrowRight",
                "home": "Home", "end": "End",
                "page up": "PageUp", "pageup": "PageUp",
                "page down": "PageDown", "pagedown": "PageDown",
                "f5": "F5", "refresh": "F5",
                "ctrl c": "Control+c", "copy": "Control+c",
                "ctrl v": "Control+v", "paste": "Control+v",
                "ctrl a": "Control+a", "select all": "Control+a",
                "ctrl s": "Control+s", "save": "Control+s",
                "ctrl z": "Control+z", "undo": "Control+z",
                "ctrl f": "Control+f", "find": "Control+f",
            }
            for alias, actual in key_map.items():
                if alias in raw:
                    key = actual
                    break
            if not key:
                return self._bilingual("Which key should I press? | কী প্রেস করব?")

        result = self._call_browser("press", key=key)
        if result.get("success"):
            return CommandResponse.ok(
                message=f"Pressed '{key}' | '{key}' প্রেস করা হয়েছে",
                action="browser_press_key", data={"key": key}
            )
        return CommandResponse.fail(
            message=f"Could not press key: {result.get('message')}",
            action="browser_press_key"
        )

    # ─── 9. CLOSE BROWSER ──────────────────────────────────

    def browser_close(self, entities: dict) -> CommandResponse:
        result = self._call_browser("close")
        if result.get("success"):
            return CommandResponse.ok(
                message="Browser closed | ব্রাউজার বন্ধ করা হয়েছে",
                action="browser_close"
            )
        return CommandResponse.fail(
            message=f"Could not close browser: {result.get('message')}",
            action="browser_close"
        )

    # ─── 10. NEW TAB ───────────────────────────────────────

    def browser_new_tab(self, entities: dict) -> CommandResponse:
        url = entities.get("url") or self._extract_url(entities.get("_raw", ""))
        result = self._call_browser("go_to", url=url) if url else self._call_browser("press", key="Control+t")
        if result.get("success"):
            msg = f"New tab opened{' for ' + url if url else ''} | নতুন ট্যাব খোলা হয়েছে"
            return CommandResponse.ok(message=msg, action="browser_new_tab")
        return CommandResponse.fail(
            message=f"Could not open new tab: {result.get('message')}",
            action="browser_new_tab"
        )

    # ─── 11. SWITCH TAB ────────────────────────────────────

    def browser_switch_tab(self, entities: dict) -> CommandResponse:
        index = entities.get("index")
        direction = entities.get("direction", "next")
        raw = entities.get("_raw", "").lower()
        if any(w in raw for w in ["previous", "prev", "back", "আগের", "পেছনে"]):
            direction = "previous"
        key = "Control+Tab" if direction == "next" else "Control+Shift+Tab"
        if index is not None:
            for _ in range(index):
                self._call_browser("press", key="Control+Tab")
            msg = f"Switched to tab {index} | ট্যাব {index} এ সুইচ করা হয়েছে"
        else:
            self._call_browser("press", key=key)
            msg = f"Switched to {direction} tab | পরবর্তী ট্যাবে সুইচ করা হয়েছে"
        return CommandResponse.ok(message=msg, action="browser_switch_tab")

    # ─── 12. GO BACK / FORWARD ─────────────────────────────

    def browser_go_back(self, entities: dict) -> CommandResponse:
        result = self._call_browser("press", key="Alt+ArrowLeft")
        return CommandResponse.ok(
            message="Went back | পিছনে যাওয়া হয়েছে",
            action="browser_go_back"
        )

    def browser_go_forward(self, entities: dict) -> CommandResponse:
        result = self._call_browser("press", key="Alt+ArrowRight")
        return CommandResponse.ok(
            message="Went forward | সামনে যাওয়া হয়েছে",
            action="browser_go_forward"
        )

    # ─── 13. REFRESH ───────────────────────────────────────

    def browser_refresh(self, entities: dict) -> CommandResponse:
        result = self._call_browser("press", key="F5")
        return CommandResponse.ok(
            message="Page refreshed | পেজ রিফ্রেশ করা হয়েছে",
            action="browser_refresh"
        )

    # ─── 14. SCREENSHOT ────────────────────────────────────

    def browser_screenshot(self, entities: dict) -> CommandResponse:
        path = entities.get("path", f"browser_screenshot_{int(time.time())}.png")
        try:
            from backend.action.browser_control import _bt
            _bt.run(_bt._get_page())
            page = _bt.run(_bt._get_page())
            import asyncio
            coro = page.screenshot(path=path)
            future = asyncio.run_coroutine_threadsafe(coro, _bt._loop)
            future.result(timeout=15)
            return CommandResponse.ok(
                message=f"Screenshot saved: {path} | স্ক্রিনশট সংরক্ষিত: {path}",
                action="browser_screenshot", data={"path": path}
            )
        except Exception as e:
            return CommandResponse.fail(
                message=f"Screenshot failed: {str(e)} | স্ক্রিনশট নেওয়া সম্ভব হয়নি",
                action="browser_screenshot"
            )

    # ─── 15. SMART INTERACT (click or type by description) ──

    def browser_smart_interact(self, entities: dict) -> CommandResponse:
        action = entities.get("action", "click")
        description = entities.get("description") or entities.get("text") or self._extract_query(
            entities.get("_raw", ""),
            remove_words=["click on", "type in", "find", "locate", "interact with"]
        )
        text = entities.get("value") or entities.get("text_to_type")

        if not description:
            return self._bilingual("What element should I interact with? | কোন এলিমেন্টে ইন্টারঅ্যাক্ট করব?")

        if action == "type" and text:
            result = self._call_browser("smart_type", description=description, text=text)
            msg = f"Typed into '{description}' | '{description}' এ টাইপ করা হয়েছে"
        elif action == "click":
            result = self._call_browser("smart_click", description=description)
            msg = f"Clicked on '{description}' | '{description}' এ ক্লিক করা হয়েছে"
        else:
            result = self._call_browser("smart_click", description=description)
            msg = f"Interacted with '{description}' | '{description}' এর সাথে ইন্টারঅ্যাক্ট করা হয়েছে"

        if result.get("success"):
            return CommandResponse.ok(message=msg, action="browser_smart_interact",
                                      data={"description": description, "action": action})
        return CommandResponse.fail(
            message=f"Could not interact: {result.get('message')}",
            action="browser_smart_interact"
        )

    # ─── capabilities ──────────────────────────────────────

    def get_capabilities(self):
        return [
            "browser_open_url", "browser_search_web", "browser_click", "browser_type",
            "browser_scroll", "browser_fill_form", "browser_get_text", "browser_press_key",
            "browser_close", "browser_new_tab", "browser_switch_tab",
            "browser_go_back", "browser_go_forward", "browser_refresh",
            "browser_screenshot", "browser_smart_interact",
        ]

    def get_description(self):
        return (
            "Browser automation via Playwright. Open URLs, search web, click elements, "
            "type text, scroll, fill forms, read page content, press keys, manage tabs. "
            "Supports both English and Bengali commands. "
            "ব্রাউজার অটোমেশন: URL খোলা, সার্চ, ক্লিক, টাইপ, স্ক্রল, ফর্ম ফিল, পেজ পড়া, ট্যাব ম্যানেজমেন্ট।"
        )

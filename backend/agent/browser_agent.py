from typing import Dict, List
from .base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    """Playwright-powered browser automation agent"""

    def __init__(self):
        super().__init__(
            name="Browser Agent",
            description="Playwright browser automation: open URLs, search, click, type, scroll, fill forms, read pages, manage tabs"
        )
        self._handler = None

    def _get_handler(self):
        if self._handler is None:
            from backend.command_handlers.browser_commands import BrowserCommandHandler
            self._handler = BrowserCommandHandler()
        return self._handler

    def get_capabilities(self) -> List[str]:
        return [
            "browser_open_url", "browser_search_web", "browser_click", "browser_type",
            "browser_type_password", "browser_scroll", "browser_fill_form", "browser_get_text",
            "browser_press_key", "browser_close", "browser_new_tab", "browser_switch_tab",
            "browser_go_back", "browser_go_forward", "browser_refresh",
            "browser_screenshot", "browser_smart_interact",
        ]

    def handle(self, intent: str, entities: Dict) -> Dict:
        handler = self._get_handler()
        result = handler.handle(intent, entities)
        return {
            "success": result.success,
            "message": result.message,
            "action": result.action,
            "data": result.data,
        }

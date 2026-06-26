"""
Atlas 7.0 — Integration Bridge
Connects command_handlers to server.py, agent_orchestrator.py, and command_handler.py.
"""

from typing import Dict, Any, Optional, Callable
import sys
import os
import threading
import traceback

from .router import router
from .base_handler import CommandResponse
from .middleware import LoggingMiddleware, RateLimitMiddleware, InputSanitizerMiddleware


class CommandHandlerBridge:
    def __init__(self):
        self._initialized = False
        self._external_handlers = {}
        self._preprocessors: list = []
        self._postprocessors: list = []

    def init(self, auto_register_middleware: bool = True):
        if self._initialized:
            return
        if auto_register_middleware:
            router.add_fallback(self._ai_fallback)
        self._initialized = True
        print(f"  CommandHandlerBridge ready | {len(router.list_handlers())} handlers loaded")

    def register_external(self, name: str, handler_fn: Callable):
        self._external_handlers[name] = handler_fn

    def add_preprocessor(self, fn: Callable):
        self._preprocessors.append(fn)

    def add_postprocessor(self, fn: Callable):
        self._postprocessors.append(fn)

    def _ai_fallback(self, intent: str, entities: Dict) -> Optional[CommandResponse]:
        try:
            from backend.core.ai_engine import ai_engine
            text = entities.get("_original_text", intent)
            response = ai_engine.chat(
                f"User said: {text}\nBe helpful and practical.",
                system_prompt="You are Atlas, a helpful AI assistant. Reply naturally."
            )
            return CommandResponse.ok(message=str(response), action="ai_fallback", source="ai")
        except Exception as e:
            return CommandResponse.fail(
                message=f"Could not process command | কমান্ড প্রসেস করা যায়নি: {str(e)}",
                action="fallback"
            )

    def process(self, text: str, context: Dict = None) -> Dict:
        for pp in self._preprocessors:
            try:
                result = pp(text, context)
                if result:
                    return result
            except Exception:
                continue

        response = router.route_text(text, context)

        for pp in self._postprocessors:
            try:
                result = pp(response)
                if result:
                    response = result
            except Exception:
                continue

        return response.to_dict()

    def process_intent(self, intent: str, entities: Dict, handler_hint: str = "") -> Dict:
        response = router.route(intent, entities, handler_hint)
        return response.to_dict()

    def speak_response(self, response_dict: Dict, lang: str = "en"):
        try:
            text = response_dict.get("message", "")
            if text:
                from backend.core.voice_output import voice_output
                threading.Thread(target=voice_output.speak, args=(text, lang), daemon=True).start()
        except Exception:
            pass

    def save_to_memory(self, command: str, response: Dict):
        try:
            from backend.core.memory import memory_manager
            memory_manager.add_to_short_term("user", command)
            memory_manager.add_to_short_term("assistant", response.get("message", ""))
        except Exception:
            pass

    def get_status(self) -> Dict:
        return {
            "initialized": self._initialized,
            "handlers": router.list_handlers(),
            "metrics": router.get_metrics(),
            "total_handlers": len(router.list_handlers()),
        }


bridge = CommandHandlerBridge()


def patch_command_handler():
    """
    Patches the existing command_handler.py get_command_response function
    to use the new command_handlers system.
    """
    import command_handler as ch

    original_fn = ch.get_command_response

    def patched_get_command_response(command: str) -> dict:
        try:
            if not bridge._initialized:
                bridge.init()
            result = bridge.process(command)
            try:
                lang = "en"
                from backend.core.language import language_detector
                lang = language_detector.detect(command)
                result["language"] = lang
            except Exception:
                result["language"] = "en"
            result["method"] = "command_handlers"
            bridge.save_to_memory(command, result)
            if result.get("success"):
                bridge.speak_response(result, result.get("language", "en"))
            return result
        except Exception as e:
            traceback.print_exc()
            return original_fn(command)

    ch.get_command_response = patched_get_command_response
    print("  patched command_handler.get_command_response ")


def patch_server_py():
    """
    Patches server.py to route /api/command through command_handlers
    """
    try:
        import server as srv

        original_cmd = srv.take_command

        async def patched_take_command(req):
            try:
                if not bridge._initialized:
                    bridge.init()
                command = req.command.strip()
                if not command:
                    return {"response": None}
                print(f"  User: {command}")
                result = bridge.process(command)
                response_text = result.get("message", "")
                lang = result.get("language", "en")
                if response_text:
                    print(f"  Atlas: {str(response_text)[:100]}")
                    bridge.speak_response(result, lang)
                return {
                    "response": response_text,
                    "language": lang,
                    "intent": result.get("action", "unknown"),
                    "confidence": result.get("confidence", 0),
                    "method": "command_handlers",
                    "entities": result.get("data", {}),
                }
            except Exception as e:
                traceback.print_exc()
                return await original_cmd(req)

        srv.take_command = patched_take_command
        print("  patched server.take_command ")
    except Exception as e:
        print(f"  server.py patch skipped: {e}")

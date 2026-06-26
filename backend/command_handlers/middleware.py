"""
Atlas 7.0 — Middleware Pipeline
Authentication, logging, rate-limiting, caching, input sanitization.
"""

from typing import Dict, Any, Optional
import time
import hashlib
import json
from .base_handler import BaseMiddleware, MiddlewareResult, CommandResponse


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        self.logs = []

    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        entry = {"time": time.time(), "handler": handler_name, "intent": intent,
                 "entities": {k: v for k, v in entities.items() if not isinstance(v, (bytes, bytearray))}}
        self.logs.append(entry)
        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]
        print(f"  [{handler_name}] intent={intent} entities={str(list(entities.keys()))}")
        return MiddlewareResult(allowed=True)

    def after(self, handler_name: str, intent: str, entities: Dict, response: CommandResponse) -> CommandResponse:
        if self.logs:
            self.logs[-1]["success"] = response.success
            self.logs[-1]["action"] = response.action
        return response


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, max_per_minute: int = 60, max_per_second: int = 5):
        self.max_per_minute = max_per_minute
        self.max_per_second = max_per_second
        self.minute_bucket: Dict[str, list] = {}
        self.second_bucket: Dict[str, list] = {}

    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        now = time.time()
        key = f"{handler_name}:{intent}"

        if key not in self.second_bucket:
            self.second_bucket[key] = []
        self.second_bucket[key] = [t for t in self.second_bucket[key] if now - t < 1]
        if len(self.second_bucket[key]) >= self.max_per_second:
            return MiddlewareResult(allowed=False, response=CommandResponse.fail(
                message=f"Rate limited (per-second) | সেকেন্ডে বেশি রিকোয়েস্ট", action=intent))

        if key not in self.minute_bucket:
            self.minute_bucket[key] = []
        self.minute_bucket[key] = [t for t in self.minute_bucket[key] if now - t < 60]
        if len(self.minute_bucket[key]) >= self.max_per_minute:
            return MiddlewareResult(allowed=False, response=CommandResponse.fail(
                message=f"Rate limited (per-minute) | মিনিটে বেশি রিকোয়েস্ট", action=intent))

        self.second_bucket[key].append(now)
        self.minute_bucket[key].append(now)
        return MiddlewareResult(allowed=True)


class InputSanitizerMiddleware(BaseMiddleware):
    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        sanitized = {}
        for k, v in entities.items():
            if isinstance(v, str):
                v = v.strip()
                if len(v) > 10000:
                    v = v[:10000]
            sanitized[k] = v
        return MiddlewareResult(allowed=True, modified_entities=sanitized)


class ResponseCacheMiddleware(BaseMiddleware):
    def __init__(self, ttl_seconds: int = 5):
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl_seconds

    def _make_key(self, handler: str, intent: str, entities: Dict) -> str:
        raw = f"{handler}:{intent}:{json.dumps(entities, sort_keys=True, default=str)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        key = self._make_key(handler_name, intent, entities)
        if key in self.cache:
            resp, ts = self.cache[key]
            if time.time() - ts < self.ttl:
                resp.metadata["cached"] = True
                return MiddlewareResult(allowed=False, response=resp)
        return MiddlewareResult(allowed=True)

    def after(self, handler_name: str, intent: str, entities: Dict, response: CommandResponse) -> CommandResponse:
        key = self._make_key(handler_name, intent, entities)
        if response.success:
            self.cache[key] = (response, time.time())
        return response


class AuthMiddleware(BaseMiddleware):
    def __init__(self, required_session: bool = False, required_intents: list = None):
        self.required_session = required_session
        self.required_intents = required_intents or []

    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        if intent in self.required_intents:
            session_token = entities.get("session_token") or entities.get("token")
            if self.required_session and not session_token:
                return MiddlewareResult(allowed=False, response=CommandResponse.fail(
                    message="Authentication required | অথেনটিকেশন প্রয়োজন", action=intent))
        return MiddlewareResult(allowed=True)


class ValidationMiddleware(BaseMiddleware):
    def __init__(self, schema: Dict[str, type] = None):
        self.schema = schema or {}

    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        for field, expected_type in self.schema.items():
            if field in entities:
                val = entities[field]
                if not isinstance(val, expected_type):
                    return MiddlewareResult(allowed=False, response=CommandResponse.fail(
                        message=f"'{field}' must be {expected_type.__name__}", action=intent))
        return MiddlewareResult(allowed=True)

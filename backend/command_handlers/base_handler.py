"""
Atlas 7.0 — Command Handler Base Framework
Abstract base class, middleware stack, decorators, and utilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional, Coroutine
from functools import wraps
import time
import inspect
import traceback
from enum import Enum


class CommandPriority(Enum):
    LOW = 0
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class CommandStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    PENDING = "pending"
    RUNNING = "running"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"
    NOT_FOUND = "not_found"
    INVALID = "invalid"


class CommandResponse:
    def __init__(self, success: bool = True, message: str = "", action: str = "",
                 status: CommandStatus = CommandStatus.SUCCESS, **kwargs):
        self.success = success
        self.message = message
        self.action = action
        self.status = status
        self.data = kwargs
        self.timestamp = time.time()
        self.metadata = {}

    def to_dict(self) -> Dict:
        base = {
            "success": self.success,
            "message": self.message,
            "action": self.action,
            "status": self.status.value,
            "timestamp": self.timestamp,
        }
        base.update(self.data)
        if self.metadata:
            base["_metadata"] = self.metadata
        return base

    @classmethod
    def ok(cls, message: str = "", action: str = "", **kwargs) -> "CommandResponse":
        return cls(success=True, message=message, action=action, **kwargs)

    @classmethod
    def fail(cls, message: str = "", action: str = "", **kwargs) -> "CommandResponse":
        return cls(success=False, message=message, action=action, status=CommandStatus.FAILURE, **kwargs)

    @classmethod
    def error(cls, message: str = "", action: str = "", exc: Exception = None, **kwargs) -> "CommandResponse":
        resp = cls(success=False, message=message or str(exc) or "Unknown error",
                   action=action, status=CommandStatus.ERROR, **kwargs)
        if exc:
            resp.metadata["error_type"] = type(exc).__name__
            resp.metadata["traceback"] = traceback.format_exc()
        return resp


class MiddlewareResult:
    def __init__(self, allowed: bool = True, response: Optional[CommandResponse] = None, modified_entities: Dict = None):
        self.allowed = allowed
        self.response = response
        self.modified_entities = modified_entities or {}


class BaseMiddleware(ABC):
    @abstractmethod
    def before(self, handler_name: str, intent: str, entities: Dict) -> MiddlewareResult:
        pass

    def after(self, handler_name: str, intent: str, entities: Dict, response: CommandResponse) -> CommandResponse:
        return response

    def on_error(self, handler_name: str, intent: str, entities: Dict, error: Exception) -> CommandResponse:
        return CommandResponse.error(message=f"Middleware error: {str(error)}", action=intent, exc=error)


def validate_required(*fields: str):
    """Decorator: validate required fields exist in entities"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, entities: Dict, *args, **kwargs):
            missing = [f for f in fields if not entities.get(f)]
            if missing:
                bn_names = {"query": "কোয়েরি", "path": "পাথ", "name": "নাম", "url": "URL",
                            "email": "ইমেইল", "password": "পাসওয়ার্ড", "command": "কমান্ড",
                            "message": "মেসেজ", "title": "টাইটেল", "content": "কন্টেন্ট",
                            "text": "টেক্সট", "file": "ফাইল", "image": "ছবি", "audio": "অডিও",
                            "video": "ভিডিও", "source": "সোর্স", "target": "টার্গেট"}
                en_msg = f"Required: {', '.join(missing)}"
                bn_msg = f"প্রয়োজনীয়: {', '.join(bn_names.get(f, f) for f in missing)}"
                return CommandResponse.fail(message=f"{en_msg} | {bn_msg}", action=func.__name__,
                                            missing_fields=missing)
            return func(self, entities, *args, **kwargs)
        return wrapper
    return decorator


def validate_range(field: str, min_val: float, max_val: float):
    """Decorator: validate numeric field range"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, entities: Dict, *args, **kwargs):
            val = entities.get(field)
            if val is not None and (val < min_val or val > max_val):
                return CommandResponse.fail(
                    message=f"{field} must be {min_val}-{max_val}",
                    action=func.__name__, field=field, value=val
                )
            return func(self, entities, *args, **kwargs)
        return wrapper
    return decorator


def validate_one_of(field: str, choices: List[str]):
    """Decorator: validate field is one of allowed values"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, entities: Dict, *args, **kwargs):
            val = entities.get(field)
            if val and val not in choices:
                return CommandResponse.fail(
                    message=f"{field} must be one of: {', '.join(choices)}",
                    action=func.__name__, field=field, value=val, allowed=choices
                )
            return func(self, entities, *args, **kwargs)
        return wrapper
    return decorator


def timed(func: Callable):
    """Decorator: track execution time"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        result = func(self, *args, **kwargs)
        elapsed = round((time.time() - start) * 1000, 2)
        if isinstance(result, CommandResponse):
            result.metadata["execution_ms"] = elapsed
        return result
    return wrapper


def safe_execute(func: Callable):
    """Decorator: catch all exceptions gracefully"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            handler_name = getattr(self, 'name', 'Unknown')
            return CommandResponse.error(
                message=f"{handler_name} error: {str(e)}",
                action=func.__name__, exc=e
            )
    return wrapper


def bilingual_response(en_msg: str, bn_msg: str, **kwargs):
    """Create bilingual response"""
    return CommandResponse.ok(message=f"{en_msg} | {bn_msg}", **kwargs)


class BaseCommandHandler(ABC):
    def __init__(self, name: str = "unnamed", description: str = ""):
        self.name = name
        self.description = description
        self._handlers: Dict[str, Callable] = {}
        self._middleware: List[BaseMiddleware] = []
        self._metrics = {"total_calls": 0, "errors": 0, "total_time_ms": 0, "by_intent": {}}
        self._register_all_methods()

    def _register_all_methods(self):
        for attr_name in dir(self):
            if attr_name.startswith("handle_"):
                intent_name = attr_name[len("handle_"):].replace("_", "_")
                method = getattr(self, attr_name)
                if callable(method):
                    self._handlers[intent_name] = method

    def register_handler(self, intent: str, func: Callable):
        self._handlers[intent] = func

    def add_middleware(self, mw: BaseMiddleware):
        self._middleware.append(mw)

    def get_metrics(self) -> Dict:
        metrics = dict(self._metrics)
        metrics["avg_time_ms"] = round(self._metrics["total_time_ms"] / max(self._metrics["total_calls"], 1), 2)
        return metrics

    def _run_middleware_before(self, intent: str, entities: Dict) -> MiddlewareResult:
        modified = dict(entities)
        for mw in self._middleware:
            result = mw.before(self.name, intent, modified)
            if not result.allowed:
                return result
            if result.modified_entities:
                modified.update(result.modified_entities)
        return MiddlewareResult(allowed=True, modified_entities=modified)

    def _run_middleware_after(self, intent: str, entities: Dict, response: CommandResponse) -> CommandResponse:
        for mw in reversed(self._middleware):
            response = mw.after(self.name, intent, entities, response)
        return response

    @safe_execute
    def handle(self, intent: str, entities: Dict) -> CommandResponse:
        start = time.time()
        self._metrics["total_calls"] += 1

        intent_key = intent.replace(" ", "_").lower()
        handler = self._handlers.get(intent_key)

        if not handler:
            handler = self._handlers.get(intent)
        if not handler:
            self._metrics["errors"] += 1
            return CommandResponse.fail(
                message=f"{self.name} cannot handle '{intent}' | {self.name} '{intent}' হ্যান্ডেল করতে পারে না",
                action=intent, available_intents=list(self._handlers.keys())
            )

        mw_result = self._run_middleware_before(intent_key, entities)
        if not mw_result.allowed:
            return mw_result.response or CommandResponse.fail(
                message="Request blocked by middleware", action=intent_key
            )

        try:
            result = handler(mw_result.modified_entities or entities)
            if not isinstance(result, CommandResponse):
                if isinstance(result, dict):
                    result = CommandResponse(**result)
                else:
                    result = CommandResponse.ok(message=str(result))
        except Exception as e:
            self._metrics["errors"] += 1
            for mw in self._middleware:
                result = mw.on_error(self.name, intent_key, entities, e)
                break
            else:
                result = CommandResponse.error(message=f"Handler error: {str(e)}", action=intent_key, exc=e)

        result = self._run_middleware_after(intent_key, entities, result)
        elapsed = time.time() - start
        self._metrics["total_time_ms"] += elapsed
        if intent_key not in self._metrics["by_intent"]:
            self._metrics["by_intent"][intent_key] = {"calls": 0, "errors": 0, "total_time_ms": 0}
        self._metrics["by_intent"][intent_key]["calls"] += 1
        if not result.success:
            self._metrics["by_intent"][intent_key]["errors"] += 1
        self._metrics["by_intent"][intent_key]["total_time_ms"] += elapsed

        return result

    def handle_batch(self, commands: List[Dict]) -> List[CommandResponse]:
        return [self.handle(cmd.get("intent", ""), cmd.get("entities", {})) for cmd in commands]

    def _register(self, intent: str, func: Callable, priority: CommandPriority = CommandPriority.NORMAL):
        self.register_handler(intent, func)

    def _bilingual(self, en: str, bn: str = None) -> CommandResponse:
        if bn is None:
            bn = en
        return CommandResponse.ok(message=f"{en} | {bn}")

    def _error(self, action: str, message: str, entities: dict = None) -> CommandResponse:
        return CommandResponse.fail(message=message, action=action)

    def get_capabilities(self) -> List[str]:
        return list(self._handlers.keys())

    def get_description(self) -> str:
        return self.description or f"{self.name} command handler"

"""
Atlas 7.0 — Command Handler Registry & Auto-Loader
"""

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority, CommandStatus
from .middleware import (LoggingMiddleware, RateLimitMiddleware, InputSanitizerMiddleware,
                         ResponseCacheMiddleware, AuthMiddleware, ValidationMiddleware)
from .router import router, BanglaCommandRouter, CommandRouter
from .integration import bridge, CommandHandlerBridge, patch_command_handler, patch_server_py

# Import all handlers for registration
from .auth_commands import AuthCommandHandler
from .agent_commands import AgentCommandHandler
from .action_commands import ActionCommandHandler
from .advanced_commands import AdvancedCommandHandler
from .analytics_commands import AnalyticsCommandHandler
from .automation_commands import AutomationCommandHandler
from .bangladesh_commands import BangladeshCommandHandler
from .core_commands import CoreCommandHandler
from .fun_commands import FunCommandHandler
from .life_commands import LifeCommandHandler
from .media_commands import MediaCommandHandler
from .productivity_commands import ProductivityCommandHandler
from .security_commands import SecurityCommandHandler
from .study_commands import StudyCommandHandler
from .system_commands import SystemCommandHandler
from .vision_commands import VisionCommandHandler
from .agent2_commands import Agent2CommandHandler
from .browser_commands import BrowserCommandHandler


def initialize(apply_patches: bool = False):
    """
    Initialize all command handlers with middleware and register to router.
    """
    logging_mw = LoggingMiddleware()
    sanitizer_mw = InputSanitizerMiddleware()
    rate_limit_mw = RateLimitMiddleware(max_per_minute=120, max_per_second=10)

    handlers = {
        "auth": AuthCommandHandler(),
        "agent": AgentCommandHandler(),
        "action": ActionCommandHandler(),
        "advanced": AdvancedCommandHandler(),
        "analytics": AnalyticsCommandHandler(),
        "automation": AutomationCommandHandler(),
        "bangladesh": BangladeshCommandHandler(),
        "core": CoreCommandHandler(),
        "fun": FunCommandHandler(),
        "life": LifeCommandHandler(),
        "media": MediaCommandHandler(),
        "productivity": ProductivityCommandHandler(),
        "security": SecurityCommandHandler(),
        "study": StudyCommandHandler(),
        "system": SystemCommandHandler(),
        "vision": VisionCommandHandler(),
        "agent2": Agent2CommandHandler(),
        "browser": BrowserCommandHandler(),
    }

    for name, handler in handlers.items():
        handler.add_middleware(logging_mw)
        handler.add_middleware(sanitizer_mw)
        handler.add_middleware(rate_limit_mw)
        router.register(name, handler)

    bridge.init()
    print(f"  Command Handlers: {len(handlers)} modules, "
          f"{sum(len(h.get_capabilities()) for h in handlers.values())} total intents registered")

    if apply_patches:
        patch_command_handler()
        patch_server_py()
        print("  Patches applied to command_handler.py & server.py")

    return router


__all__ = [
    "BaseCommandHandler", "CommandResponse", "CommandPriority", "CommandStatus",
    "LoggingMiddleware", "RateLimitMiddleware", "InputSanitizerMiddleware",
    "ResponseCacheMiddleware", "AuthMiddleware", "ValidationMiddleware",
    "router", "BanglaCommandRouter", "CommandRouter",
    "bridge", "CommandHandlerBridge", "patch_command_handler", "patch_server_py",
    "initialize", "BrowserCommandHandler",
]

initialize(apply_patches=False)

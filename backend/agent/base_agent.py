from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from functools import wraps
import time


def safe_execute(func):
    """Decorator for automatic error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            agent_name = getattr(args[0], 'name', 'Unknown') if args else 'Unknown'
            return {
                "success": False,
                "message": f"❌ {agent_name} error: {str(e)}",
                "error_type": type(e).__name__
            }
    return wrapper


class BaseAgent(ABC):
    """সব Agent-এর Base Class — Fixed Version"""
    
    def __init__(self, name: str, description: str = "", ai_engine=None):
        self.name = name
        self.description = description
        self.ai = ai_engine  # ← FIXED: dependency injection instead of hard import
        self._handlers = {}  # ← NEW: intent-to-method registry
        self._metrics = {"total_calls": 0, "errors": 0, "avg_time": 0.0}

    def register(self, intent: str):
        """Decorator to register intent handlers"""
        def decorator(func):
            self._handlers[intent] = func
            return func
        return decorator

    def think(self, task: str, context: Dict = None) -> str:
        """AI দিয়ে intelligent decision — FIXED: sync version"""
        if not self.ai:
            return "AI engine not available"
        
        prompt = f"""You are the {self.name} Agent of Atlas 7.0.
Your job: {self.description}

Task: {task}
Context: {context or 'No additional context'}

Return only the best action in clear, concise format."""
        
        try:
            # Try sync first, fallback to async if needed
            if hasattr(self.ai, 'chat'):
                return self.ai.chat(prompt)
            return "AI response unavailable"
        except Exception as e:
            return f"Thinking error: {str(e)}"

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass

    @safe_execute  # ← NEW: automatic error handling
    def handle(self, intent: str, entities: Dict) -> Dict:
        """Default handler with registry support"""
        # Try registered handler first
        handler = self._handlers.get(intent)
        if handler:
            return handler(entities)
        
        # Fallback to pattern matching
        return {"success": False, "message": f"{self.name} cannot handle '{intent}' yet."}

    def get_metrics(self) -> Dict:
        """Return agent performance metrics"""
        return self._metrics.copy()


# Remove hard import to prevent circular dependency
# ai_engine should be injected during agent initialization
"""Routes queries to different AI models based on task type."""

import time
from typing import Optional, Callable


class MultiModelRouter:
    """Routes user queries to appropriate AI models based on task classification.

    Supports registering model handlers and routing by task type
    (e.g. 'chat', 'code', 'analysis', 'creative').
    """

    def __init__(self):
        self.models: dict[str, dict] = {}
        self.routes: dict[str, str] = {}
        self.routing_history: list[dict] = []
        self.default_model: Optional[str] = None

    def register_model(self, name: str, handler: Callable, capabilities: Optional[list[str]] = None) -> None:
        """Register an AI model with a handler function.

        Args:
            name: Unique model name.
            handler: Callable that accepts a prompt string and returns a response.
            capabilities: List of task types this model can handle.
        """
        if not name or not name.strip():
            raise ValueError("Model name must not be empty.")
        if not callable(handler):
            raise ValueError("Handler must be a callable.")

        self.models[name.strip()] = {
            "handler": handler,
            "capabilities": capabilities or [],
        }
        if self.default_model is None:
            self.default_model = name.strip()

    def set_route(self, task_type: str, model_name: str) -> None:
        """Map a task type to a specific model.

        Args:
            task_type: The task category (e.g. 'chat', 'code', 'analysis').
            model_name: Name of the registered model to route to.
        """
        if task_type not in ("chat", "code", "analysis", "creative", "summarization", "translation"):
            raise ValueError(f"Unknown task type '{task_type}'.")
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' is not registered.")
        self.routes[task_type] = model_name

    def classify_task(self, query: str) -> str:
        """Classify a query into a task type based on heuristics.

        Args:
            query: The user input string.

        Returns:
            Detected task type label.
        """
        q = query.lower()
        code_keywords = {"code", "function", "def ", "class ", "import ", "debug", "algorithm",
                         "syntax", "compile", "program", "script", "api"}
        analysis_keywords = {"analyze", "compare", "summarize", "explain", "what is",
                             "how does", "difference between", "calculate", "evaluate"}
        creative_keywords = {"write a story", "poem", "creative", "generate", "design",
                             "imagine", "invent", "compose", "art", "music"}
        chat_keywords = {"hello", "hi", "how are you", "what's up", "hey", "help",
                         "who are you", "thank"}

        if any(kw in q for kw in code_keywords):
            return "code"
        elif any(kw in q for kw in analysis_keywords):
            return "analysis"
        elif any(kw in q for kw in creative_keywords):
            return "creative"
        elif any(kw in q for kw in chat_keywords):
            return "chat"
        else:
            return "chat"

    def route(self, query: str, task_type: Optional[str] = None) -> dict:
        """Route a query to the appropriate model and return the response.

        Args:
            query: The user input.
            task_type: Optional explicit task type override. Auto-classified if omitted.

        Returns:
            Dictionary with model name, response, task type, and latency.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        if task_type is None:
            task_type = self.classify_task(query)

        model_name = self.routes.get(task_type) or self.default_model
        if model_name is None:
            raise RuntimeError(f"No model registered for task '{task_type}' and no default model set.")

        model = self.models[model_name]
        start = time.perf_counter()
        try:
            response = model["handler"](query)
        except Exception as e:
            response = f"Error executing model '{model_name}': {e}"

        latency = round((time.perf_counter() - start) * 1000, 2)

        result = {
            "model": model_name,
            "task_type": task_type,
            "response": response,
            "latency_ms": latency,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.routing_history.append(result)
        return result

    def get_model_info(self, model_name: Optional[str] = None) -> dict:
        """Get information about registered models.

        Args:
            model_name: Specific model to query, or None for all.

        Returns:
            Model metadata.
        """
        if model_name:
            model = self.models.get(model_name)
            if not model:
                raise ValueError(f"Model '{model_name}' not found.")
            return {
                "name": model_name,
                "capabilities": model["capabilities"],
                "has_handler": callable(model["handler"]),
            }
        return {
            name: {
                "capabilities": info["capabilities"],
                "has_handler": callable(info["handler"]),
            }
            for name, info in self.models.items()
        }

    def get_routing_stats(self, top_n: int = 10) -> dict:
        """Get statistics on routing patterns.

        Args:
            top_n: Number of recent entries to include.

        Returns:
            Stats dictionary with counts by model and task type.
        """
        from collections import Counter
        model_counter: Counter = Counter()
        task_counter: Counter = Counter()
        total_latency = 0.0

        recent = self.routing_history[-top_n:] if top_n else self.routing_history
        for entry in recent:
            model_counter[entry["model"]] += 1
            task_counter[entry["task_type"]] += 1
            total_latency += entry.get("latency_ms", 0)

        n = len(recent)
        return {
            "total_routed": n,
            "model_distribution": dict(model_counter.most_common()),
            "task_distribution": dict(task_counter.most_common()),
            "avg_latency_ms": round(total_latency / n, 2) if n > 0 else 0,
        }

    def set_default_model(self, model_name: str) -> None:
        """Set the default fallback model.

        Args:
            model_name: Name of the registered model.
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' is not registered.")
        self.default_model = model_name

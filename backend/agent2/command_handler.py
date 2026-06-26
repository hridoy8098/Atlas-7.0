# backend/agent2/command_handler.py — Agent2 Command Handler (Multi-step Task Pipeline)
# ভয়েস কমান্ড থেকে complex multi-step task execute করে

from typing import Dict, Any, Optional, Callable
from agent2.task_queue import get_queue, TaskPriority
from agent2.executor import AgentExecutor


class Agent2CommandHandler:
    def __init__(self, speak: Optional[Callable] = None):
        self.speak = speak
        self.executor = AgentExecutor(speak=speak)
        self.queue = get_queue(speak=speak)

    def execute(self, command: str, priority: TaskPriority = TaskPriority.NORMAL) -> Dict[str, Any]:
        """
        একটি voice command / goal নিয়ে plan তৈরি করে execute করে
        """
        print(f"[Agent2Handler] Goal: {command}")

        if not command or not command.strip():
            return {"success": False, "message": "No command provided, sir."}

        task_id = self.queue.submit(
            goal=command,
            priority=priority,
            speak=self.speak,
            on_complete=self._on_task_complete
        )

        return {
            "success": True,
            "message": f"Task queued with ID {task_id}, sir.",
            "task_id": task_id,
            "method": "agent2"
        }

    def execute_sync(self, command: str) -> Dict[str, Any]:
        """
        সরাসরি (blocking) execute — queue না করে এখনই শুরু করবে
        """
        try:
            result = self.executor.execute(goal=command, speak=self.speak)
            return {"success": True, "message": result, "method": "agent2"}
        except Exception as e:
            return {"success": False, "message": f"Task failed: {str(e)}"}

    def cancel_task(self, task_id: str) -> bool:
        return self.queue.cancel(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        return self.queue.get_status(task_id)

    def _on_task_complete(self, task_id: str, result: str):
        print(f"[Agent2Handler] Task {task_id} completed: {result[:100]}")

    def is_agent2_command(self, command: str) -> bool:
        cmd_lower = command.lower()
        agent2_keywords = [
            "research and", "research then", "find and", "search and",
            "create a", "build a", "make a", "write a",
            "compare", "analyze", "summarize",
            "organize", "clean up", "backup",
            "রিসার্চ", "খুঁজে", "তৈরি কর", "বানাও",
            "তুলনা", "এনালাইসিস", "সারাংশ",
            "গোছাও", "ব্যাকআপ", "পরিষ্কার",
        ]
        return any(kw in cmd_lower for kw in agent2_keywords)


agent2_handler: Optional[Agent2CommandHandler] = None


def get_agent2_handler(speak: Optional[Callable] = None) -> Agent2CommandHandler:
    global agent2_handler
    if agent2_handler is None:
        agent2_handler = Agent2CommandHandler(speak=speak)
    return agent2_handler


def handle_agent2_command(
    command: str,
    speak: Optional[Callable] = None,
    sync: bool = False,
) -> Dict[str, Any]:
    handler = get_agent2_handler(speak)
    if sync:
        return handler.execute_sync(command)
    return handler.execute(command)

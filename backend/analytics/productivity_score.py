"""Calculate productivity score from task completion data."""
from datetime import datetime, timedelta
from collections import defaultdict


class ProductivityScore:
    """Calculates productivity score based on task completion rates and timeliness."""

    def __init__(self):
        self._tasks = []

    def add_task(self, task_id: str, completed: bool = False,
                 completed_on_time: bool = False, timestamp: datetime = None):
        if not task_id:
            raise ValueError("task_id must be non-empty")
        self._tasks.append({
            "task_id": task_id,
            "completed": completed,
            "completed_on_time": completed_on_time,
            "timestamp": timestamp or datetime.now()
        })

    def calculate_score(self, since: datetime = None) -> float:
        data = self._tasks
        if since:
            data = [t for t in data if t["timestamp"] >= since]
        if not data:
            return 0.0

        completed = [t for t in data if t["completed"]]
        on_time = [t for t in completed if t["completed_on_time"]]

        completion_rate = len(completed) / len(data)
        timeliness_rate = len(on_time) / len(completed) if completed else 0.0

        raw = (completion_rate * 0.6 + timeliness_rate * 0.4) * 100
        return max(0.0, min(100.0, raw))

    def get_completed_count(self, since: datetime = None) -> int:
        data = self._tasks
        if since:
            data = [t for t in data if t["timestamp"] >= since]
        return sum(1 for t in data if t["completed"])

    def get_pending_count(self, since: datetime = None) -> int:
        data = self._tasks
        if since:
            data = [t for t in data if t["timestamp"] >= since]
        return sum(1 for t in data if not t["completed"])

    def get_daily_scores(self, days: int = 7) -> list:
        results = []
        for i in range(days):
            day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            tasks_today = [t for t in self._tasks if day_start <= t["timestamp"] < day_end]
            if tasks_today:
                completed = sum(1 for t in tasks_today if t["completed"])
                score = (completed / len(tasks_today)) * 100
            else:
                score = 0.0
            results.append({"date": day_start.date().isoformat(), "score": score})
        return list(reversed(results))

    def reset(self):
        self._tasks.clear()

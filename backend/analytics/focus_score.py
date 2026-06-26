"""Calculate focus/productivity score based on app usage patterns."""
from datetime import datetime, timedelta


class FocusScore:
    """Calculates a focus score (0-100) from app usage data."""

    PRODUCTIVITY_APPS = {"vscode", "notion", "excel", "word", "pycharm", "intellij",
                         "slack", "teams", "outlook", "terminal", "chrome-dev"}
    DISTRACTION_APPS = {"youtube", "netflix", "spotify", "instagram", "facebook",
                        "twitter", "reddit", "tiktok", "snapchat", "gaming", "games"}

    def __init__(self):
        self._usage_data = []

    def record_session(self, app: str, duration_seconds: float, timestamp: datetime = None):
        if duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        if not app or not isinstance(app, str):
            raise ValueError("app must be a non-empty string")
        self._usage_data.append({
            "app": app.lower(),
            "duration": duration_seconds,
            "timestamp": timestamp or datetime.now()
        })

    def calculate_score(self, since: datetime = None) -> float:
        if not self._usage_data:
            return 50.0
        data = self._usage_data
        if since:
            data = [d for d in data if d["timestamp"] >= since]
        if not data:
            return 50.0

        productive = sum(d["duration"] for d in data
                         if d["app"] in self.PRODUCTIVITY_APPS)
        distracting = sum(d["duration"] for d in data
                          if d["app"] in self.DISTRACTION_APPS)
        neutral = sum(d["duration"] for d in data
                      if d["app"] not in self.PRODUCTIVITY_APPS
                      and d["app"] not in self.DISTRACTION_APPS)
        total = productive + distracting + neutral
        if total == 0:
            return 50.0

        raw = ((productive + neutral * 0.5) / total) * 100
        return max(0.0, min(100.0, raw))

    def get_category_breakdown(self, since: datetime = None) -> dict:
        data = self._usage_data
        if since:
            data = [d for d in data if d["timestamp"] >= since]
        breakdown = {"productive": 0.0, "distracting": 0.0, "neutral": 0.0}
        for d in data:
            if d["app"] in self.PRODUCTIVITY_APPS:
                breakdown["productive"] += d["duration"]
            elif d["app"] in self.DISTRACTION_APPS:
                breakdown["distracting"] += d["duration"]
            else:
                breakdown["neutral"] += d["duration"]
        return breakdown

    def get_focus_streak(self, min_score: float = 60.0) -> int:
        from collections import defaultdict
        daily = defaultdict(float)
        for d in self._usage_data:
            day = d["timestamp"].date()
            if d["app"] in self.PRODUCTIVITY_APPS:
                daily[day] += d["duration"]
            elif d["app"] in self.DISTRACTION_APPS:
                daily[day] -= d["duration"]

        sorted_days = sorted(daily.keys())
        streak = 0
        current = 0
        for day in sorted_days:
            if daily[day] >= min_score * 60:
                current += 1
                streak = max(streak, current)
            else:
                current = 0
        return streak

    def reset(self):
        self._usage_data.clear()

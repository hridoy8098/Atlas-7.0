"""Study time tracking and subject-wise analysis."""
from datetime import datetime, timedelta
from collections import defaultdict


class StudyAnalytics:
    """Tracks study sessions and provides subject-wise analysis."""

    def __init__(self):
        self._sessions = []

    def start_session(self, subject: str, timestamp: datetime = None):
        if not subject or not isinstance(subject, str):
            raise ValueError("subject must be a non-empty string")
        ts = timestamp or datetime.now()
        self._sessions.append({
            "subject": subject.lower(),
            "start": ts,
            "end": None,
            "duration": None
        })

    def end_session(self, subject: str = None, timestamp: datetime = None):
        ts = timestamp or datetime.now()
        for session in reversed(self._sessions):
            if session["end"] is not None:
                continue
            if subject and session["subject"] != subject.lower():
                continue
            session["end"] = ts
            session["duration"] = (ts - session["start"]).total_seconds()
            return session
        raise ValueError("No active study session found")

    def get_total_study_hours(self, since: datetime = None) -> float:
        data = self._sessions
        if since:
            data = [s for s in data if s["start"] >= since]
        total_seconds = sum(s["duration"] for s in data if s["duration"] is not None)
        return total_seconds / 3600.0

    def get_subject_breakdown(self, since: datetime = None) -> dict:
        data = self._sessions
        if since:
            data = [s for s in data if s["start"] >= since]
        breakdown = defaultdict(float)
        for s in data:
            if s["duration"] is not None:
                breakdown[s["subject"]] += s["duration"] / 3600.0
        return dict(breakdown)

    def get_daily_study_hours(self, days: int = 7) -> list:
        results = []
        for i in range(days):
            day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            day_sessions = [
                s for s in self._sessions
                if s["duration"] is not None and day_start <= s["start"] < day_end
            ]
            hours = sum(s["duration"] for s in day_sessions) / 3600.0
            results.append({"date": day_start.date().isoformat(), "hours": hours})
        return list(reversed(results))

    def get_average_session_duration(self, subject: str = None) -> float:
        data = self._sessions
        if subject:
            data = [s for s in data if s["subject"] == subject.lower()]
        completed = [s for s in data if s["duration"] is not None]
        if not completed:
            return 0.0
        return sum(s["duration"] for s in completed) / len(completed)

    def reset(self):
        self._sessions.clear()

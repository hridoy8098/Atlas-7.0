"""Track application usage, time spent, and most-used apps."""
from collections import defaultdict
from datetime import datetime, timedelta


class AppTracker:
    """Tracks application usage statistics including time spent and frequency."""

    def __init__(self):
        self._sessions = []
        self._app_log = defaultdict(list)

    def log_open(self, app_name: str, timestamp: datetime = None) -> dict:
        if not app_name or not isinstance(app_name, str):
            raise ValueError("app_name must be a non-empty string")
        ts = timestamp or datetime.now()
        record = {"app": app_name, "action": "open", "timestamp": ts}
        self._app_log[app_name].append(record)
        self._sessions.append(record)
        return record

    def log_close(self, app_name: str, timestamp: datetime = None) -> dict:
        if not app_name or not isinstance(app_name, str):
            raise ValueError("app_name must be a non-empty string")
        ts = timestamp or datetime.now()
        record = {"app": app_name, "action": "close", "timestamp": ts}
        self._app_log[app_name].append(record)
        self._sessions.append(record)
        return record

    def get_time_spent(self, app_name: str = None) -> dict:
        result = {}
        apps = [app_name] if app_name else list(self._app_log.keys())
        for app in apps:
            records = self._app_log.get(app, [])
            total = timedelta()
            open_time = None
            for r in sorted(records, key=lambda x: x["timestamp"]):
                if r["action"] == "open":
                    open_time = r["timestamp"]
                elif r["action"] == "close" and open_time is not None:
                    total += r["timestamp"] - open_time
                    open_time = None
            result[app] = total.total_seconds()
        return result

    def get_most_used_apps(self, top_n: int = 5) -> list:
        time_spent = self.get_time_spent()
        sorted_apps = sorted(time_spent.items(), key=lambda x: x[1], reverse=True)
        return [{"app": app, "seconds": secs} for app, secs in sorted_apps[:top_n]]

    def get_total_usage_time(self) -> float:
        return sum(self.get_time_spent().values())

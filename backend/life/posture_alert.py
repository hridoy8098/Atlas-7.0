"""PostureAlert - Posture check reminders, sitting time tracking."""

import json
import os
import time
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class PostureAlert:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.sitting_file = os.path.join(self.data_dir, "sitting_log.json")
        self._ensure_data_dir()
        self._session_start = None
        self._posture_check_interval = 1800  # 30 minutes

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def start_sitting_session(self):
        self._session_start = time.time()
        return {"message": "Sitting session started.", "started_at": datetime.now().isoformat()}

    def end_sitting_session(self):
        if self._session_start is None:
            raise ValueError("No active sitting session.")
        elapsed = time.time() - self._session_start
        entry = {
            "duration_minutes": round(elapsed / 60, 2),
            "started_at": datetime.fromtimestamp(self._session_start).isoformat(),
            "ended_at": datetime.now().isoformat()
        }
        history = self.get_history()
        history.append(entry)
        with open(self.sitting_file, "w") as f:
            json.dump(history, f, indent=2)
        self._session_start = None
        return entry

    def check_posture(self):
        if self._session_start is None:
            return {"alert": False, "message": "No active session."}
        elapsed = time.time() - self._session_start
        if elapsed >= self._posture_check_interval:
            return {
                "alert": True,
                "message": "Please check your posture! Sit up straight, shoulders back.",
                "elapsed_minutes": round(elapsed / 60, 1)
            }
        return {
            "alert": False,
            "message": "Posture looks good.",
            "elapsed_minutes": round(elapsed / 60, 1)
        }

    def reset_posture_timer(self):
        self._session_start = time.time()
        return {"message": "Posture timer reset.", "reset_at": datetime.now().isoformat()}

    def set_posture_interval(self, minutes):
        if minutes < 1:
            raise ValueError("Interval must be at least 1 minute.")
        self._posture_check_interval = minutes * 60

    def get_history(self):
        if not os.path.exists(self.sitting_file):
            return []
        with open(self.sitting_file, "r") as f:
            return json.load(f)

    def total_sitting_time_today(self):
        history = self.get_history()
        today = datetime.now().strftime("%Y-%m-%d")
        total = 0
        for entry in history:
            try:
                if entry["started_at"].startswith(today):
                    total += entry["duration_minutes"]
            except (KeyError, AttributeError):
                continue
        return round(total, 2)

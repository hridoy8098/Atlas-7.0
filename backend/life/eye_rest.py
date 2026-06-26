"""EyeRest - 20-20-20 rule timer, eye exercise reminders."""

import time
import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class EyeRest:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.log_file = os.path.join(self.data_dir, "eye_rest_log.json")
        self._ensure_data_dir()
        self._timer_start = None
        self._reminder_interval = 1200  # 20 minutes in seconds

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def start_timer(self):
        self._timer_start = time.time()
        return {"message": "Eye rest timer started.", "started_at": datetime.now().isoformat()}

    def check_rest_needed(self):
        if self._timer_start is None:
            return {"rest_needed": False, "message": "Timer not started."}
        elapsed = time.time() - self._timer_start
        rest_needed = elapsed >= self._reminder_interval
        return {
            "rest_needed": rest_needed,
            "elapsed_seconds": round(elapsed),
            "message": "Time for a break! Look at something 20 feet away for 20 seconds." if rest_needed else "Keep going."
        }

    def reset_timer(self):
        self._timer_start = time.time()
        return {"message": "Timer reset.", "reset_at": datetime.now().isoformat()}

    def log_eye_exercise(self, exercise_type, duration_seconds):
        if duration_seconds <= 0:
            raise ValueError("Duration must be positive.")
        entry = {
            "exercise_type": exercise_type,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now().isoformat()
        }
        history = self.get_history()
        history.append(entry)
        with open(self.log_file, "w") as f:
            json.dump(history, f, indent=2)
        return entry

    def get_exercises(self):
        return [
            {"name": "Palming", "description": "Rub hands together, place over closed eyes for 20 seconds."},
            {"name": "Focus Shift", "description": "Focus on a distant object 20 feet away for 20 seconds."},
            {"name": "Figure Eight", "description": "Trace a figure eight with your eyes for 30 seconds."},
            {"name": "Blinking", "description": "Blink rapidly 10 times, then close eyes for 5 seconds."},
            {"name": "Rolling", "description": "Roll eyes clockwise then counter-clockwise, 5 times each."}
        ]

    def get_history(self):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            return json.load(f)

    def set_reminder_interval(self, seconds):
        if seconds < 60:
            raise ValueError("Interval must be at least 60 seconds.")
        self._reminder_interval = seconds

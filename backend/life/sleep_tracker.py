"""SleepTracker - Sleep logging, duration calc, quality tracking."""

import json
import os
from datetime import datetime, timedelta


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class SleepTracker:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.sleep_file = os.path.join(self.data_dir, "sleep_log.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_log(self):
        if not os.path.exists(self.sleep_file):
            return []
        with open(self.sleep_file, "r") as f:
            return json.load(f)

    def _save_log(self, log):
        with open(self.sleep_file, "w") as f:
            json.dump(log, f, indent=2)

    def _calculate_duration(self, bed_time, wake_time):
        fmt = "%Y-%m-%d %H:%M"
        try:
            bed = datetime.strptime(bed_time, fmt)
            wake = datetime.strptime(wake_time, fmt)
        except ValueError:
            raise ValueError("Times must be in 'YYYY-MM-DD HH:MM' format.")
        duration = wake - bed
        if duration.total_seconds() < 0:
            duration += timedelta(days=1)
        hours = duration.total_seconds() / 3600
        return round(hours, 2)

    def log_sleep(self, bed_time, wake_time, quality=None, notes=None):
        duration_hours = self._calculate_duration(bed_time, wake_time)
        if duration_hours <= 0:
            raise ValueError("Wake time must be after bed time.")
        entry = {
            "bed_time": bed_time,
            "wake_time": wake_time,
            "duration_hours": duration_hours,
            "quality": quality,
            "notes": notes or "",
            "logged_at": datetime.now().isoformat()
        }
        log = self._load_log()
        log.append(entry)
        self._save_log(log)
        return entry

    def get_sleep_data(self, days=7):
        log = self._load_log()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent = [e for e in log if e.get("logged_at", "") >= cutoff]
        return recent

    def get_average_duration(self, days=7):
        data = self.get_sleep_data(days)
        if not data:
            return 0
        durations = [e["duration_hours"] for e in data]
        return round(sum(durations) / len(durations), 2)

    def get_quality_summary(self, days=7):
        data = self.get_sleep_data(days)
        if not data:
            return {"average_quality": None, "entries": 0}
        qualities = [e["quality"] for e in data if e.get("quality") is not None]
        if not qualities:
            return {"average_quality": None, "entries": len(data)}
        avg_quality = round(sum(qualities) / len(qualities), 2)
        return {"average_quality": avg_quality, "entries": len(data)}

    def delete_entry(self, index):
        log = self._load_log()
        if index < 0 or index >= len(log):
            raise ValueError("Invalid entry index.")
        removed = log.pop(index)
        self._save_log(log)
        return {"message": "Entry deleted.", "entry": removed}

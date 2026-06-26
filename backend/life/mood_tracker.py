"""MoodTracker - Mood logging, trends, calendar view data."""

import json
import os
from datetime import datetime, timedelta
from collections import Counter


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class MoodTracker:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.mood_file = os.path.join(self.data_dir, "mood_log.json")
        self._ensure_data_dir()
        self.moods = {
            "happy": 5, "excited": 5, "content": 4, "calm": 4,
            "neutral": 3, "sad": 2, "anxious": 2, "angry": 1,
            "stressed": 1, "depressed": 1
        }

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_log(self):
        if not os.path.exists(self.mood_file):
            return []
        with open(self.mood_file, "r") as f:
            return json.load(f)

    def _save_log(self, log):
        with open(self.mood_file, "w") as f:
            json.dump(log, f, indent=2)

    def log_mood(self, mood, note=None):
        mood = mood.lower()
        if mood not in self.moods:
            raise ValueError(f"Invalid mood. Valid: {', '.join(self.moods.keys())}")
        entry = {
            "mood": mood,
            "score": self.moods[mood],
            "note": note or "",
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        log = self._load_log()
        log.append(entry)
        self._save_log(log)
        return entry

    def get_trends(self, days=7):
        log = self._load_log()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent = [e for e in log if e["timestamp"] >= cutoff]
        if not recent:
            return {"average_score": 0, "most_common": None, "entries": []}
        scores = [e["score"] for e in recent]
        moods_list = [e["mood"] for e in recent]
        avg_score = round(sum(scores) / len(scores), 2)
        most_common = Counter(moods_list).most_common(1)[0][0]
        return {"average_score": avg_score, "most_common": most_common, "entries": recent}

    def get_calendar_data(self, year, month):
        log = self._load_log()
        result = {}
        for e in log:
            try:
                dt = datetime.fromisoformat(e["timestamp"])
                if dt.year == year and dt.month == month:
                    day = str(dt.day)
                    if day not in result or dt.isoformat() > result[day]["timestamp"]:
                        result[day] = {"mood": e["mood"], "score": e["score"], "timestamp": e["timestamp"]}
            except (ValueError, TypeError):
                continue
        return result

    def get_mood_scores(self):
        return dict(self.moods)

    def get_recent_moods(self, limit=10):
        log = self._load_log()
        return log[-limit:]

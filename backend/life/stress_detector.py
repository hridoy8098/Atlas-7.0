"""StressDetector - Stress level calculation from various inputs."""

import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class StressDetector:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.log_file = os.path.join(self.data_dir, "stress_log.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_log(self):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            return json.load(f)

    def _save_log(self, log):
        with open(self.log_file, "w") as f:
            json.dump(log, f, indent=2)

    def calculate_stress(self, heart_rate=None, sleep_hours=None, work_hours=None,
                         mood_score=None, exercise_minutes=None):
        score = 0
        factors = {}
        if heart_rate is not None:
            if heart_rate > 100:
                score += 30
                factors["heart_rate"] = "elevated"
            elif heart_rate > 80:
                score += 15
                factors["heart_rate"] = "slightly elevated"
            else:
                factors["heart_rate"] = "normal"
        if sleep_hours is not None:
            if sleep_hours < 5:
                score += 25
                factors["sleep"] = "severe deprivation"
            elif sleep_hours < 7:
                score += 15
                factors["sleep"] = "mild deprivation"
            else:
                factors["sleep"] = "adequate"
        if work_hours is not None:
            if work_hours > 12:
                score += 25
                factors["work_hours"] = "overtime"
            elif work_hours > 8:
                score += 10
                factors["work_hours"] = "moderate"
            else:
                factors["work_hours"] = "normal"
        if mood_score is not None:
            if mood_score <= 2:
                score += 20
                factors["mood"] = "low"
            elif mood_score <= 3:
                score += 10
                factors["mood"] = "moderate"
            else:
                factors["mood"] = "positive"
        if exercise_minutes is not None:
            if exercise_minutes < 15:
                score += 10
                factors["exercise"] = "low"
            else:
                factors["exercise"] = "active"

        level = self._get_stress_level(score)
        return {
            "stress_score": score,
            "stress_level": level,
            "factors": factors,
            "assessed_at": datetime.now().isoformat()
        }

    def _get_stress_level(self, score):
        if score >= 70:
            return "High"
        if score >= 40:
            return "Moderate"
        if score >= 20:
            return "Mild"
        return "Low"

    def log_stress_assessment(self, **kwargs):
        result = self.calculate_stress(**kwargs)
        log = self._load_log()
        log.append(result)
        self._save_log(log)
        return result

    def get_stress_history(self, limit=20):
        log = self._load_log()
        return log[-limit:]

    def get_stress_trend(self, days=7):
        log = self._load_log()
        cutoff = (datetime.now().isoformat())
        recent = [e for e in log if e.get("assessed_at", "") <= cutoff][-days:]
        if not recent:
            return {"average_score": 0, "trend": "stable", "entries": []}
        scores = [e["stress_score"] for e in recent]
        avg = round(sum(scores) / len(scores), 2)
        if len(scores) >= 2:
            trend = "increasing" if scores[-1] > scores[0] else "decreasing" if scores[-1] < scores[0] else "stable"
        else:
            trend = "stable"
        return {"average_score": avg, "trend": trend, "entries": recent}

    def get_stress_relief_tips(self, level):
        tips = {
            "Low": ["Keep up your routine!", "Stay hydrated.", "Take short breaks."],
            "Mild": ["Go for a 10-minute walk.", "Practice deep breathing.", "Listen to calming music."],
            "Moderate": ["Try meditation for 15 minutes.", "Talk to a friend or family member.", "Write in a journal."],
            "High": ["Consult a professional.", "Take a day off if possible.", "Practice progressive muscle relaxation."]
        }
        return tips.get(level, tips["Low"])

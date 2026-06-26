"""Predict habit formation likelihood from user behavior data."""
from datetime import datetime, date, timedelta
from collections import defaultdict


class HabitPredictor:
    """Predicts the likelihood of habit formation based on user streak data."""

    def __init__(self):
        self._habits = defaultdict(list)

    def log_habit_completion(self, habit_name: str, completed: bool = True,
                             timestamp: datetime = None):
        if not habit_name or not isinstance(habit_name, str):
            raise ValueError("habit_name must be a non-empty string")
        ts = timestamp or datetime.now()
        self._habits[habit_name].append({"completed": completed, "timestamp": ts})

    def get_streak(self, habit_name: str) -> int:
        records = self._habits.get(habit_name, [])
        if not records:
            return 0
        sorted_recs = sorted(records, key=lambda r: r["timestamp"], reverse=True)
        streak = 0
        for r in sorted_recs:
            if r["completed"]:
                streak += 1
            else:
                break
        return streak

    def get_completion_rate(self, habit_name: str, days: int = 30) -> float:
        records = self._habits.get(habit_name, [])
        if not records:
            return 0.0
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in records if r["timestamp"] >= cutoff]
        if not recent:
            return 0.0
        completed = sum(1 for r in recent if r["completed"])
        return completed / len(recent)

    def predict_formation_probability(self, habit_name: str) -> float:
        records = self._habits.get(habit_name, [])
        if not records:
            return 0.5

        streak = self.get_streak(habit_name)
        rate = self.get_completion_rate(habit_name)

        streak_score = min(1.0, streak / 66.0)
        rate_score = rate
        consistency_bonus = 0.1 if rate >= 0.8 else 0.0

        raw = (streak_score * 0.4 + rate_score * 0.5 + consistency_bonus)
        return max(0.0, min(1.0, raw))

    def get_all_habit_predictions(self) -> dict:
        return {h: self.predict_formation_probability(h) for h in self._habits}

    def get_habits_needing_attention(self, threshold: float = 0.5) -> list:
        needing = []
        for h in self._habits:
            prob = self.predict_formation_probability(h)
            if prob < threshold:
                needing.append({"habit": h, "probability": prob, "streak": self.get_streak(h)})
        return needing

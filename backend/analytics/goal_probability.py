"""Predict probability of achieving goals based on current progress."""
from datetime import datetime, date
from math import exp


class GoalProbability:
    """Predicts goal achievement probability using progress data."""

    def __init__(self):
        self._goals = {}

    def set_goal(self, goal_id: str, target_value: float, current_value: float = 0.0,
                 deadline: date = None, created_at: date = None):
        if not goal_id:
            raise ValueError("goal_id must be non-empty")
        if target_value <= 0:
            raise ValueError("target_value must be positive")
        if current_value < 0:
            raise ValueError("current_value must be non-negative")
        self._goals[goal_id] = {
            "target": target_value,
            "current": current_value,
            "deadline": deadline or date.today(),
            "created_at": created_at or date.today()
        }

    def update_progress(self, goal_id: str, current_value: float):
        if goal_id not in self._goals:
            raise KeyError(f"Goal '{goal_id}' not found")
        if current_value < 0:
            raise ValueError("current_value must be non-negative")
        self._goals[goal_id]["current"] = current_value

    def get_probability(self, goal_id: str) -> float:
        if goal_id not in self._goals:
            raise KeyError(f"Goal '{goal_id}' not found")
        g = self._goals[goal_id]
        progress_ratio = g["current"] / g["target"]
        if progress_ratio >= 1.0:
            return 1.0

        total_days = (g["deadline"] - g["created_at"]).days
        if total_days <= 0:
            return 1.0 if progress_ratio >= 1.0 else 0.0

        elapsed = (date.today() - g["created_at"]).days
        elapsed = max(0, min(elapsed, total_days))
        time_ratio = elapsed / total_days

        if time_ratio <= 0:
            return max(0.0, min(1.0, progress_ratio))

        required_pace = 1.0 / total_days
        actual_pace = progress_ratio / elapsed if elapsed > 0 else 0
        pace_factor = actual_pace / required_pace if required_pace > 0 else 0

        score = 1.0 / (1.0 + exp(-4.0 * (pace_factor - 0.5)))
        if progress_ratio >= 0.9:
            score = max(score, 0.85)
        return max(0.0, min(1.0, score))

    def get_all_probabilities(self) -> dict:
        return {gid: self.get_probability(gid) for gid in self._goals}

    def get_goals_at_risk(self, threshold: float = 0.4) -> list:
        at_risk = []
        for gid, g in self._goals.items():
            prob = self.get_probability(gid)
            if prob < threshold:
                at_risk.append({
                    "goal_id": gid,
                    "probability": prob,
                    "current": g["current"],
                    "target": g["target"]
                })
        return at_risk

    def remove_goal(self, goal_id: str):
        if goal_id not in self._goals:
            raise KeyError(f"Goal '{goal_id}' not found")
        del self._goals[goal_id]

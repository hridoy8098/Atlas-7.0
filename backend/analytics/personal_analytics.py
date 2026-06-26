"""Aggregate personal analytics dashboard data from all analytics modules."""
from .app_tracker import AppTracker
from .focus_score import FocusScore
from .goal_probability import GoalProbability
from .habit_predictor import HabitPredictor
from .productivity_score import ProductivityScore
from .spending_analytics import SpendingAnalytics
from .study_analytics import StudyAnalytics


class PersonalAnalytics:
    """Aggregates data from all analytics modules for a unified dashboard view."""

    def __init__(self):
        self.app_tracker = AppTracker()
        self.focus_score = FocusScore()
        self.goal_probability = GoalProbability()
        self.habit_predictor = HabitPredictor()
        self.productivity_score = ProductivityScore()
        self.spending_analytics = SpendingAnalytics()
        self.study_analytics = StudyAnalytics()

    def get_dashboard_summary(self) -> dict:
        return {
            "focus": self._focus_summary(),
            "goals": self._goal_summary(),
            "habits": self._habit_summary(),
            "productivity": self._productivity_summary(),
            "spending": self._spending_summary(),
            "study": self._study_summary(),
            "usage": self._usage_summary()
        }

    def _focus_summary(self) -> dict:
        return {
            "score": self.focus_score.calculate_score(),
            "breakdown": self.focus_score.get_category_breakdown()
        }

    def _goal_summary(self) -> dict:
        probs = self.goal_probability.get_all_probabilities()
        avg = sum(probs.values()) / len(probs) if probs else 0.0
        return {
            "goals_count": len(probs),
            "average_probability": avg,
            "at_risk": self.goal_probability.get_goals_at_risk()
        }

    def _habit_summary(self) -> dict:
        preds = self.habit_predictor.get_all_habit_predictions()
        avg = sum(preds.values()) / len(preds) if preds else 0.0
        return {
            "habits_count": len(preds),
            "average_probability": avg,
            "needing_attention": self.habit_predictor.get_habits_needing_attention()
        }

    def _productivity_summary(self) -> dict:
        return {
            "score": self.productivity_score.calculate_score(),
            "completed": self.productivity_score.get_completed_count(),
            "pending": self.productivity_score.get_pending_count()
        }

    def _spending_summary(self) -> dict:
        return {
            "total_spent": self.spending_analytics.get_total_spent(),
            "category_breakdown": self.spending_analytics.get_category_breakdown()
        }

    def _study_summary(self) -> dict:
        return {
            "total_hours": self.study_analytics.get_total_study_hours(),
            "subject_breakdown": self.study_analytics.get_subject_breakdown()
        }

    def _usage_summary(self) -> dict:
        return {
            "total_usage_seconds": self.app_tracker.get_total_usage_time(),
            "most_used": self.app_tracker.get_most_used_apps()
        }

    def reset_all(self):
        self.app_tracker = AppTracker()
        self.focus_score = FocusScore()
        self.goal_probability = GoalProbability()
        self.habit_predictor = HabitPredictor()
        self.productivity_score = ProductivityScore()
        self.spending_analytics = SpendingAnalytics()
        self.study_analytics = StudyAnalytics()

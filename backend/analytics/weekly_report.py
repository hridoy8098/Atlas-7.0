"""Generate weekly analytics reports from all analytics modules."""
from datetime import datetime, timedelta, date
from .app_tracker import AppTracker
from .focus_score import FocusScore
from .goal_probability import GoalProbability
from .habit_predictor import HabitPredictor
from .productivity_score import ProductivityScore
from .spending_analytics import SpendingAnalytics
from .study_analytics import StudyAnalytics


class WeeklyReport:
    """Generates weekly aggregated analytics reports."""

    def __init__(self, app_tracker=None, focus_score=None,
                 goal_probability=None, habit_predictor=None,
                 productivity_score=None, spending_analytics=None,
                 study_analytics=None):
        self.app_tracker = app_tracker or AppTracker()
        self.focus_score = focus_score or FocusScore()
        self.goal_probability = goal_probability or GoalProbability()
        self.habit_predictor = habit_predictor or HabitPredictor()
        self.productivity_score = productivity_score or ProductivityScore()
        self.spending_analytics = spending_analytics or SpendingAnalytics()
        self.study_analytics = study_analytics or StudyAnalytics()

    def generate_weekly_report(self, week_start: date = None) -> dict:
        ws = week_start or (date.today() - timedelta(days=date.today().weekday()))
        week_end = ws + timedelta(days=7)

        since_dt = datetime(ws.year, ws.month, ws.day)

        focus = self.focus_score.calculate_score(since=since_dt)
        product = self.productivity_score.calculate_score(since=since_dt)

        return {
            "week_start": ws.isoformat(),
            "week_end": week_end.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "focus_score": focus,
            "productivity_score": product,
            "goals": self._goals_section(),
            "habits": self._habits_section(),
            "spending": self._spending_section(since=since_dt),
            "study": self._study_section(since=since_dt),
            "usage": self._usage_section(since=since_dt)
        }

    def _goals_section(self) -> dict:
        probs = self.goal_probability.get_all_probabilities()
        avg = sum(probs.values()) / len(probs) if probs else 0.0
        return {
            "total_goals": len(probs),
            "average_probability": round(avg, 4),
            "at_risk_count": len(self.goal_probability.get_goals_at_risk())
        }

    def _habits_section(self) -> dict:
        preds = self.habit_predictor.get_all_habit_predictions()
        avg = sum(preds.values()) / len(preds) if preds else 0.0
        return {
            "total_habits": len(preds),
            "average_probability": round(avg, 4),
            "needing_attention_count": len(self.habit_predictor.get_habits_needing_attention())
        }

    def _spending_section(self, since: datetime = None) -> dict:
        return {
            "total_spent": round(self.spending_analytics.get_total_spent(since=since), 2),
            "top_categories": self.spending_analytics.get_top_categories(3)
        }

    def _study_section(self, since: datetime = None) -> dict:
        return {
            "total_hours": round(self.study_analytics.get_total_study_hours(since=since), 2),
            "subjects": self.study_analytics.get_subject_breakdown(since=since)
        }

    def _usage_section(self, since: datetime = None) -> dict:
        total_secs = self.app_tracker.get_total_usage_time()
        return {
            "total_usage_hours": round(total_secs / 3600.0, 2),
            "most_used_apps": self.app_tracker.get_most_used_apps(3)
        }

    def compare_weeks(self, week1_start: date, week2_start: date) -> dict:
        r1 = self.generate_weekly_report(week1_start)
        r2 = self.generate_weekly_report(week2_start)
        diff_focus = r2["focus_score"] - r1["focus_score"]
        diff_productivity = r2["productivity_score"] - r1["productivity_score"]
        return {
            "week1": r1,
            "week2": r2,
            "changes": {
                "focus_score_change": round(diff_focus, 4),
                "productivity_score_change": round(diff_productivity, 4)
            }
        }

    def summary_text(self, week_start: date = None) -> str:
        report = self.generate_weekly_report(week_start)
        lines = [
            f"Weekly Report ({report['week_start']} to {report['week_end']})",
            f"Focus Score: {report['focus_score']:.1f}/100",
            f"Productivity Score: {report['productivity_score']:.1f}/100",
            f"Goals: {report['goals']['total_goals']} active, "
            f"{report['goals']['at_risk_count']} at risk",
            f"Habits: {report['habits']['total_habits']} tracked, "
            f"{report['habits']['needing_attention_count']} needing attention",
            f"Spending: ${report['spending']['total_spent']:.2f}",
            f"Study Hours: {report['study']['total_hours']:.1f}h",
            f"Usage: {report['usage']['total_usage_hours']:.1f}h total"
        ]
        return "\n".join(lines)

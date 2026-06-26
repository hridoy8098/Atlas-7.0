"""Lifestyle modules: BMI, eye rest, journal, mood, posture, reminders, sleep, stress, time capsule, workout"""

from .bmi_calculator import BMICalculator
from .eye_rest import EyeRest
from .journal import Journal
from .mood_tracker import MoodTracker
from .posture_alert import PostureAlert
from .reminder import LifeReminder
from .sleep_tracker import SleepTracker
from .stress_detector import StressDetector
from .time_capsule import TimeCapsule
from .workout import Workout

__all__ = ["BMICalculator", "EyeRest", "Journal", "MoodTracker",
           "PostureAlert", "LifeReminder", "SleepTracker", "StressDetector",
           "TimeCapsule", "Workout"]

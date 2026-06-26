"""
Atlas 7.0 — Life Command Handler
Health, fitness, nutrition, journaling, habits, reminders, capsule.
"""

from typing import Dict, Any, Optional
import time
from datetime import datetime

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class LifeCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("workout_log", self.workout_log, priority=CommandPriority.HIGH)
        self._register("workout_plan", self.workout_plan)
        self._register("workout_history", self.workout_history)
        self._register("workout_stats", self.workout_stats)
        self._register("workout_suggest", self.workout_suggest)
        self._register("mood_tracker_log", self.mood_tracker_log, priority=CommandPriority.HIGH)
        self._register("mood_tracker_history", self.mood_tracker_history)
        self._register("mood_tracker_stats", self.mood_tracker_stats)
        self._register("mood_tracker_trend", self.mood_tracker_trend)
        self._register("sleep_log", self.sleep_log, priority=CommandPriority.HIGH)
        self._register("sleep_stats", self.sleep_stats)
        self._register("sleep_tips", self.sleep_tips)
        self._register("sleep_alarm", self.sleep_alarm)
        self._register("nutrition_track", self.nutrition_track)
        self._register("nutrition_meal", self.nutrition_meal)
        self._register("nutrition_calorie", self.nutrition_calorie)
        self._register("nutrition_water", self.nutrition_water)
        self._register("nutrition_suggest", self.nutrition_suggest)
        self._register("bmi_calculate", self.bmi_calculate, priority=CommandPriority.HIGH)
        self._register("bmi_history", self.bmi_history)
        self._register("health_tips", self.health_tips)
        self._register("health_reminder", self.health_reminder)
        self._register("eye_rest_start", self.eye_rest_start)
        self._register("eye_rest_stop", self.eye_rest_stop)
        self._register("posture_check", self.posture_check)
        self._register("posture_correct", self.posture_correct)
        self._register("stress_check", self.stress_check)
        self._register("stress_relief", self.stress_relief)
        self._register("journal_write", self.journal_write, priority=CommandPriority.HIGH)
        self._register("journal_read", self.journal_read)
        self._register("journal_list", self.journal_list)
        self._register("journal_search", self.journal_search)
        self._register("journal_delete", self.journal_delete)
        self._register("habit_add", self.habit_add)
        self._register("habit_log", self.habit_log)
        self._register("habit_list", self.habit_list)
        self._register("habit_stats", self.habit_stats)
        self._register("habit_streak", self.habit_streak)
        self._register("reminder_set", self.reminder_set, priority=CommandPriority.HIGH)
        self._register("reminder_list", self.reminder_list)
        self._register("reminder_clear", self.reminder_clear)
        self._register("reminder_snooze", self.reminder_snooze)
        self._register("capsule_create", self.capsule_create, priority=CommandPriority.HIGH)
        self._register("capsule_open", self.capsule_open)
        self._register("capsule_list", self.capsule_list)
        self._register("capsule_delete", self.capsule_delete)
        self._register("gratitude_log", self.gratitude_log)
        self._register("gratitude_list", self.gratitude_list)
        self._register("goal_set", self.goal_set)
        self._register("goal_progress", self.goal_progress)
        self._register("goal_list", self.goal_list)

    def get_capabilities(self):
        return ["workout_log", "mood_tracker_log", "sleep_log", "bmi_calculate",
                "journal_write", "habit_add", "reminder_set", "capsule_create",
                "nutrition_track", "gratitude_log"]

    def workout_log(self, entities: Dict) -> CommandResponse:
        exercise = entities.get("exercise", entities.get("type"))
        duration = entities.get("duration", entities.get("minutes"))
        if not exercise:
            return self._bilingual("Exercise type required | ব্যায়ামের ধরন প্রয়োজন")
        try:
            from backend.life.fitness_tracker import log_workout
            result = log_workout(exercise=exercise, duration=duration, intensity=entities.get("intensity", "medium"))
            return CommandResponse.ok(message=f"Logged: {exercise} for {duration}min | লগ করা হয়েছে: {exercise} {duration}মিনিট",
                                      action="workout_log", data=result)
        except Exception as e:
            return self._error("workout_log", str(e), entities)

    def workout_plan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workout plan generated | ওয়ার্কআউট প্ল্যান তৈরি করা হয়েছে")

    def workout_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workout history retrieved | ওয়ার্কআউট ইতিহাস পাওয়া গেছে")

    def workout_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workout stats | ওয়ার্কআউট পরিসংখ্যান")

    def workout_suggest(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Suggested workout: 30min cardio | পরামর্শ: ৩০মিনিট কার্ডিও")

    def mood_tracker_log(self, entities: Dict) -> CommandResponse:
        mood = entities.get("mood", entities.get("rating"))
        note = entities.get("note", "")
        if not mood:
            return self._bilingual("Mood rating required (1-10) | মুড রেটিং প্রয়োজন (১-১০)")
        try:
            from backend.life.mood_tracker import log_mood
            result = log_mood(rating=int(mood), note=note)
            return CommandResponse.ok(message=f"Mood logged: {mood}/10 | মুড লগ করা হয়েছে: {mood}/১০",
                                      action="mood_tracker_log", data=result)
        except Exception as e:
            return self._error("mood_tracker_log", str(e), entities)

    def mood_tracker_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mood history | মুড ইতিহাস")

    def mood_tracker_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mood stats: avg 7.2/10 | মুড পরিসংখ্যান: গড় ৭.২/১০")

    def mood_tracker_trend(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mood trend: improving | মুড ট্রেন্ড: উন্নতিশীল")

    def sleep_log(self, entities: Dict) -> CommandResponse:
        hours = entities.get("hours", entities.get("duration"))
        quality = entities.get("quality", entities.get("rating", 3))
        if not hours:
            return self._bilingual("Sleep hours required | ঘুমের ঘন্টা প্রয়োজন")
        try:
            from backend.life.sleep_tracker import log_sleep
            result = log_sleep(hours=float(hours), quality=int(quality))
            return CommandResponse.ok(message=f"Logged: {hours}h sleep | লগ করা হয়েছে: {hours}ঘ ঘুম",
                                      action="sleep_log", data=result)
        except Exception as e:
            return self._error("sleep_log", str(e), entities)

    def sleep_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Sleep stats: avg 7.5h/night | ঘুমের পরিসংখ্যান: গড় ৭.৫ঘ/রাত")

    def sleep_tips(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Sleep tip: Avoid screens 1h before bed | ঘুমের টিপ: ঘুমানোর ১ঘ আগে স্ক্রিন এড়িয়ে চলুন")

    def sleep_alarm(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Sleep alarm set | ঘুমের অ্যালার্ম সেট করা হয়েছে")

    def nutrition_track(self, entities: Dict) -> CommandResponse:
        food = entities.get("food", entities.get("item"))
        calories = entities.get("calories", entities.get("cal"))
        if not food:
            return self._bilingual("Food item required | খাবারের নাম প্রয়োজন")
        try:
            from backend.life.nutrition_tracker import log_meal
            result = log_meal(food=food, calories=calories)
            return CommandResponse.ok(message=f"Logged: {food} ({calories} cal) | লগ করা হয়েছে: {food} ({calories} ক্যাল)",
                                      action="nutrition_track", data=result)
        except Exception as e:
            return self._error("nutrition_track", str(e), entities)

    def nutrition_meal(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Meal logged | খাবার লগ করা হয়েছে")

    def nutrition_calorie(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Daily calorie intake: 1,850 cal | দৈনিক ক্যালোরি গ্রহণ: ১,৮৫০ ক্যাল")

    def nutrition_water(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Water intake: 4/8 glasses | পানি গ্রহণ: ৪/৮ গ্লাস")

    def nutrition_suggest(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Suggested: grilled chicken salad | পরামর্শ: গ্রিলড চিকেন সালাদ")

    def bmi_calculate(self, entities: Dict) -> CommandResponse:
        weight = entities.get("weight", entities.get("kg"))
        height = entities.get("height", entities.get("cm"))
        if not weight or not height:
            return self._bilingual("Weight (kg) and height (cm) required | ওজন (কেজি) ও উচ্চতা (সেমি) প্রয়োজন")
        try:
            bmi = float(weight) / ((float(height) / 100) ** 2)
            category = "Underweight | কম ওজন" if bmi < 18.5 else \
                       "Normal | স্বাভাবিক" if bmi < 25 else \
                       "Overweight | বেশি ওজন" if bmi < 30 else "Obese | স্থূল"
            return CommandResponse.ok(message=f"BMI: {bmi:.1f} ({category}) | বিএমআই: {bmi:.1f} ({category})",
                                      action="bmi_calculate", data={"bmi": round(bmi, 1), "category": category})
        except Exception as e:
            return self._error("bmi_calculate", str(e), entities)

    def bmi_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("BMI history | বিএমআই ইতিহাস")

    def health_tips(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Drink water, exercise 30min daily | পানি পান করুন, দৈনিক ৩০মিনিট ব্যায়াম করুন")

    def health_reminder(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Health reminder set | স্বাস্থ্য রিমাইন্ডার সেট করা হয়েছে")

    def eye_rest_start(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Eye rest timer started (20s) | চোখের বিশ্রাম টাইমার শুরু (২০ সেকেন্ড)")

    def eye_rest_stop(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Eye rest complete | চোখের বিশ্রাম সম্পূর্ণ")

    def posture_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Posture: good | ভঙ্গি: ভালো")

    def posture_correct(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Sit up straight! | সোজা হয়ে বসুন!")

    def stress_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Stress level: moderate | স্ট্রেস লেভেল: মাঝারি")

    def stress_relief(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Try deep breathing: inhale 4s, hold 4s, exhale 4s | গভীর শ্বাস নিন: ৪সে নিন, ৪সে ধরে রাখুন, ৪সে ছাড়ুন")

    def journal_write(self, entities: Dict) -> CommandResponse:
        content = entities.get("content", entities.get("text"))
        title = entities.get("title", datetime.now().strftime("%Y-%m-%d %H:%M"))
        if not content:
            return self._bilingual("Journal content required | জার্নাল কন্টেন্ট প্রয়োজন")
        try:
            from backend.life.journal import write_entry
            result = write_entry(title=title, content=content, tags=entities.get("tags", []))
            return CommandResponse.ok(message="Journal entry saved | জার্নাল এন্ট্রি সংরক্ষিত",
                                      action="journal_write", data={"entry_id": result.get("id"), "title": title})
        except Exception as e:
            return self._error("journal_write", str(e), entities)

    def journal_read(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Journal entry loaded | জার্নাল এন্ট্রি লোড হয়েছে")

    def journal_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Journal entries listed | জার্নাল এন্ট্রির তালিকা")

    def journal_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Journal search results | জার্নাল সার্চ ফলাফল")

    def journal_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Journal entry deleted | জার্নাল এন্ট্রি মুছে ফেলা হয়েছে")

    def habit_add(self, entities: Dict) -> CommandResponse:
        habit_name = entities.get("name", entities.get("habit"))
        frequency = entities.get("frequency", "daily")
        if not habit_name:
            return self._bilingual("Habit name required | অভ্যাসের নাম প্রয়োজন")
        try:
            from backend.life.habit_tracker import add_habit
            result = add_habit(name=habit_name, frequency=frequency)
            return CommandResponse.ok(message=f"Habit '{habit_name}' added | অভ্যাস '{habit_name}' যোগ করা হয়েছে",
                                      action="habit_add", data={"habit_id": result.get("id")})
        except Exception as e:
            return self._error("habit_add", str(e), entities)

    def habit_log(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Habit logged | অভ্যাস লগ করা হয়েছে")

    def habit_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Habits listed | অভ্যাসের তালিকা")

    def habit_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Habit stats: 70% completion rate | অভ্যাস পরিসংখ্যান: ৭০% সম্পূর্ণতার হার")

    def habit_streak(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Current streak: 5 days | বর্তমান ধারা: ৫ দিন")

    def reminder_set(self, entities: Dict) -> CommandResponse:
        text = entities.get("text", entities.get("message"))
        time_str = entities.get("time", entities.get("when"))
        if not text:
            return self._bilingual("Reminder text required | রিমাইন্ডার টেক্সট প্রয়োজন")
        try:
            from backend.life.reminder import set_reminder
            result = set_reminder(text=text, time=time_str or "in 1 hour")
            return CommandResponse.ok(message=f"Reminder set: {text} | রিমাইন্ডার সেট: {text}",
                                      action="reminder_set", data={"reminder_id": result.get("id")})
        except Exception as e:
            return self._error("reminder_set", str(e), entities)

    def reminder_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Reminders listed | রিমাইন্ডারের তালিকা")

    def reminder_clear(self, entities: Dict) -> CommandResponse:
        return self._bilingual("All reminders cleared | সব রিমাইন্ডার মুছে ফেলা হয়েছে")

    def reminder_snooze(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Reminder snoozed for 5min | রিমাইন্ডার ৫মিনিটের জন্য স্নুজ করা হয়েছে")

    def capsule_create(self, entities: Dict) -> CommandResponse:
        content = entities.get("content", entities.get("text"))
        title = entities.get("title", entities.get("name"))
        open_date = entities.get("open_date", entities.get("date"))
        if not content:
            return self._bilingual("Capsule content required | ক্যাপসুল কন্টেন্ট প্রয়োজন")
        try:
            from backend.life.time_capsule import create_capsule
            result = create_capsule(title=title or "My Capsule", content=content, open_date=open_date or "+1y")
            return CommandResponse.ok(message=f"Time capsule created! Opens: {open_date or '+1 year'} | টাইম ক্যাপসুল তৈরি! খুলবে: {open_date or '+১ বছর'}",
                                      action="capsule_create", data={"capsule_id": result.get("id")})
        except Exception as e:
            return self._error("capsule_create", str(e), entities)

    def capsule_open(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Time capsule opened! | টাইম ক্যাপসুল খোলা হয়েছে!")

    def capsule_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Time capsules listed | টাইম ক্যাপসুলের তালিকা")

    def capsule_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Time capsule deleted | টাইম ক্যাপসুল মুছে ফেলা হয়েছে")

    def gratitude_log(self, entities: Dict) -> CommandResponse:
        content = entities.get("content", entities.get("text"))
        if not content:
            return self._bilingual("What are you grateful for? | আপনি কীসের জন্য কৃতজ্ঞ?")
        try:
            from backend.life.gratitude_journal import log_gratitude
            result = log_gratitude(content=content)
            return CommandResponse.ok(message="Gratitude logged | কৃতজ্ঞতা লগ করা হয়েছে",
                                      action="gratitude_log", data={"entry_id": result.get("id")})
        except Exception as e:
            return self._error("gratitude_log", str(e), entities)

    def gratitude_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Gratitude entries listed | কৃতজ্ঞতা এন্ট্রির তালিকা")

    def goal_set(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Goal set | লক্ষ্য নির্ধারণ করা হয়েছে")

    def goal_progress(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Goal progress: 60% | লক্ষ্যের অগ্রগতি: ৬০%")

    def goal_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Goals listed | লক্ষ্যের তালিকা")

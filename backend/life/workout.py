"""Workout - Workout logging, exercise library, progress tracking."""

import json
import os
from datetime import datetime, timedelta


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class Workout:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.workout_file = os.path.join(self.data_dir, "workout_log.json")
        self.library_file = os.path.join(self.data_dir, "exercise_library.json")
        self._ensure_data_dir()
        self._init_library()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _init_library(self):
        if not os.path.exists(self.library_file):
            default_exercises = [
                {"id": 1, "name": "Push-ups", "category": "strength", "muscle_group": "chest", "calories_per_min": 7},
                {"id": 2, "name": "Squats", "category": "strength", "muscle_group": "legs", "calories_per_min": 8},
                {"id": 3, "name": "Running", "category": "cardio", "muscle_group": "full body", "calories_per_min": 11},
                {"id": 4, "name": "Plank", "category": "core", "muscle_group": "abs", "calories_per_min": 4},
                {"id": 5, "name": "Pull-ups", "category": "strength", "muscle_group": "back", "calories_per_min": 8},
                {"id": 6, "name": "Jumping Jacks", "category": "cardio", "muscle_group": "full body", "calories_per_min": 8},
                {"id": 7, "name": "Lunges", "category": "strength", "muscle_group": "legs", "calories_per_min": 6},
                {"id": 8, "name": "Yoga", "category": "flexibility", "muscle_group": "full body", "calories_per_min": 3},
                {"id": 9, "name": "Cycling", "category": "cardio", "muscle_group": "legs", "calories_per_min": 9},
                {"id": 10, "name": "Dumbbell Curls", "category": "strength", "muscle_group": "arms", "calories_per_min": 5}
            ]
            with open(self.library_file, "w") as f:
                json.dump(default_exercises, f, indent=2)

    def _load_library(self):
        with open(self.library_file, "r") as f:
            return json.load(f)

    def _load_log(self):
        if not os.path.exists(self.workout_file):
            return []
        with open(self.workout_file, "r") as f:
            return json.load(f)

    def _save_log(self, log):
        with open(self.workout_file, "w") as f:
            json.dump(log, f, indent=2)

    def _next_workout_id(self, log):
        return max([w["id"] for w in log], default=0) + 1

    def log_workout(self, exercise_name, duration_minutes, sets=None, reps=None, notes=None):
        if not exercise_name or duration_minutes <= 0:
            raise ValueError("Exercise name and positive duration are required.")
        library = self._load_library()
        exercise = next((e for e in library if e["name"].lower() == exercise_name.lower()), None)
        if exercise is None:
            raise ValueError(f"Exercise '{exercise_name}' not found in library.")
        calories = round(exercise["calories_per_min"] * duration_minutes, 2)
        log = self._load_log()
        entry = {
            "id": self._next_workout_id(log),
            "exercise_name": exercise["name"],
            "category": exercise["category"],
            "muscle_group": exercise["muscle_group"],
            "duration_minutes": duration_minutes,
            "sets": sets,
            "reps": reps,
            "calories_burned": calories,
            "notes": notes or "",
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        log.append(entry)
        self._save_log(log)
        return entry

    def get_exercise_library(self, category=None, muscle_group=None):
        library = self._load_library()
        if category:
            library = [e for e in library if e["category"] == category]
        if muscle_group:
            library = [e for e in library if e["muscle_group"] == muscle_group]
        return library

    def add_exercise_to_library(self, name, category, muscle_group, calories_per_min):
        library = self._load_library()
        new_id = max([e["id"] for e in library], default=0) + 1
        exercise = {
            "id": new_id,
            "name": name,
            "category": category,
            "muscle_group": muscle_group,
            "calories_per_min": calories_per_min
        }
        library.append(exercise)
        with open(self.library_file, "w") as f:
            json.dump(library, f, indent=2)
        return exercise

    def get_workout_history(self, days=None):
        log = self._load_log()
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            log = [w for w in log if w["timestamp"] >= cutoff]
        return log

    def get_progress(self, days=30):
        log = self.get_workout_history(days)
        if not log:
            return {"total_workouts": 0, "total_duration": 0, "total_calories": 0, "average_duration": 0}
        total_workouts = len(log)
        total_duration = sum(w["duration_minutes"] for w in log)
        total_calories = sum(w["calories_burned"] for w in log)
        return {
            "total_workouts": total_workouts,
            "total_duration": round(total_duration, 2),
            "total_calories": round(total_calories, 2),
            "average_duration": round(total_duration / total_workouts, 2) if total_workouts else 0
        }

    def get_workouts_by_date(self, date_str):
        log = self._load_log()
        return [w for w in log if w.get("date") == date_str]

    def delete_workout(self, workout_id):
        log = self._load_log()
        new_log = [w for w in log if w["id"] != workout_id]
        if len(new_log) == len(log):
            raise ValueError(f"Workout with id {workout_id} not found.")
        self._save_log(new_log)
        return {"message": f"Workout {workout_id} deleted."}

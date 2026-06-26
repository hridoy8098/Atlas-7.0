"""LifeReminder - Life reminders with scheduling, categories."""

import json
import os
from datetime import datetime, timedelta
import threading


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class LifeReminder:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.reminder_file = os.path.join(self.data_dir, "reminders.json")
        self._ensure_data_dir()
        self._timers = {}

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_reminders(self):
        if not os.path.exists(self.reminder_file):
            return []
        with open(self.reminder_file, "r") as f:
            return json.load(f)

    def _save_reminders(self, reminders):
        with open(self.reminder_file, "w") as f:
            json.dump(reminders, f, indent=2)

    def _next_id(self, reminders):
        return max([r["id"] for r in reminders], default=0) + 1

    def create_reminder(self, title, description, category, due_at, priority=1):
        if not title or not due_at:
            raise ValueError("Title and due_at are required.")
        categories = ["health", "work", "personal", "finance", "social", "other"]
        if category not in categories:
            raise ValueError(f"Invalid category. Valid: {', '.join(categories)}")
        reminders = self._load_reminders()
        reminder = {
            "id": self._next_id(reminders),
            "title": title,
            "description": description,
            "category": category,
            "due_at": due_at,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        reminders.append(reminder)
        self._save_reminders(reminders)
        return reminder

    def get_reminder(self, reminder_id):
        reminders = self._load_reminders()
        for r in reminders:
            if r["id"] == reminder_id:
                return r
        return None

    def update_reminder(self, reminder_id, **kwargs):
        reminders = self._load_reminders()
        for r in reminders:
            if r["id"] == reminder_id:
                for key, val in kwargs.items():
                    if key in ("title", "description", "category", "due_at", "priority", "completed"):
                        r[key] = val
                self._save_reminders(reminders)
                return r
        raise ValueError(f"Reminder with id {reminder_id} not found.")

    def delete_reminder(self, reminder_id):
        reminders = self._load_reminders()
        new_reminders = [r for r in reminders if r["id"] != reminder_id]
        if len(new_reminders) == len(reminders):
            raise ValueError(f"Reminder with id {reminder_id} not found.")
        self._save_reminders(new_reminders)
        return {"message": f"Reminder {reminder_id} deleted."}

    def list_reminders(self, category=None, completed=None):
        reminders = self._load_reminders()
        if category:
            reminders = [r for r in reminders if r["category"] == category]
        if completed is not None:
            reminders = [r for r in reminders if r["completed"] == completed]
        return sorted(reminders, key=lambda r: r.get("priority", 1), reverse=True)

    def get_due_reminders(self):
        reminders = self._load_reminders()
        now = datetime.now().isoformat()
        return [r for r in reminders if not r["completed"] and r["due_at"] <= now]

    def get_categories(self):
        return ["health", "work", "personal", "finance", "social", "other"]

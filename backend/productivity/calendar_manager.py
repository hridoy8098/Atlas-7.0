import datetime
import json
import os
import uuid


class CalendarManager:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path or "calendar_events.json"
        self.events = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.events = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.events = []

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.events, f, indent=2, default=str)

    def create_event(self, title, start_time, end_time, description="", location=""):
        if not title or not start_time or not end_time:
            raise ValueError("title, start_time, and end_time are required")
        event = {
            "id": str(uuid.uuid4()),
            "title": title,
            "start_time": str(start_time),
            "end_time": str(end_time),
            "description": description,
            "location": location,
            "created_at": str(datetime.datetime.now()),
        }
        self.events.append(event)
        self._save()
        return event

    def get_event(self, event_id):
        for event in self.events:
            if event["id"] == event_id:
                return event
        return None

    def update_event(self, event_id, **kwargs):
        event = self.get_event(event_id)
        if not event:
            raise KeyError(f"Event {event_id} not found")
        for key in ("title", "start_time", "end_time", "description", "location"):
            if key in kwargs:
                event[key] = str(kwargs[key])
        event["updated_at"] = str(datetime.datetime.now())
        self._save()
        return event

    def delete_event(self, event_id):
        event = self.get_event(event_id)
        if not event:
            raise KeyError(f"Event {event_id} not found")
        self.events = [e for e in self.events if e["id"] != event_id]
        self._save()

    def list_events(self, start_date=None, end_date=None):
        if not start_date and not end_date:
            return self.events
        filtered = []
        for event in self.events:
            try:
                event_start = datetime.datetime.fromisoformat(event["start_time"])
                if start_date:
                    s = datetime.datetime.fromisoformat(str(start_date))
                    if event_start < s:
                        continue
                if end_date:
                    e = datetime.datetime.fromisoformat(str(end_date))
                    if event_start > e:
                        continue
                filtered.append(event)
            except (ValueError, TypeError):
                filtered.append(event)
        return filtered

    def add_reminder(self, event_id, minutes_before=15):
        event = self.get_event(event_id)
        if not event:
            raise KeyError(f"Event {event_id} not found")
        if "reminders" not in event:
            event["reminders"] = []
        reminder = {"minutes_before": minutes_before, "triggered": False}
        event["reminders"].append(reminder)
        self._save()
        return reminder

    def get_upcoming_events(self, days=7):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=days)
        return self.list_events(start_date=now, end_date=end)

import datetime
import json
import os
import re
import uuid


class MeetingNotes:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path or "meeting_notes.json"
        self.notes = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.notes = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.notes = []

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.notes, f, indent=2, default=str)

    def create_notes(self, title, content, participants=None, date=None):
        if not title:
            raise ValueError("title is required")
        note = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "participants": participants or [],
            "date": str(date or datetime.date.today()),
            "created_at": str(datetime.datetime.now()),
            "action_items": [],
            "summary": "",
        }
        self.notes.append(note)
        self._save()
        return note

    def get_notes(self, note_id):
        for note in self.notes:
            if note["id"] == note_id:
                return note
        raise KeyError(f"Notes '{note_id}' not found")

    def update_notes(self, note_id, **kwargs):
        note = self.get_notes(note_id)
        for key in ("title", "content", "participants", "date"):
            if key in kwargs:
                note[key] = kwargs[key]
        note["updated_at"] = str(datetime.datetime.now())
        self._save()
        return note

    def delete_notes(self, note_id):
        note = self.get_notes(note_id)
        self.notes = [n for n in self.notes if n["id"] != note_id]
        self._save()

    def list_notes(self):
        return self.notes

    def summarize(self, note_id):
        note = self.get_notes(note_id)
        content = note.get("content", "")
        sentences = re.split(r"[.!?\n]+", content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        if len(sentences) <= 3:
            summary = content[:200]
        else:
            first = sentences[0] if sentences else ""
            mid = sentences[len(sentences) // 2] if len(sentences) > 2 else ""
            last = sentences[-1] if sentences else ""
            summary = ". ".join(filter(None, [first, mid, last])) + "."
        note["summary"] = summary
        self._save()
        return summary

    def extract_action_items(self, note_id):
        note = self.get_notes(note_id)
        content = note.get("content", "")
        patterns = [
            r"(?:action item|todo|to[- ]do|follow[- ]up|need to|must|should)\s*[:：]\s*(.+?)(?:[.\n]|$)",
            r"(?:will|going to|plan to|responsible for)\s+(.+?)(?:[.\n]|$)",
            r"(?:assign(?:ed)? to|owner)\s*[:：]\s*(.+?)(?:[.\n]|$)",
        ]
        items = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            items.extend(m.strip() for m in matches if m.strip())
        note["action_items"] = list(set(items))
        self._save()
        return note["action_items"]

    def search_notes(self, query):
        query_lower = query.lower()
        results = []
        for note in self.notes:
            if (query_lower in note["title"].lower()
                    or query_lower in note["content"].lower()):
                results.append(note)
        return results

    def add_participant(self, note_id, participant):
        note = self.get_notes(note_id)
        if participant not in note["participants"]:
            note["participants"].append(participant)
            self._save()
        return note["participants"]

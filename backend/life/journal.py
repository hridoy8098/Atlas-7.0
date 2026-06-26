"""Journal - Journal entry CRUD with mood tagging, search."""

import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class Journal:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.journal_file = os.path.join(self.data_dir, "journal_entries.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_entries(self):
        if not os.path.exists(self.journal_file):
            return []
        with open(self.journal_file, "r") as f:
            return json.load(f)

    def _save_entries(self, entries):
        with open(self.journal_file, "w") as f:
            json.dump(entries, f, indent=2)

    def _next_id(self, entries):
        return max([e["id"] for e in entries], default=0) + 1

    def create_entry(self, title, content, mood, tags=None):
        if not title or not content:
            raise ValueError("Title and content are required.")
        entries = self._load_entries()
        entry = {
            "id": self._next_id(entries),
            "title": title,
            "content": content,
            "mood": mood,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        entries.append(entry)
        self._save_entries(entries)
        return entry

    def get_entry(self, entry_id):
        entries = self._load_entries()
        for e in entries:
            if e["id"] == entry_id:
                return e
        return None

    def update_entry(self, entry_id, title=None, content=None, mood=None, tags=None):
        entries = self._load_entries()
        for e in entries:
            if e["id"] == entry_id:
                if title is not None:
                    e["title"] = title
                if content is not None:
                    e["content"] = content
                if mood is not None:
                    e["mood"] = mood
                if tags is not None:
                    e["tags"] = tags
                e["updated_at"] = datetime.now().isoformat()
                self._save_entries(entries)
                return e
        raise ValueError(f"Entry with id {entry_id} not found.")

    def delete_entry(self, entry_id):
        entries = self._load_entries()
        new_entries = [e for e in entries if e["id"] != entry_id]
        if len(new_entries) == len(entries):
            raise ValueError(f"Entry with id {entry_id} not found.")
        self._save_entries(new_entries)
        return {"message": f"Entry {entry_id} deleted."}

    def list_entries(self, mood=None, tag=None):
        entries = self._load_entries()
        if mood:
            entries = [e for e in entries if e["mood"] == mood]
        if tag:
            entries = [e for e in entries if tag in e["tags"]]
        return entries

    def search_entries(self, query):
        query = query.lower()
        entries = self._load_entries()
        return [
            e for e in entries
            if query in e["title"].lower() or query in e["content"].lower()
        ]

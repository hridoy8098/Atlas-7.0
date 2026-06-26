"""TimeCapsule - Create and open time capsules with messages."""

import json
import os
import base64
from datetime import datetime, timedelta


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TimeCapsule:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.capsule_file = os.path.join(self.data_dir, "time_capsules.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_capsules(self):
        if not os.path.exists(self.capsule_file):
            return []
        with open(self.capsule_file, "r") as f:
            return json.load(f)

    def _save_capsules(self, capsules):
        with open(self.capsule_file, "w") as f:
            json.dump(capsules, f, indent=2)

    def _next_id(self, capsules):
        return max([c["id"] for c in capsules], default=0) + 1

    def _encode_message(self, message):
        return base64.b64encode(message.encode()).decode()

    def _decode_message(self, encoded):
        return base64.b64decode(encoded).decode()

    def create_capsule(self, title, message, open_date, recipient=None):
        if not title or not message or not open_date:
            raise ValueError("Title, message, and open_date are required.")
        try:
            datetime.strptime(open_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("open_date must be in YYYY-MM-DD format.")
        capsules = self._load_capsules()
        capsule = {
            "id": self._next_id(capsules),
            "title": title,
            "message_encoded": self._encode_message(message),
            "open_date": open_date,
            "recipient": recipient,
            "created_at": datetime.now().isoformat(),
            "opened": False,
            "opened_at": None
        }
        capsules.append(capsule)
        self._save_capsules(capsules)
        return {
            "id": capsule["id"],
            "title": capsule["title"],
            "open_date": capsule["open_date"],
            "recipient": capsule["recipient"],
            "created_at": capsule["created_at"]
        }

    def open_capsule(self, capsule_id):
        capsules = self._load_capsules()
        for c in capsules:
            if c["id"] == capsule_id:
                now = datetime.now()
                open_dt = datetime.strptime(c["open_date"], "%Y-%m-%d")
                if now < open_dt:
                    days_left = (open_dt - now).days
                    raise ValueError(f"Capsule not ready. {days_left} days remaining until {c['open_date']}.")
                c["opened"] = True
                c["opened_at"] = now.isoformat()
                self._save_capsules(capsules)
                return {
                    "id": c["id"],
                    "title": c["title"],
                    "message": self._decode_message(c["message_encoded"]),
                    "recipient": c["recipient"],
                    "created_at": c["created_at"],
                    "opened_at": c["opened_at"]
                }
        raise ValueError(f"Capsule with id {capsule_id} not found.")

    def list_capsules(self, include_opened=False):
        capsules = self._load_capsules()
        result = []
        for c in capsules:
            if c["opened"] and not include_opened:
                continue
            result.append({
                "id": c["id"],
                "title": c["title"],
                "open_date": c["open_date"],
                "recipient": c["recipient"],
                "created_at": c["created_at"],
                "opened": c["opened"]
            })
        return result

    def get_capsule_status(self, capsule_id):
        capsules = self._load_capsules()
        for c in capsules:
            if c["id"] == capsule_id:
                open_dt = datetime.strptime(c["open_date"], "%Y-%m-%d")
                now = datetime.now()
                return {
                    "id": c["id"],
                    "title": c["title"],
                    "open_date": c["open_date"],
                    "opened": c["opened"],
                    "available": now >= open_dt,
                    "days_until_open": max((open_dt - now).days, 0)
                }
        raise ValueError(f"Capsule with id {capsule_id} not found.")

    def delete_capsule(self, capsule_id):
        capsules = self._load_capsules()
        new_capsules = [c for c in capsules if c["id"] != capsule_id]
        if len(new_capsules) == len(capsules):
            raise ValueError(f"Capsule with id {capsule_id} not found.")
        self._save_capsules(new_capsules)
        return {"message": f"Capsule {capsule_id} deleted."}

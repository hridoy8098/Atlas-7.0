import math
from datetime import datetime, timedelta


class SpacedRepetition:
    def __init__(self):
        self.items = {}
        self.next_id = 1
        self.review_log = []

    def add_item(self, front, back, tags=None, initial_interval=1):
        if not front or not back:
            raise ValueError("front and back are required")
        item_id = self.next_id
        self.next_id += 1
        self.items[item_id] = {
            "id": item_id,
            "front": front,
            "back": back,
            "tags": tags or [],
            "repetitions": 0,
            "easiness": 2.5,
            "interval": initial_interval,
            "next_review": datetime.now(),
            "last_review": None,
            "correct_streak": 0,
        }
        return item_id

    def get_item(self, item_id):
        if item_id not in self.items:
            raise KeyError(f"Item '{item_id}' not found")
        return self.items[item_id]

    def delete_item(self, item_id):
        if item_id not in self.items:
            raise KeyError(f"Item '{item_id}' not found")
        del self.items[item_id]

    def search_items(self, query):
        q = query.lower()
        return [
            it for it in self.items.values()
            if q in it["front"].lower() or q in it["back"].lower()
        ]

    def _sm2(self, item, quality):
        if quality < 0 or quality > 5:
            raise ValueError("quality must be 0-5")
        item["last_review"] = datetime.now()
        item["repetitions"] += 1
        if quality < 3:
            item["repetitions"] = 0
            item["interval"] = 1
            item["correct_streak"] = 0
        else:
            item["correct_streak"] += 1
            if item["repetitions"] == 1:
                item["interval"] = 1
            elif item["repetitions"] == 2:
                item["interval"] = 6
            else:
                item["interval"] = round(item["interval"] * item["easiness"])
        item["easiness"] = max(
            1.3,
            item["easiness"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        item["next_review"] = item["last_review"] + timedelta(days=item["interval"])
        return item

    def review(self, item_id, quality):
        if item_id not in self.items:
            raise KeyError(f"Item '{item_id}' not found")
        item = self._sm2(self.items[item_id], quality)
        log_entry = {
            "item_id": item_id,
            "quality": quality,
            "timestamp": datetime.now().isoformat(),
            "interval": item["interval"],
            "easiness": item["easiness"],
        }
        self.review_log.append(log_entry)
        return item

    def get_due_items(self, limit=None):
        now = datetime.now()
        due = [it for it in self.items.values() if it["next_review"] <= now]
        due.sort(key=lambda x: x["next_review"])
        if limit:
            return due[:limit]
        return due

    def get_due_count(self):
        return len(self.get_due_items())

    def get_upcoming_items(self, days=7):
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        return [
            it for it in self.items.values()
            if now < it["next_review"] <= cutoff
        ]

    def get_stats(self):
        items = self.items.values()
        if not items:
            return {
                "total": 0,
                "due": 0,
                "average_easiness": 0.0,
                "mastered": 0,
            }
        return {
            "total": len(items),
            "due": self.get_due_count(),
            "average_easiness": round(sum(it["easiness"] for it in items) / len(items), 2),
            "mastered": sum(1 for it in items if it["interval"] >= 21),
        }

    def schedule_batch_review(self, min_quality=3):
        results = []
        for item in self.get_due_items():
            results.append(self._sm2(item, min_quality))
        return results

    def get_review_history(self, item_id=None):
        if item_id:
            return [log for log in self.review_log if log["item_id"] == item_id]
        return self.review_log

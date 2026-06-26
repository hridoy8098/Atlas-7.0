import json
from datetime import datetime, timedelta


class Flashcard:
    def __init__(self):
        self.cards = {}
        self.categories = {}
        self.next_id = 1

    def add_category(self, category_id, name, description=""):
        if not category_id or not name:
            raise ValueError("category_id and name are required")
        if category_id in self.categories:
            raise ValueError(f"Category '{category_id}' already exists")
        self.categories[category_id] = {
            "id": category_id,
            "name": name,
            "description": description,
            "card_count": 0,
        }
        return True

    def remove_category(self, category_id):
        if category_id not in self.categories:
            raise KeyError(f"Category '{category_id}' not found")
        ids_to_remove = [cid for cid, c in self.cards.items() if c["category"] == category_id]
        for cid in ids_to_remove:
            del self.cards[cid]
        del self.categories[category_id]

    def add_card(self, front, back, category=None, tags=None):
        if not front or not back:
            raise ValueError("front and back are required")
        if category and category not in self.categories:
            raise KeyError(f"Category '{category}' not found")
        card_id = self.next_id
        self.next_id += 1
        self.cards[card_id] = {
            "id": card_id,
            "front": front,
            "back": back,
            "category": category,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "review_count": 0,
            "last_reviewed": None,
            "next_review": datetime.now().isoformat(),
            "interval": 1,
            "ease": 2.5,
        }
        if category:
            self.categories[category]["card_count"] += 1
        return card_id

    def get_card(self, card_id):
        if card_id not in self.cards:
            raise KeyError(f"Card '{card_id}' not found")
        return self.cards[card_id]

    def update_card(self, card_id, front=None, back=None, category=None, tags=None):
        if card_id not in self.cards:
            raise KeyError(f"Card '{card_id}' not found")
        card = self.cards[card_id]
        if front is not None:
            card["front"] = front
        if back is not None:
            card["back"] = back
        if category is not None:
            if category not in self.categories:
                raise KeyError(f"Category '{category}' not found")
            old_cat = card.get("category")
            if old_cat and old_cat in self.categories:
                self.categories[old_cat]["card_count"] -= 1
            card["category"] = category
            self.categories[category]["card_count"] += 1
        if tags is not None:
            card["tags"] = tags

    def delete_card(self, card_id):
        if card_id not in self.cards:
            raise KeyError(f"Card '{card_id}' not found")
        cat = self.cards[card_id].get("category")
        if cat and cat in self.categories:
            self.categories[cat]["card_count"] -= 1
        del self.cards[card_id]

    def get_cards_by_category(self, category):
        if category not in self.categories:
            raise KeyError(f"Category '{category}' not found")
        return [c for c in self.cards.values() if c["category"] == category]

    def get_cards_by_tag(self, tag):
        return [c for c in self.cards.values() if tag in c["tags"]]

    def search_cards(self, query):
        q = query.lower()
        return [
            c for c in self.cards.values()
            if q in c["front"].lower() or q in c["back"].lower()
        ]

    def review_card(self, card_id, quality):
        if card_id not in self.cards:
            raise KeyError(f"Card '{card_id}' not found")
        if quality < 0 or quality > 5:
            raise ValueError("quality must be between 0 and 5")
        card = self.cards[card_id]
        card["review_count"] += 1
        card["last_reviewed"] = datetime.now().isoformat()
        if quality < 3:
            card["interval"] = 1
            card["ease"] = max(1.3, card["ease"] - 0.2)
        else:
            if card["interval"] == 1:
                card["interval"] = 6
            else:
                card["interval"] = round(card["interval"] * card["ease"])
            card["ease"] = min(3.0, card["ease"] + (quality - 3) * 0.15)
        card["next_review"] = (datetime.now() + timedelta(days=card["interval"])).isoformat()
        return card

    def get_due_cards(self):
        now = datetime.now().isoformat()
        return [c for c in self.cards.values() if c["next_review"] <= now]

    def get_stats(self):
        return {
            "total_cards": len(self.cards),
            "total_categories": len(self.categories),
            "due_cards": len(self.get_due_cards()),
        }

    def export_json(self, filepath):
        data = {"cards": self.cards, "categories": self.categories, "next_id": self.next_id}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def import_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.cards.update(data.get("cards", {}))
        self.categories.update(data.get("categories", {}))
        self.next_id = max(self.next_id, data.get("next_id", 1))

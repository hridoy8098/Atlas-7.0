"""User behavior modeling and preference learning module."""

import json
from datetime import datetime
from typing import Optional
from collections import defaultdict, Counter


class DigitalTwin:
    """Models user behavior, learns preferences, and builds a digital twin profile."""

    def __init__(self, user_id: str, storage_path: Optional[str] = None):
        if not user_id or not user_id.strip():
            raise ValueError("user_id must be a non-empty string.")
        self.user_id = user_id.strip()
        self.storage_path = storage_path or f"digital_twin_{self.user_id}.json"
        self.profile: dict = self._default_profile()
        self._load()

    def _default_profile(self) -> dict:
        return {
            "user_id": self.user_id,
            "preferences": {},
            "behavior_history": [],
            "learned_traits": {},
            "interaction_count": 0,
            "last_updated": datetime.utcnow().isoformat(),
        }

    def _load(self) -> None:
        """Load profile from storage."""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                if data.get("user_id") == self.user_id:
                    self.profile = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.profile = self._default_profile()

    def _save(self) -> None:
        """Persist profile to storage."""
        self.profile["last_updated"] = datetime.utcnow().isoformat()
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.profile, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save digital twin profile: {e}")

    def record_interaction(self, action: str, category: str, metadata: Optional[dict] = None) -> dict:
        """Record a user interaction event.

        Args:
            action: The action performed (e.g. 'click', 'view', 'purchase').
            category: Category of the action (e.g. 'music', 'news', 'shopping').
            metadata: Optional contextual data.

        Returns:
            The interaction record.
        """
        if not action or not category:
            raise ValueError("action and category must not be empty.")

        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.strip().lower(),
            "category": category.strip().lower(),
            "metadata": metadata or {},
        }
        self.profile["behavior_history"].append(interaction)
        self.profile["interaction_count"] += 1
        self._update_preferences(interaction)
        self._save()
        return interaction

    def _update_preferences(self, interaction: dict) -> None:
        """Update learned preferences based on interaction."""
        cat = interaction["category"]
        if cat not in self.profile["preferences"]:
            self.profile["preferences"][cat] = {"count": 0, "actions": Counter()}
        self.profile["preferences"][cat]["count"] += 1
        self.profile["preferences"][cat]["actions"][interaction["action"]] += 1

    def get_preferences(self, min_interactions: int = 1) -> dict:
        """Get learned user preferences sorted by interaction frequency.

        Args:
            min_interactions: Minimum interaction count to include a category.

        Returns:
            Sorted dictionary of preference categories and their stats.
        """
        prefs = {}
        for cat, data in self.profile.get("preferences", {}).items():
            if data["count"] >= min_interactions:
                prefs[cat] = {
                    "interaction_count": data["count"],
                    "top_actions": dict(
                        Counter(data["actions"]).most_common(5)
                    ),
                }
        return dict(sorted(prefs.items(), key=lambda x: x[1]["interaction_count"], reverse=True))

    def recommend_categories(self, top_n: int = 5) -> list[str]:
        """Recommend top categories based on interaction frequency.

        Args:
            top_n: Number of categories to recommend.

        Returns:
            List of recommended category names.
        """
        prefs = self.get_preferences()
        return list(prefs.keys())[:top_n]

    def get_behavior_summary(self) -> dict:
        """Get a summary of user behavior patterns.

        Returns:
            Dictionary with total interactions, top categories, and action distribution.
        """
        all_actions: Counter = Counter()
        for interaction in self.profile.get("behavior_history", []):
            all_actions[interaction["action"]] += 1

        return {
            "user_id": self.user_id,
            "total_interactions": self.profile["interaction_count"],
            "top_categories": self.recommend_categories(10),
            "action_distribution": dict(all_actions.most_common()),
            "last_updated": self.profile["last_updated"],
        }

    def learn_trait(self, trait_name: str, value: float) -> dict:
        """Store or update a learned personality/behavior trait.

        Args:
            trait_name: Name of the trait (e.g. 'curiosity', 'patience').
            value: Numeric value representing the trait strength (0.0 - 1.0).

        Returns:
            Updated learned_traits dictionary.
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError("Trait value must be between 0.0 and 1.0.")
        self.profile["learned_traits"][trait_name.strip().lower()] = round(value, 4)
        self._save()
        return dict(self.profile["learned_traits"])

    def get_profile_snapshot(self) -> dict:
        """Get a complete snapshot of the digital twin profile.

        Returns:
            Full profile dictionary.
        """
        return {
            "user_id": self.profile["user_id"],
            "preferences": self.get_preferences(),
            "learned_traits": dict(self.profile.get("learned_traits", {})),
            "interaction_count": self.profile["interaction_count"],
            "last_updated": self.profile["last_updated"],
        }

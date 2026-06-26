"""Learns user personality traits over time through interaction analysis."""

import json
from datetime import datetime
from typing import Optional
from collections import Counter


class PersonalityLearning:
    """Analyzes user interactions to learn and model personality traits over time.

    Traits are updated incrementally based on observed behaviors, sentiment,
    and communication patterns.
    """

    # Big Five personality dimensions and their observable indicators
    TRAIT_INDICATORS = {
        "openness": {
            "keywords": {"creative", "curious", "explore", "imagine", "novel",
                         "discover", "adventure", "experiment", "idea", "art"},
            "inverse_keywords": {"routine", "traditional", "conventional", "predictable"},
        },
        "conscientiousness": {
            "keywords": {"organize", "plan", "schedule", "complete", "achieve",
                         "discipline", "thorough", "precise", "efficient", "deadline"},
            "inverse_keywords": {"messy", "chaotic", "procrastinate", "careless"},
        },
        "extraversion": {
            "keywords": {"social", "party", "friend", "together", "talk",
                         "meet", "group", "collaborate", "celebrate", "outgoing"},
            "inverse_keywords": {"quiet", "alone", "solitary", "introvert", "peaceful"},
        },
        "agreeableness": {
            "keywords": {"help", "kind", "support", "cooperate", "understand",
                         "empathy", "care", "share", "trust", "polite"},
            "inverse_keywords": {"argue", "criticize", "selfish", "competitive"},
        },
        "neuroticism": {
            "keywords": {"worry", "anxious", "stress", "nervous", "fear",
                         "upset", "frustrate", "overwhelmed", "tense", "mood"},
            "inverse_keywords": {"calm", "relaxed", "secure", "stable", "confident"},
        },
    }

    def __init__(self, user_id: str, storage_path: Optional[str] = None):
        if not user_id or not user_id.strip():
            raise ValueError("user_id must be a non-empty string.")
        self.user_id = user_id.strip()
        self.storage_path = storage_path or f"personality_{self.user_id}.json"
        self.traits: dict[str, float] = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5,
        }
        self.interaction_count = 0
        self._load()

    def _load(self) -> None:
        """Load personality data from storage."""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                if data.get("user_id") == self.user_id:
                    self.traits = data.get("traits", self.traits)
                    self.interaction_count = data.get("interaction_count", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save(self) -> None:
        """Persist personality data to storage."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump({
                    "user_id": self.user_id,
                    "traits": self.traits,
                    "interaction_count": self.interaction_count,
                    "last_updated": datetime.utcnow().isoformat(),
                }, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save personality data: {e}")

    def _update_trait(self, trait: str, delta: float) -> None:
        """Adjust a single trait value, clamping to [0, 1]."""
        current = self.traits.get(trait, 0.5)
        self.traits[trait] = max(0.0, min(1.0, current + delta))

    def analyze_text(self, text: str) -> dict:
        """Analyze a text utterance and update personality traits.

        Args:
            text: User's spoken or written text.

        Returns:
            Dict of per-trait score adjustments applied.
        """
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")

        words = set(text.lower().split())
        adjustments = {}

        for trait, indicators in self.TRAIT_INDICATORS.items():
            pos_hits = sum(1 for kw in indicators["keywords"] if kw in words)
            neg_hits = sum(1 for kw in indicators["inverse_keywords"] if kw in words)
            net = (pos_hits - neg_hits) * 0.02
            if net != 0:
                self._update_trait(trait, net)
                adjustments[trait] = round(net, 4)

        self.interaction_count += 1
        self._save()
        return adjustments

    def get_traits(self) -> dict[str, float]:
        """Get the current personality trait scores.

        Returns:
            Dictionary of trait name to score (0.0 - 1.0).
        """
        return dict(self.traits)

    def get_dominant_traits(self, top_n: int = 3) -> list[tuple[str, float]]:
        """Get the strongest personality traits.

        Args:
            top_n: Number of top traits to return.

        Returns:
            List of (trait_name, score) tuples sorted descending.
        """
        sorted_traits = sorted(self.traits.items(), key=lambda x: x[1], reverse=True)
        return sorted_traits[:top_n]

    def get_personality_summary(self) -> dict:
        """Get a human-readable summary of the user's personality profile.

        Returns:
            Summary with dominant traits, balance, and interaction count.
        """
        dominant = self.get_dominant_traits(2)
        labels = {
            "openness": ("Open to new experiences", "Resistant to change"),
            "conscientiousness": ("Organized and disciplined", "Flexible and spontaneous"),
            "extraversion": ("Outgoing and social", "Introverted and reserved"),
            "agreeableness": ("Cooperative and compassionate", "Competitive and challenging"),
            "neuroticism": ("Sensitive and prone to stress", "Emotionally stable"),
        }

        descriptions = []
        for trait, score in dominant:
            high = score > 0.55
            low = score < 0.45
            if high:
                descriptions.append(labels.get(trait, (trait, trait))[0])
            elif low:
                descriptions.append(labels.get(trait, (trait, trait))[1])

        return {
            "user_id": self.user_id,
            "traits": self.get_traits(),
            "dominant_traits": descriptions,
            "interaction_count": self.interaction_count,
        }

    def merge_traits(self, other_traits: dict[str, float], weight: float = 0.3) -> dict[str, float]:
        """Merge externally provided trait estimates into the learned profile.

        Args:
            other_traits: Dict of trait_name -> score from another source.
            weight: Blending weight for the external estimate (0.0 - 1.0).

        Returns:
            Updated trait dictionary.
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0.")

        for trait, score in other_traits.items():
            if trait in self.traits:
                blended = (1 - weight) * self.traits[trait] + weight * max(0.0, min(1.0, score))
                self.traits[trait] = round(blended, 4)

        self._save()
        return self.get_traits()

"""Dream logging, analysis, pattern detection, and recall module."""

import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Optional


class AtlasDreams:
    """Handles dream logging, analysis, pattern detection, and recall."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "dreams_store.json"
        self.dreams: list[dict] = []
        self._load()

    def _load(self) -> None:
        """Load dreams from storage file."""
        try:
            with open(self.storage_path, "r") as f:
                self.dreams = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.dreams = []

    def _save(self) -> None:
        """Persist dreams to storage file."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.dreams, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save dreams: {e}")

    def log_dream(self, description: str, emotions: list[str], tags: Optional[list[str]] = None) -> dict:
        """Log a new dream entry.

        Args:
            description: Narrative of the dream.
            emotions: List of emotions experienced in the dream.
            tags: Optional categorical tags.

        Returns:
            The created dream record.
        """
        if not description or not description.strip():
            raise ValueError("Dream description cannot be empty.")
        record = {
            "id": len(self.dreams) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "description": description.strip(),
            "emotions": emotions or [],
            "tags": tags or [],
        }
        self.dreams.append(record)
        self._save()
        return record

    def analyze_themes(self) -> dict:
        """Detect recurring themes, emotions, and patterns across all dreams.

        Returns:
            A dictionary with theme frequency, emotion frequency, and top tags.
        """
        if not self.dreams:
            return {"themes": {}, "emotions": {}, "tags": {}}

        emotion_counter: Counter = Counter()
        tag_counter: Counter = Counter()
        keyword_counter: Counter = Counter()

        stop_words = {"the", "a", "an", "i", "me", "my", "we", "our", "you",
                      "he", "she", "it", "they", "them", "is", "was", "were",
                      "be", "been", "being", "have", "has", "had", "do", "does",
                      "did", "but", "and", "or", "if", "because", "as", "until",
                      "while", "of", "at", "by", "for", "with", "about", "against",
                      "between", "into", "through", "during", "before", "after",
                      "above", "below", "to", "from", "up", "down", "in", "out",
                      "on", "off", "over", "under", "again", "further", "then",
                      "once", "here", "there", "all", "each", "every", "both",
                      "few", "more", "most", "other", "some", "such", "no", "nor",
                      "not", "only", "own", "same", "so", "than", "too", "very",
                      "just", "also", "now"}

        for dream in self.dreams:
            for em in dream.get("emotions", []):
                emotion_counter[em.lower()] += 1
            for tag in dream.get("tags", []):
                tag_counter[tag.lower()] += 1

            words = dream.get("description", "").lower().split()
            for word in words:
                word = word.strip(".,!?;:'\"()[]{}")
                if word and word not in stop_words and len(word) > 3:
                    keyword_counter[word] += 1

        return {
            "emotions": dict(emotion_counter.most_common()),
            "tags": dict(tag_counter.most_common()),
            "common_keywords": dict(keyword_counter.most_common(20)),
            "total_dreams": len(self.dreams),
        }

    def get_recent_dreams(self, days: int = 7) -> list[dict]:
        """Retrieve dreams from the last N days.

        Args:
            days: Number of days to look back.

        Returns:
            List of dream records within the time window.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = []
        for dream in self.dreams:
            try:
                dt = datetime.fromisoformat(dream["timestamp"])
                if dt >= cutoff:
                    recent.append(dream)
            except (ValueError, KeyError):
                continue
        return recent

    def search_dreams(self, query: str) -> list[dict]:
        """Search dreams by keyword in description or emotions.

        Args:
            query: Search term.

        Returns:
            Matching dream records.
        """
        q = query.lower()
        results = []
        for dream in self.dreams:
            if q in dream.get("description", "").lower():
                results.append(dream)
            elif any(q in em.lower() for em in dream.get("emotions", [])):
                results.append(dream)
            elif any(q in tag.lower() for tag in dream.get("tags", [])):
                results.append(dream)
        return results

    def get_dream_by_id(self, dream_id: int) -> Optional[dict]:
        """Retrieve a specific dream by its ID.

        Args:
            dream_id: The dream record ID.

        Returns:
            The dream record or None if not found.
        """
        for dream in self.dreams:
            if dream.get("id") == dream_id:
                return dream
        return None

    def delete_dream(self, dream_id: int) -> bool:
        """Delete a dream record by ID.

        Args:
            dream_id: The dream record ID.

        Returns:
            True if deleted, False if not found.
        """
        for i, dream in enumerate(self.dreams):
            if dream.get("id") == dream_id:
                del self.dreams[i]
                self._save()
                return True
        return False

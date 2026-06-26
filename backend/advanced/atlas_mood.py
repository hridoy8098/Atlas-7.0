"""Mood tracking, trends, and sentiment analysis module."""

import json
from datetime import datetime, timedelta
from typing import Optional
from collections import Counter


class AtlasMood:
    """Tracks user mood over time, analyzes trends, and performs sentiment analysis."""

    MOOD_SCALE = {
        "very_happy": 5,
        "happy": 4,
        "neutral": 3,
        "sad": 2,
        "very_sad": 1,
        "angry": 1,
        "anxious": 2,
        "calm": 4,
    }

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "mood_store.json"
        self.entries: list[dict] = []
        self._load()

    def _load(self) -> None:
        """Load mood entries from storage."""
        try:
            with open(self.storage_path, "r") as f:
                self.entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.entries = []

    def _save(self) -> None:
        """Persist mood entries to storage."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.entries, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save mood data: {e}")

    def log_mood(self, mood: str, note: Optional[str] = None, score: Optional[int] = None) -> dict:
        """Log a mood entry.

        Args:
            mood: Mood label (e.g. 'happy', 'sad', 'anxious').
            note: Optional context note.
            score: Optional numeric score (1-5). Auto-derived from mood if omitted.

        Returns:
            The created mood record.
        """
        mood_key = mood.strip().lower()
        if mood_key not in self.MOOD_SCALE:
            raise ValueError(f"Unknown mood '{mood}'. Valid moods: {list(self.MOOD_SCALE.keys())}")

        entry = {
            "id": len(self.entries) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "mood": mood_key,
            "score": score if score is not None else self.MOOD_SCALE[mood_key],
            "note": note or "",
        }
        self.entries.append(entry)
        self._save()
        return entry

    def get_trend(self, days: int = 30) -> dict:
        """Calculate mood trend over a given period.

        Args:
            days: Number of days to analyze.

        Returns:
            Dictionary with average score, mood distribution, and trend direction.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = []
        for e in self.entries:
            try:
                dt = datetime.fromisoformat(e["timestamp"])
                if dt >= cutoff:
                    recent.append(e)
            except (ValueError, KeyError):
                continue

        if not recent:
            return {"average_score": 0, "mood_distribution": {}, "trend": "insufficient_data", "count": 0}

        scores = [e.get("score", 3) for e in recent]
        avg = sum(scores) / len(scores)

        mood_counter: Counter = Counter()
        for e in recent:
            mood_counter[e.get("mood", "neutral")] += 1

        # Simple trend: compare first half vs second half
        mid = len(scores) // 2
        first_half = sum(scores[:mid]) / mid if mid > 0 else avg
        second_half = sum(scores[mid:]) / (len(scores) - mid) if (len(scores) - mid) > 0 else avg
        delta = second_half - first_half

        if delta > 0.3:
            trend = "improving"
        elif delta < -0.3:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "average_score": round(avg, 2),
            "mood_distribution": dict(mood_counter.most_common()),
            "trend": trend,
            "count": len(recent),
        }

    def analyze_sentiment(self, text: str) -> dict:
        """Perform basic sentiment analysis on a text string.

        Args:
            text: Input text to analyze.

        Returns:
            Sentiment polarity, score, and key emotional words found.
        """
        positive_words = {
            "happy", "joy", "love", "great", "amazing", "wonderful", "excellent",
            "good", "beautiful", "fantastic", "awesome", "grateful", "hopeful",
            "excited", "peaceful", "calm", "content", "thrilled", "delighted",
        }
        negative_words = {
            "sad", "angry", "upset", "terrible", "horrible", "awful", "bad",
            "hate", "pain", "hurt", "lonely", "depressed", "anxious", "afraid",
            "worried", "stressed", "frustrated", "disappointed", "miserable",
        }

        words = text.lower().split()
        found_pos = [w for w in words if w.strip(".,!?;:'\"") in positive_words]
        found_neg = [w for w in words if w.strip(".,!?;:'\"") in negative_words]

        pos_score = len(found_pos)
        neg_score = len(found_neg)
        total = pos_score + neg_score

        if total == 0:
            polarity = "neutral"
            normalized = 0.0
        elif pos_score > neg_score:
            polarity = "positive"
            normalized = round(pos_score / total, 2)
        elif neg_score > pos_score:
            polarity = "negative"
            normalized = round(-neg_score / total, 2)
        else:
            polarity = "neutral"
            normalized = 0.0

        return {
            "polarity": polarity,
            "score": normalized,
            "positive_words": found_pos,
            "negative_words": found_neg,
            "word_count": len(words),
        }

    def get_mood_by_date(self, date: str) -> list[dict]:
        """Retrieve mood entries for a specific date (YYYY-MM-DD).

        Args:
            date: Date string in ISO format (YYYY-MM-DD).

        Returns:
            List of mood entries from that date.
        """
        results = []
        for e in self.entries:
            try:
                entry_date = datetime.fromisoformat(e["timestamp"]).strftime("%Y-%m-%d")
                if entry_date == date:
                    results.append(e)
            except (ValueError, KeyError):
                continue
        return results

    def get_recent_moods(self, limit: int = 10) -> list[dict]:
        """Get the most recent mood entries.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Latest mood entries sorted by timestamp descending.
        """
        sorted_entries = sorted(
            self.entries,
            key=lambda e: e.get("timestamp", ""),
            reverse=True,
        )
        return sorted_entries[:limit]

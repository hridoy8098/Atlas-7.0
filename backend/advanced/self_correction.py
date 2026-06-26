"""Error detection, auto-correction, and feedback loop module."""

import json
import re
from datetime import datetime
from typing import Optional
from collections import defaultdict


class SelfCorrection:
    """Detects errors in AI outputs, applies auto-correction rules,
    and maintains a feedback loop for continuous improvement.
    """

    # Built-in correction rules: (error_pattern, correction)
    DEFAULT_RULES = [
        (r"\bteh\b", "the"),
        (r"\brecieve\b", "receive"),
        (r"\bacheive\b", "achieve"),
        (r"\bseperate\b", "separate"),
        (r"\bdefinately\b", "definitely"),
        (r"\boccured\b", "occurred"),
        (r"\bcalender\b", "calendar"),
        (r"\bwierd\b", "weird"),
        (r"\bneccessary\b", "necessary"),
        (r"\btruely\b", "truly"),
        (r"\byield\b", "field"),
    ]

    def __init__(self, rules_path: Optional[str] = None, history_path: Optional[str] = None):
        self.rules_path = rules_path or "correction_rules.json"
        self.history_path = history_path or "correction_history.json"
        self.rules: list[tuple[str, str]] = list(self.DEFAULT_RULES)
        self.history: list[dict] = []
        self.feedback_stats: dict[str, int] = defaultdict(int)
        self._load_rules()
        self._load_history()

    def _load_rules(self) -> None:
        """Load custom correction rules from storage."""
        try:
            with open(self.rules_path, "r") as f:
                custom = json.load(f)
                if isinstance(custom, list):
                    for item in custom:
                        if isinstance(item, dict) and "pattern" in item and "replacement" in item:
                            self.rules.append((item["pattern"], item["replacement"]))
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save_rules(self) -> None:
        """Persist custom rules to storage."""
        try:
            custom = [{"pattern": p, "replacement": r} for p, r in self.rules[len(self.DEFAULT_RULES):]]
            with open(self.rules_path, "w") as f:
                json.dump(custom, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save correction rules: {e}")

    def _load_history(self) -> None:
        """Load correction history from storage."""
        try:
            with open(self.history_path, "r") as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []

    def _save_history(self) -> None:
        """Persist correction history to storage."""
        try:
            with open(self.history_path, "w") as f:
                json.dump(self.history, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save correction history: {e}")

    def correct(self, text: str, context: Optional[dict] = None) -> dict:
        """Apply all correction rules to the input text.

        Args:
            text: The text to correct.
            context: Optional metadata about the source (e.g. {"module": "chat", "user_id": "abc"}).

        Returns:
            Dict with original text, corrected text, list of changes, and change count.
        """
        if not text:
            return {"original": text, "corrected": text, "changes": [], "change_count": 0}

        corrected = text
        changes = []

        for pattern, replacement in self.rules:
            matches = list(re.finditer(pattern, corrected, re.IGNORECASE))
            for match in reversed(matches):
                start, end = match.start(), match.end()
                original_word = corrected[start:end]
                # Preserve case
                if original_word[0].isupper() and replacement[0].islower():
                    replacement_word = replacement.capitalize()
                elif original_word.isupper():
                    replacement_word = replacement.upper()
                else:
                    replacement_word = replacement

                corrected = corrected[:start] + replacement_word + corrected[end:]
                changes.append({
                    "original": original_word,
                    "replacement": replacement_word,
                    "pattern": pattern,
                })

        # Remove duplicate changes on same position
        seen = set()
        unique_changes = []
        for c in changes:
            key = (c["original"], c["replacement"])
            if key not in seen:
                seen.add(key)
                unique_changes.append(c)

        # Also detect duplicate words (e.g. "the the")
        dup_pattern = r"\b(\w+)\s+\1\b"
        for match in re.finditer(dup_pattern, corrected):
            corrected = corrected[:match.start()] + match.group(1) + corrected[match.end():]
            unique_changes.append({
                "original": match.group(0),
                "replacement": match.group(1),
                "pattern": "duplicate_word",
            })

        record = {
            "id": len(self.history) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "original": text,
            "corrected": corrected,
            "change_count": len(unique_changes),
            "changes": unique_changes,
            "context": context or {},
        }
        self.history.append(record)
        self.feedback_stats["total_corrections"] += len(unique_changes)
        self.feedback_stats["total_processed"] += 1
        self._save_history()

        return {
            "original": text,
            "corrected": corrected,
            "changes": unique_changes,
            "change_count": len(unique_changes),
        }

    def add_rule(self, pattern: str, replacement: str) -> None:
        """Add a custom correction rule.

        Args:
            pattern: Regex pattern to match.
            replacement: Replacement string.
        """
        if not pattern or not replacement:
            raise ValueError("Pattern and replacement must not be empty.")
        # Validate regex
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

        self.rules.append((pattern, replacement))
        self._save_rules()

    def remove_rule(self, pattern: str) -> bool:
        """Remove a custom correction rule (cannot remove built-in defaults).

        Args:
            pattern: The regex pattern to remove.

        Returns:
            True if removed, False if not found or is a default rule.
        """
        for i, (p, _) in enumerate(self.rules[len(self.DEFAULT_RULES):], start=len(self.DEFAULT_RULES)):
            if p == pattern:
                del self.rules[i]
                self._save_rules()
                return True
        return False

    def get_rules(self) -> list[dict]:
        """Get all active correction rules.

        Returns:
            List of rule dicts with pattern, replacement, and origin (built-in/custom).
        """
        result = []
        for i, (p, r) in enumerate(self.rules):
            result.append({
                "id": i + 1,
                "pattern": p,
                "replacement": r,
                "origin": "built-in" if i < len(self.DEFAULT_RULES) else "custom",
            })
        return result

    def get_stats(self) -> dict:
        """Get summary statistics of the correction system.

        Returns:
            Dict with counts of total processed, corrections applied, rules, and history size.
        """
        return {
            "total_processed": self.feedback_stats["total_processed"],
            "total_corrections": self.feedback_stats["total_corrections"],
            "active_rules": len(self.rules),
            "built_in_rules": len(self.DEFAULT_RULES),
            "custom_rules": len(self.rules) - len(self.DEFAULT_RULES),
            "history_entries": len(self.history),
        }

    def get_recent_corrections(self, limit: int = 20) -> list[dict]:
        """Get the most recent correction records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of the latest correction records.
        """
        return list(reversed(self.history[-limit:]))

    def provide_feedback(self, correction_id: int, accepted: bool) -> bool:
        """Provide feedback on whether a correction was helpful.

        Args:
            correction_id: ID of the correction record.
            accepted: True if correction was accepted, False if rejected.

        Returns:
            True if feedback was recorded, False if correction_id not found.
        """
        for record in self.history:
            if record.get("id") == correction_id:
                record["feedback"] = {"accepted": accepted, "timestamp": datetime.utcnow().isoformat()}
                key = "accepted_corrections" if accepted else "rejected_corrections"
                self.feedback_stats[key] += 1
                self._save_history()
                return True
        return False

    def clear_history(self) -> None:
        """Clear all correction history."""
        self.history.clear()
        self.feedback_stats.clear()
        self._save_history()

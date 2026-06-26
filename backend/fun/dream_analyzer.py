import random
import re


class DreamAnalyzer:
    """Dream interpretation and analysis using symbolic meanings."""

    def __init__(self):
        self.symbols = {
            "water": "Emotions, the unconscious, purification, or change.",
            "flying": "Freedom, ambition, desire to escape, or high aspirations.",
            "falling": "Fear of failure, loss of control, or insecurity.",
            "teeth": "Anxiety about appearance, powerlessness, or communication issues.",
            "chase": "Avoiding a problem, fear, or unresolved conflict.",
            "house": "The self, different floors represent different aspects of personality.",
            "snake": "Transformation, hidden fears, healing, or temptation.",
            "death": "End of a phase, transformation, new beginnings.",
            "baby": "New start, innocence, vulnerability, or potential.",
            "ocean": "Vast emotions, the subconscious, mystery, depth.",
            "forest": "The unknown, growth, exploration, or being lost.",
            "fire": "Passion, destruction, transformation, or anger.",
            "rain": "Sadness, renewal, cleansing, or emotional release.",
            "bridge": "Transition, connection, or overcoming an obstacle.",
            "door": "Opportunity, new possibilities, or a barrier.",
        }
        self.interpretation_history = []

    def analyze_dream(self, description: str) -> dict:
        if not description or not isinstance(description, str):
            raise ValueError("Dream description must be a non-empty string.")
        text = description.lower()
        found = {}
        for symbol, meaning in self.symbols.items():
            if symbol in text:
                found[symbol] = meaning
        if not found:
            found["unrecognized"] = "No common symbols detected. This dream may be highly personal."
        interpretation = {
            "description": description[:200],
            "symbols_identified": list(found.keys()),
            "meanings": found,
            "overall": self._generate_overall(found),
            "mood": self._assess_mood(text),
        }
        self.interpretation_history.append(interpretation)
        return interpretation

    def _generate_overall(self, symbols_found: dict) -> str:
        if not symbols_found:
            return "Consider keeping a dream journal to identify recurring themes."
        templates = [
            "Your dream suggests themes of {theme}.",
            "This dream may reflect your subconscious thoughts about {theme}.",
            "The symbols point toward {theme} in your waking life.",
        ]
        theme = " and ".join(list(symbols_found.keys())[:3])
        return random.choice(templates).format(theme=theme)

    def _assess_mood(self, text: str) -> str:
        positive = {"happy", "joy", "peace", "love", "calm", "beautiful", "free"}
        negative = {"scared", "fear", "sad", "angry", "anxious", "fall", "chase", "dark"}
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    def add_symbol(self, symbol: str, meaning: str) -> str:
        if not symbol or not meaning:
            raise ValueError("Symbol and meaning must be non-empty strings.")
        self.symbols[symbol.strip().lower()] = meaning.strip()
        return f"Symbol '{symbol}' added with meaning: {meaning}"

    def get_symbol(self, symbol: str) -> str:
        key = symbol.strip().lower()
        return self.symbols.get(key, f"No known meaning for symbol '{symbol}'.")

    def list_symbols(self) -> list:
        return list(self.symbols.keys())

    def get_interpretation_history(self) -> list:
        return list(self.interpretation_history)

    def clear_history(self) -> str:
        self.interpretation_history.clear()
        return "Interpretation history cleared."

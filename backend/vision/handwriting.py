"""Handwriting recognition and analysis."""

import re
from collections import Counter


class Handwriting:
    """Recognize and analyze handwriting from text or stroke data."""

    def __init__(self):
        self.text = ""
        self.strokes = []
        self.words = []

    def load_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        self.text = text
        self.words = re.findall(r"\b\w+\b", text.lower())

    def load_strokes(self, strokes: list) -> None:
        if not isinstance(strokes, list):
            raise TypeError("strokes must be a list of point sequences")
        self.strokes = strokes

    def recognize(self) -> dict:
        if self.text:
            return {"text": self.text, "word_count": len(self.words), "method": "text_input"}
        if self.strokes:
            return {"text": "mock_recognition_result", "method": "stroke_analysis"}
        return {"text": "", "method": "none", "error": "no input data"}

    def analyze_legibility(self) -> dict:
        if not self.words:
            return {"score": 0.0, "issues": ["no_data"]}
        avg_len = sum(len(w) for w in self.words) / len(self.words)
        unique = len(set(self.words))
        variety = unique / len(self.words) if self.words else 0
        score = min(1.0, (avg_len / 10) * 0.5 + variety * 0.5)
        issues = []
        if score < 0.4:
            issues.append("short_words")
        if variety < 0.3:
            issues.append("low_vocabulary")
        return {"legibility_score": round(score, 2), "issues": issues}

    def detect_emotion(self) -> dict:
        if not self.words:
            return {"emotion": "neutral", "confidence": 0.0}
        positive = {"happy", "love", "great", "good", "wonderful", "excellent", "amazing", "fantastic"}
        negative = {"sad", "angry", "hate", "bad", "terrible", "awful", "horrible", "depressed"}
        pos_count = sum(1 for w in self.words if w in positive)
        neg_count = sum(1 for w in self.words if w in negative)
        if pos_count > neg_count:
            return {"emotion": "positive", "confidence": round(pos_count / (pos_count + neg_count + 1), 2)}
        elif neg_count > pos_count:
            return {"emotion": "negative", "confidence": round(neg_count / (pos_count + neg_count + 1), 2)}
        return {"emotion": "neutral", "confidence": 0.6}

    def get_writing_style(self) -> dict:
        if not self.words:
            return {"style": "unknown"}
        total_chars = sum(len(w) for w in self.words)
        avg_word_len = round(total_chars / len(self.words), 2) if self.words else 0
        sentences = re.split(r"[.!?]+", self.text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_len = round(sum(len(s.split()) for s in sentences) / len(sentences), 1) if sentences else 0
        return {
            "style": "cursive" if avg_word_len > 6 else "print",
            "avg_word_length": avg_word_len,
            "avg_sentence_length": avg_sentence_len,
            "total_words": len(self.words),
        }

    def summarize(self) -> dict:
        return {
            "recognition": self.recognize(),
            "legibility": self.analyze_legibility(),
            "emotion": self.detect_emotion(),
            "style": self.get_writing_style(),
        }

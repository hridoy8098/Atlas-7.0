import math
import re
from collections import Counter


class Summarizer:
    def __init__(self, language="english"):
        self.language = language
        self._stop_words = self._get_stop_words()

    def _get_stop_words(self):
        return {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "by", "with", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can", "need",
            "dare", "ought", "used", "this", "that", "these", "those", "it",
            "its", "he", "she", "they", "we", "you", "i", "me", "him", "her",
            "them", "us", "my", "your", "his", "its", "our", "their", "not",
            "no", "nor", "so", "if", "then", "than", "too", "very", "just",
            "about", "above", "after", "again", "all", "also", "any", "because",
            "before", "between", "both", "each", "few", "more", "most", "other",
            "some", "such", "only", "own", "same", "into", "over", "under",
            "up", "out", "off", "down", "here", "there", "when", "where", "why",
            "how", "which", "who", "whom", "what",
        }

    def extractive_summarize(self, text, num_sentences=5):
        if not text or not text.strip():
            return ""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        if len(sentences) <= num_sentences:
            return " ".join(sentences)

        word_freq = Counter()
        for sentence in sentences:
            words = re.findall(r"\w+", sentence.lower())
            for word in words:
                if word not in self._stop_words:
                    word_freq[word] += 1

        max_freq = max(word_freq.values()) if word_freq else 1
        for word in word_freq:
            word_freq[word] /= max_freq

        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = re.findall(r"\w+", sentence.lower())
            score = sum(word_freq.get(word, 0) for word in words)
            sentence_scores[i] = score / (len(words) + 1)

        ranked = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_indices = sorted([idx for idx, _ in ranked[:num_sentences]])
        summary = " ".join(sentences[idx] for idx in top_indices)
        return summary

    def abstractive_summarize(self, text, max_length=150):
        if not text or not text.strip():
            return ""
        extractive = self.extractive_summarize(text, num_sentences=3)
        if len(extractive) <= max_length:
            return extractive
        words = extractive.split()
        while len(" ".join(words)) > max_length and len(words) > 1:
            words.pop()
        return " ".join(words) + "."

    def summarize_by_ratio(self, text, ratio=0.3):
        if not text or not text.strip():
            return ""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        num_sentences = max(1, math.ceil(len(sentences) * ratio))
        return self.extractive_summarize(text, num_sentences)

    def keyword_summary(self, text, top_n=10):
        words = re.findall(r"\w+", text.lower())
        words = [w for w in words if w not in self._stop_words and len(w) > 2]
        freq = Counter(words)
        return freq.most_common(top_n)

    def sentence_count(self, text):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return len([s for s in sentences if s.strip()])

    def word_count(self, text):
        return len(re.findall(r"\w+", text))

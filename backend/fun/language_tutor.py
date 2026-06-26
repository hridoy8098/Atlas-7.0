import random


class LanguageTutor:
    """Language learning with translations, vocabulary, and quizzes."""

    def __init__(self):
        self.vocabulary = {}
        self.languages = set()
        self.quiz_history = []
        self.translations_served = 0

    def add_vocabulary(self, word: str, translation: str, language: str = "unknown") -> str:
        if not word or not translation:
            raise ValueError("Word and translation must be non-empty strings.")
        word = word.strip().lower()
        self.vocabulary[word] = {
            "translation": translation.strip(),
            "language": language.strip(),
        }
        self.languages.add(language.strip())
        return f"Added: {word} -> {translation} ({language})"

    def add_vocabulary_batch(self, word_pairs: list) -> str:
        if not word_pairs:
            raise ValueError("Word pairs list must not be empty.")
        count = 0
        for pair in word_pairs:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                lang = pair[2] if len(pair) > 2 else "unknown"
                self.add_vocabulary(pair[0], pair[1], lang)
                count += 1
        return f"Added {count} vocabulary entries."

    def translate(self, text: str, source_lang: str = "", target_lang: str = "") -> dict:
        if not text:
            raise ValueError("Text must be non-empty.")
        text_lower = text.strip().lower()
        lookup = self.vocabulary.get(text_lower)
        if lookup:
            self.translations_served += 1
            return {
                "original": text.strip(),
                "translation": lookup["translation"],
                "language": lookup["language"],
                "source": "vocabulary",
            }
        self.translations_served += 1
        return {
            "original": text.strip(),
            "translation": f"[{target_lang or 'target'} translation of '{text.strip()}']",
            "language": target_lang or "unknown",
            "source": "auto",
        }

    def get_vocabulary(self, language: str = "") -> list:
        if language:
            return [
                {"word": w, **details}
                for w, details in self.vocabulary.items()
                if details["language"] == language
            ]
        return [{"word": w, **details} for w, details in self.vocabulary.items()]

    def get_languages(self) -> list:
        return sorted(self.languages)

    def quiz(self, count: int = 5) -> list:
        if count < 1:
            raise ValueError("Count must be at least 1.")
        available = list(self.vocabulary.items())
        if len(available) < count:
            count = len(available)
        if count == 0:
            return [{"error": "No vocabulary available. Add words first."}]
        selected = random.sample(available, count)
        questions = []
        for word, details in selected:
            wrong = random.sample(
                [v["translation"] for k, v in self.vocabulary.items() if k != word],
                min(3, len(self.vocabulary) - 1),
            )
            options = [details["translation"]] + wrong
            random.shuffle(options)
            questions.append({
                "word": word,
                "correct": details["translation"],
                "options": options,
                "language": details["language"],
            })
        self.quiz_history.append({"count": count, "questions": questions})
        return questions

    def get_progress(self) -> dict:
        return {
            "vocabulary_count": len(self.vocabulary),
            "languages": sorted(self.languages),
            "translations_served": self.translations_served,
            "quizzes_taken": len(self.quiz_history),
        }

    def remove_word(self, word: str) -> str:
        key = word.strip().lower()
        if key in self.vocabulary:
            del self.vocabulary[key]
            return f"Removed '{word}' from vocabulary."
        return f"Word '{word}' not found."

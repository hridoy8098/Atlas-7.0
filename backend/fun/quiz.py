import random


class QuizEngine:
    """Quiz engine with multiple categories, scoring, and progress tracking."""

    def __init__(self):
        self.categories = {}
        self.current_category = ""
        self.current_questions = []
        self.current_index = 0
        self.score = 0
        self.total = 0
        self.history = []

    def add_category(self, name: str, questions: list) -> str:
        if not name or not isinstance(name, str):
            raise ValueError("Category name must be a non-empty string.")
        if not questions or not isinstance(questions, list):
            raise ValueError("Questions must be a non-empty list.")
        for q in questions:
            if "question" not in q or "options" not in q or "answer" not in q:
                raise ValueError(
                    "Each question must have 'question', 'options', and 'answer' keys."
                )
            if q["answer"] not in q["options"]:
                raise ValueError(f"Answer must be one of the options for: {q['question']}")
        self.categories[name.strip()] = questions
        return f"Category '{name}' added with {len(questions)} questions."

    def get_categories(self) -> list:
        return list(self.categories.keys())

    def get_question_count(self, category: str) -> int:
        cat = self.categories.get(category.strip())
        if cat is None:
            raise ValueError(f"Category '{category}' not found.")
        return len(cat)

    def start_quiz(self, category: str, question_count: int = 0) -> dict:
        cat_name = category.strip()
        if cat_name not in self.categories:
            raise ValueError(f"Category '{category}' not found.")
        pool = list(self.categories[cat_name])
        if question_count and question_count < len(pool):
            pool = random.sample(pool, min(question_count, len(pool)))
        random.shuffle(pool)
        self.current_category = cat_name
        self.current_questions = pool
        self.current_index = 0
        self.score = 0
        self.total = len(pool)
        return {
            "category": cat_name,
            "total_questions": self.total,
            "started": True,
        }

    def answer_question(self, answer: str) -> dict:
        if self.current_index >= self.total:
            raise RuntimeError("Quiz is already complete. Start a new quiz.")
        q = self.current_questions[self.current_index]
        correct = q["answer"]
        is_correct = answer.strip().lower() == correct.strip().lower()
        if is_correct:
            self.score += 1
        result = {
            "question": q["question"],
            "your_answer": answer.strip(),
            "correct_answer": correct,
            "is_correct": is_correct,
            "question_number": self.current_index + 1,
            "total": self.total,
        }
        self.current_index += 1
        result["completed"] = self.current_index >= self.total
        self.history.append(result)
        return result

    def get_current_question(self) -> dict:
        if self.current_index >= self.total:
            return {"message": "Quiz completed.", "completed": True}
        q = self.current_questions[self.current_index]
        return {
            "question": q["question"],
            "options": q["options"],
            "question_number": self.current_index + 1,
            "total": self.total,
        }

    def get_score(self) -> dict:
        return {
            "score": self.score,
            "total": self.total,
            "percentage": round((self.score / self.total * 100), 1) if self.total else 0,
        }

    def get_progress(self) -> dict:
        return {
            "category": self.current_category,
            "answered": self.current_index,
            "total": self.total,
            "remaining": self.total - self.current_index,
            "score": self.score,
        }

    def get_history(self) -> list:
        return list(self.history)

    def reset(self) -> str:
        self.current_category = ""
        self.current_questions.clear()
        self.current_index = 0
        self.score = 0
        self.total = 0
        return "Quiz engine reset."

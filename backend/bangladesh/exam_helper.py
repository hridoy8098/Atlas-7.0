class ExamHelper:
    """Bangladesh education exam helper with past questions."""

    def __init__(self):
        self._questions = {
            "bangla": [
                {"id": 1, "question": "'পারিবারিক' শব্দের সন্ধি বিচ্ছেদ কী?", "answer": "পরিবার + ইক"},
                {"id": 2, "question": "'সূর্য' শব্দের প্রতিশব্দ কী?", "answer": "রবি, আদিত্য, দিবাকর"},
                {"id": 3, "question": "'অহনা' শব্দের অর্থ কী?", "answer": "দিন"},
            ],
            "english": [
                {"id": 4, "question": "What is the past tense of 'go'?", "answer": "went"},
                {"id": 5, "question": "Choose the correct spelling.", "answer": "accommodation"},
                {"id": 6, "question": "What is a synonym for 'beautiful'?", "answer": "gorgeous"},
            ],
            "math": [
                {"id": 7, "question": "x^2 - 5x + 6 = 0 এর সমাধান কী?", "answer": "x = 2, 3"},
                {"id": 8, "question": "৫ এবং ৭ এর ল.সা.গু. কত?", "answer": "৩৫"},
                {"id": 9, "question": "একটি ত্রিভুজের তিন কোণের সমষ্টি কত?", "answer": "১৮০ ডিগ্রি"},
            ],
            "science": [
                {"id": 10, "question": "পানির রাসায়নিক সংকেত কী?", "answer": "H2O"},
                {"id": 11, "question": "সালফিউরিক অ্যাসিডের সংকেত কী?", "answer": "H2SO4"},
            ],
            "bangladesh_studies": [
                {"id": 12, "question": "বাংলাদেশের স্বাধীনতা দিবস কবে?", "answer": "২৬ মার্চ"},
                {"id": 13, "question": "বাংলাদেশের জাতীয় ফল কী?", "answer": "কাঁঠাল"},
            ],
        }

    def get_questions(self, subject, grade=None):
        subject = subject.lower().strip()
        if subject not in self._questions:
            raise ValueError(f"Subject '{subject}' not found. Available: {self.list_subjects()}")
        questions = self._questions[subject]
        if grade is not None:
            questions = [q for q in questions if q.get("grade") == grade]
        return list(questions)

    def get_answer(self, question_id):
        for subject, questions in self._questions.items():
            for q in questions:
                if q["id"] == question_id:
                    return q["answer"]
        raise ValueError(f"Question with id {question_id} not found")

    def search_questions(self, keyword):
        keyword = keyword.lower().strip()
        if not keyword:
            raise ValueError("Keyword must not be empty")
        results = []
        for subject, questions in self._questions.items():
            for q in questions:
                if keyword in q["question"].lower() or keyword in q.get("answer", "").lower():
                    results.append({**q, "subject": subject})
        return results

    def add_question(self, subject, question, answer, question_id=None):
        subject = subject.lower().strip()
        if not question or not answer:
            raise ValueError("Question and answer must not be empty")
        if subject not in self._questions:
            self._questions[subject] = []
        new_id = question_id if question_id is not None else (
            max((q["id"] for subs in self._questions.values() for q in subs), default=0) + 1
        )
        self._questions[subject].append({"id": new_id, "question": question, "answer": answer})
        return new_id

    def list_subjects(self):
        return list(self._questions.keys())

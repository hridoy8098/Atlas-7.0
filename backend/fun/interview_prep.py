class InterviewPrep:
    """Interview preparation with common questions, answers, and tips."""

    def __init__(self):
        self.position = ""
        self.questions = {
            "Tell me about yourself.": (
                "Give a brief summary of your background, key achievements, "
                "and why you are interested in this role."
            ),
            "What are your strengths?": (
                "Mention 2-3 strengths relevant to the job with concrete examples."
            ),
            "What are your weaknesses?": (
                "Be honest about a real weakness and explain steps you are taking to improve."
            ),
            "Why do you want to work here?": (
                "Research the company and connect your values/skills to their mission."
            ),
            "Where do you see yourself in 5 years?": (
                "Show ambition and alignment with the company's growth trajectory."
            ),
            "Tell me about a time you faced a challenge.": (
                "Use the STAR method: Situation, Task, Action, Result."
            ),
            "Why should we hire you?": (
                "Highlight what sets you apart and how you can add value."
            ),
            "Describe your ideal work environment.": (
                "Be honest but align it with the company culture."
            ),
        }
        self.custom_questions = {}
        self.tips = [
            "Research the company thoroughly before the interview.",
            "Prepare examples using the STAR method.",
            "Dress appropriately for the company culture.",
            "Prepare 2-3 thoughtful questions to ask the interviewer.",
            "Practice good posture and eye contact.",
            "Follow up with a thank-you email within 24 hours.",
            "Arrive 10-15 minutes early.",
            "Bring extra copies of your resume.",
            "Listen carefully and ask for clarification if needed.",
            "Be honest and authentic in your responses.",
        ]
        self.progress = {"questions_reviewed": 0, "questions_practiced": 0}

    def set_position(self, position: str) -> str:
        if not position or not isinstance(position, str):
            raise ValueError("Position must be a non-empty string.")
        self.position = position.strip()
        return f"Position set to: {self.position}"

    def get_common_questions(self) -> dict:
        return dict(self.questions)

    def get_tips(self) -> list:
        return list(self.tips)

    def add_custom_question(self, question: str, answer: str) -> str:
        if not question or not answer:
            raise ValueError("Question and answer must be non-empty strings.")
        self.custom_questions[question.strip()] = answer.strip()
        self.progress["questions_reviewed"] += 1
        return f"Custom question added: {question[:60]}..."

    def practice_question(self, question: str) -> dict:
        if not question:
            raise ValueError("Question must be a non-empty string.")
        q = question.strip()
        answer = self.custom_questions.get(q) or self.questions.get(q)
        if not answer:
            return {
                "question": q,
                "answer": None,
                "tips": "Try relating this to your personal experience.",
            }
        self.progress["questions_practiced"] += 1
        return {"question": q, "answer": str(answer), "tips": "Use specific examples from your experience."}

    def add_tip(self, tip: str) -> str:
        if not tip:
            raise ValueError("Tip must be non-empty.")
        self.tips.append(tip.strip())
        return "Tip added."

    def get_progress(self) -> dict:
        return dict(self.progress)

    def reset(self) -> str:
        self.position = ""
        self.custom_questions.clear()
        self.progress = {"questions_reviewed": 0, "questions_practiced": 0}
        return "InterviewPrep has been reset."

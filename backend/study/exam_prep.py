import random
from datetime import datetime


class ExamPrep:
    def __init__(self):
        self.topics = {}
        self.questions = []
        self.exam_results = []
        self.study_sessions = []

    def add_topic(self, topic_id, name, content="", difficulty="medium"):
        if not topic_id or not name:
            raise ValueError("topic_id and name are required")
        if difficulty not in ("easy", "medium", "hard"):
            raise ValueError("difficulty must be easy, medium, or hard")
        self.topics[topic_id] = {
            "id": topic_id,
            "name": name,
            "content": content,
            "difficulty": difficulty,
            "created": datetime.now().isoformat(),
            "reviews": 0,
            "mastery": 0.0,
        }
        return True

    def remove_topic(self, topic_id):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        del self.topics[topic_id]
        self.questions = [q for q in self.questions if q.get("topic") != topic_id]

    def update_topic_content(self, topic_id, content):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        self.topics[topic_id]["content"] = content

    def add_question(self, question, answer, topic_id, difficulty="medium", options=None):
        if not question or not answer:
            raise ValueError("question and answer are required")
        if topic_id and topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        q = {
            "id": len(self.questions) + 1,
            "question": question,
            "answer": answer,
            "topic": topic_id,
            "difficulty": difficulty,
            "options": options or [],
            "created": datetime.now().isoformat(),
        }
        self.questions.append(q)
        return q["id"]

    def get_questions_by_topic(self, topic_id, count=None):
        filtered = [q for q in self.questions if q.get("topic") == topic_id]
        if not filtered:
            raise ValueError(f"No questions found for topic '{topic_id}'")
        if count:
            filtered = random.sample(filtered, min(count, len(filtered)))
        return filtered

    def get_questions_by_difficulty(self, difficulty, count=None):
        filtered = [q for q in self.questions if q["difficulty"] == difficulty]
        if not filtered:
            raise ValueError(f"No questions found with difficulty '{difficulty}'")
        if count:
            filtered = random.sample(filtered, min(count, len(filtered)))
        return filtered

    def generate_practice_test(self, num_questions=10, topic_ids=None):
        pool = self.questions
        if topic_ids:
            pool = [q for q in self.questions if q.get("topic") in topic_ids]
        if not pool:
            raise ValueError("No questions available for practice test")
        selected = random.sample(pool, min(num_questions, len(pool)))
        return selected

    def record_result(self, topic_id, score, total):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        result = {
            "topic_id": topic_id,
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 2) if total else 0,
            "timestamp": datetime.now().isoformat(),
        }
        self.exam_results.append(result)
        topic = self.topics[topic_id]
        topic["reviews"] += 1
        topic["mastery"] = round(
            (topic["mastery"] * (topic["reviews"] - 1) + result["percentage"]) / topic["reviews"], 2
        )
        return result

    def get_topic_mastery(self, topic_id):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        return self.topics[topic_id]["mastery"]

    def get_weak_topics(self, threshold=50.0):
        return [
            t for t in self.topics.values()
            if t["mastery"] < threshold and t["reviews"] > 0
        ]

    def start_study_session(self, topic_ids=None):
        session = {
            "id": len(self.study_sessions) + 1,
            "topics": topic_ids or list(self.topics.keys()),
            "started": datetime.now().isoformat(),
            "completed": None,
        }
        self.study_sessions.append(session)
        return session

    def end_study_session(self, session_id):
        for s in self.study_sessions:
            if s["id"] == session_id:
                s["completed"] = datetime.now().isoformat()
                return s
        raise ValueError(f"Study session '{session_id}' not found")

    def review_topic(self, topic_id):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        topic = self.topics[topic_id]
        questions = self.get_questions_by_topic(topic_id)
        return {"topic": topic, "questions": questions}

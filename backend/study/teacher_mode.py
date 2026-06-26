import random
from datetime import datetime


class TeacherMode:
    def __init__(self):
        self.topics = {}
        self.quizzes = {}
        self.lesson_plans = {}
        self.explanations = {}
        self.next_quiz_id = 1

    def add_topic(self, topic_id, name, summary="", key_points=None, examples=None):
        if not topic_id or not name:
            raise ValueError("topic_id and name are required")
        self.topics[topic_id] = {
            "id": topic_id,
            "name": name,
            "summary": summary,
            "key_points": key_points or [],
            "examples": examples or [],
            "created": datetime.now().isoformat(),
        }
        return True

    def remove_topic(self, topic_id):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        del self.topics[topic_id]

    def update_topic(self, topic_id, summary=None, key_points=None, examples=None):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        t = self.topics[topic_id]
        if summary is not None:
            t["summary"] = summary
        if key_points is not None:
            t["key_points"] = key_points
        if examples is not None:
            t["examples"] = examples

    def explain_topic(self, topic_id, style="simple"):
        if topic_id not in self.topics:
            raise KeyError(f"Topic '{topic_id}' not found")
        if style not in ("simple", "detailed", "analogy"):
            raise ValueError("style must be simple, detailed, or analogy")
        t = self.topics[topic_id]
        if style == "simple":
            explanation = f"{t['name']}: {t['summary']}\n\nKey points:\n"
            explanation += "\n".join(f"- {p}" for p in t["key_points"])
        elif style == "detailed":
            explanation = f"=== {t['name']} (Detailed) ===\n\n{t['summary']}\n\n"
            explanation += "Core concepts:\n"
            explanation += "\n".join(f"{i+1}. {p}" for i, p in enumerate(t["key_points"]))
            if t["examples"]:
                explanation += "\n\nExamples:\n"
                explanation += "\n".join(f"- {e}" for e in t["examples"])
        else:
            explanation = f"Analogy for {t['name']}:\n"
            explanation += f"Think of it this way: {t['summary']}\n\n"
            if t["examples"]:
                explanation += "Related example:\n" + t["examples"][0]
        self.explanations[topic_id] = {
            "topic_id": topic_id,
            "style": style,
            "content": explanation,
            "timestamp": datetime.now().isoformat(),
        }
        return explanation

    def generate_quiz(self, topic_ids, num_questions=5, title=None):
        if not topic_ids:
            raise ValueError("At least one topic_id is required")
        available = []
        for tid in topic_ids:
            if tid not in self.topics:
                raise KeyError(f"Topic '{tid}' not found")
            pts = self.topics[tid]["key_points"]
            for pt in pts:
                available.append({"topic": tid, "point": pt})
        if not available:
            raise ValueError("No key points available to generate quiz questions")
        selected = random.sample(available, min(num_questions, len(available)))
        quiz_id = self.next_quiz_id
        self.next_quiz_id += 1
        questions = []
        for i, item in enumerate(selected):
            topic_name = self.topics[item["topic"]]["name"]
            correct = item["point"]
            distractors = self._generate_distractors(item["topic"], correct)
            options = distractors[:3]
            options.insert(random.randint(0, len(options)), correct)
            questions.append({
                "id": i + 1,
                "question": f"Which of the following is a key point about {topic_name}?",
                "options": options,
                "correct_answer": correct,
                "topic": item["topic"],
            })
        title = title or f"Quiz on {', '.join(self.topics[t]['name'] for t in topic_ids)}"
        self.quizzes[quiz_id] = {
            "id": quiz_id,
            "title": title,
            "topic_ids": topic_ids,
            "questions": questions,
            "created": datetime.now().isoformat(),
        }
        return self.quizzes[quiz_id]

    def _generate_distractors(self, topic_id, correct_point):
        distractors = []
        for tid, t in self.topics.items():
            for pt in t["key_points"]:
                if pt != correct_point and len(distractors) < 3:
                    distractors.append(pt)
        while len(distractors) < 3:
            distractors.append(f"Related concept #{len(distractors) + 1}")
        return distractors

    def get_quiz(self, quiz_id):
        if quiz_id not in self.quizzes:
            raise KeyError(f"Quiz '{quiz_id}' not found")
        return self.quizzes[quiz_id]

    def grade_quiz(self, quiz_id, answers):
        if quiz_id not in self.quizzes:
            raise KeyError(f"Quiz '{quiz_id}' not found")
        quiz = self.quizzes[quiz_id]
        results = []
        correct_count = 0
        for q in quiz["questions"]:
            user_answer = answers.get(str(q["id"]), "")
            is_correct = user_answer == q["correct_answer"]
            if is_correct:
                correct_count += 1
            results.append({
                "question_id": q["id"],
                "question": q["question"],
                "user_answer": user_answer,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
            })
        return {
            "quiz_id": quiz_id,
            "total": len(quiz["questions"]),
            "correct": correct_count,
            "score": round((correct_count / len(quiz["questions"])) * 100, 2) if quiz["questions"] else 0,
            "results": results,
        }

    def create_lesson_plan(self, topic_ids, duration_minutes=60):
        if not topic_ids:
            raise ValueError("At least one topic_id is required")
        for tid in topic_ids:
            if tid not in self.topics:
                raise KeyError(f"Topic '{tid}' not found")
        plan_id = len(self.lesson_plans) + 1
        sections = []
        minutes_per_topic = duration_minutes // len(topic_ids)
        for tid in topic_ids:
            t = self.topics[tid]
            sections.append({
                "topic_id": tid,
                "topic_name": t["name"],
                "duration": minutes_per_topic,
                "activities": [
                    f"Introduction to {t['name']}",
                    "Review key points",
                    "Discussion and examples",
                    "Q&A session",
                ],
            })
        self.lesson_plans[plan_id] = {
            "id": plan_id,
            "topic_ids": topic_ids,
            "total_duration": duration_minutes,
            "sections": sections,
            "created": datetime.now().isoformat(),
        }
        return self.lesson_plans[plan_id]

    def get_lesson_plan(self, plan_id):
        if plan_id not in self.lesson_plans:
            raise KeyError(f"Lesson plan '{plan_id}' not found")
        return self.lesson_plans[plan_id]

    def list_topics(self):
        return [{"id": t["id"], "name": t["name"]} for t in self.topics.values()]

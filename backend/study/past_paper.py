import json
from datetime import datetime


class PastPaper:
    def __init__(self):
        self.papers = {}
        self.next_id = 1

    def add_paper(self, title, subject, year, exam_board=None, description="", questions=None):
        if not title or not subject or not year:
            raise ValueError("title, subject, and year are required")
        paper_id = self.next_id
        self.next_id += 1
        self.papers[paper_id] = {
            "id": paper_id,
            "title": title,
            "subject": subject,
            "year": int(year),
            "exam_board": exam_board,
            "description": description,
            "questions": questions or [],
            "created": datetime.now().isoformat(),
        }
        return paper_id

    def get_paper(self, paper_id):
        if paper_id not in self.papers:
            raise KeyError(f"Paper '{paper_id}' not found")
        return self.papers[paper_id]

    def update_paper(self, paper_id, title=None, subject=None, year=None, exam_board=None, description=None):
        if paper_id not in self.papers:
            raise KeyError(f"Paper '{paper_id}' not found")
        p = self.papers[paper_id]
        if title:
            p["title"] = title
        if subject:
            p["subject"] = subject
        if year is not None:
            p["year"] = int(year)
        if exam_board is not None:
            p["exam_board"] = exam_board
        if description is not None:
            p["description"] = description
        return p

    def delete_paper(self, paper_id):
        if paper_id not in self.papers:
            raise KeyError(f"Paper '{paper_id}' not found")
        del self.papers[paper_id]

    def filter_by_subject(self, subject):
        return [p for p in self.papers.values() if p["subject"].lower() == subject.lower()]

    def filter_by_year(self, year):
        return [p for p in self.papers.values() if p["year"] == int(year)]

    def filter_by_year_range(self, start_year, end_year):
        return [
            p for p in self.papers.values()
            if start_year <= p["year"] <= end_year
        ]

    def filter_by_exam_board(self, exam_board):
        return [
            p for p in self.papers.values()
            if p.get("exam_board") and p["exam_board"].lower() == exam_board.lower()
        ]

    def search_papers(self, query):
        q = query.lower()
        return [
            p for p in self.papers.values()
            if q in p["title"].lower() or q in p["subject"].lower() or q in p["description"].lower()
        ]

    def add_question_to_paper(self, paper_id, question, answer, marks=None):
        if paper_id not in self.papers:
            raise KeyError(f"Paper '{paper_id}' not found")
        q = {
            "id": len(self.papers[paper_id]["questions"]) + 1,
            "question": question,
            "answer": answer,
            "marks": marks,
        }
        self.papers[paper_id]["questions"].append(q)
        return q["id"]

    def list_subjects(self):
        return sorted(set(p["subject"] for p in self.papers.values()))

    def list_years(self):
        return sorted(set(p["year"] for p in self.papers.values()), reverse=True)

    def get_stats(self):
        return {
            "total_papers": len(self.papers),
            "subjects": len(self.list_subjects()),
            "years_range": (
                min(self.list_years()) if self.papers else None,
                max(self.list_years()) if self.papers else None,
            ),
        }

    def export_json(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.papers, f, indent=2)

    def import_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.papers.update(data)
        if data:
            self.next_id = max(int(k) for k in data.keys()) + 1

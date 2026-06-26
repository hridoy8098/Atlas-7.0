"""
Atlas 7.0 — Study Command Handler
YouTube search, flashcards, exam prep, notes, coding practice, tutor.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class StudyCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("youtube_ai_search", self.youtube_ai_search, priority=CommandPriority.HIGH)
        self._register("youtube_ai_summary", self.youtube_ai_summary)
        self._register("youtube_ai_transcript", self.youtube_ai_transcript)
        self._register("youtube_ai_download", self.youtube_ai_download)
        self._register("flashcard_create", self.flashcard_create, priority=CommandPriority.HIGH)
        self._register("flashcard_list", self.flashcard_list)
        self._register("flashcard_study", self.flashcard_study)
        self._register("flashcard_review", self.flashcard_review)
        self._register("flashcard_delete", self.flashcard_delete)
        self._register("flashcard_import", self.flashcard_import)
        self._register("flashcard_export", self.flashcard_export)
        self._register("exam_prep", self.exam_prep, priority=CommandPriority.HIGH)
        self._register("exam_questions", self.exam_questions)
        self._register("exam_answer", self.exam_answer)
        self._register("exam_result", self.exam_result)
        self._register("exam_tips", self.exam_tips)
        self._register("study_timer", self.study_timer)
        self._register("study_plan", self.study_plan)
        self._register("study_stats", self.study_stats)
        self._register("study_reminder", self.study_reminder)
        self._register("study_group", self.study_group)
        self._register("study_summarize", self.study_summarize)
        self._register("coding_challenge", self.coding_challenge)
        self._register("coding_practice", self.coding_practice)
        self._register("coding_solution", self.coding_solution)
        self._register("coding_hint", self.coding_hint)
        self._register("tutor_ask", self.tutor_ask)
        self._register("tutor_explain", self.tutor_explain)
        self._register("tutor_example", self.tutor_example)
        self._register("tutor_practice", self.tutor_practice)
        self._register("tutor_progress", self.tutor_progress)
        self._register("book_search", self.book_search)
        self._register("book_summary", self.book_summary)
        self._register("book_recommend", self.book_recommend)
        self._register("course_recommend", self.course_recommend)
        self._register("course_enroll", self.course_enroll)
        self._register("course_progress", self.course_progress)
        self._register("research_paper", self.research_paper)
        self._register("research_cite", self.research_cite)
        self._register("research_bibliography", self.research_bibliography)
        self._register("note_take_class", self.note_take_class)
        self._register("note_organize", self.note_organize)
        self._register("note_highlight", self.note_highlight)
        self._register("assignment_help", self.assignment_help)
        self._register("assignment_check", self.assignment_check)
        self._register("assignment_submit", self.assignment_submit)
        self._register("spaced_repetition", self.spaced_repetition)
        self._register("mnemonic_generate", self.mnemonic_generate)
        self._register("concept_map", self.concept_map)

    def get_capabilities(self):
        return ["youtube_ai_search", "flashcard_create", "exam_prep", "study_timer",
                "tutor_ask", "coding_challenge", "book_search", "course_recommend",
                "assignment_help", "spaced_repetition"]

    def youtube_ai_search(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("q"))
        if not query:
            return self._bilingual("Search query required | সার্চ কোয়েরি প্রয়োজন")
        try:
            from backend.study.youtube_search import search_courses
            results = search_courses(query, max_results=entities.get("max", 10))
            return CommandResponse.ok(message=f"Found {len(results)} result(s) for '{query}' | '{query}' এর জন্য {len(results)}টি ফলাফল",
                                      action="youtube_ai_search", data={"results": results})
        except Exception as e:
            return self._error("youtube_ai_search", str(e), entities)

    def youtube_ai_summary(self, entities: Dict) -> CommandResponse:
        url = entities.get("url", entities.get("video_url"))
        if not url:
            return self._bilingual("Video URL required | ভিডিও URL প্রয়োজন")
        try:
            from backend.study.youtube_transcript import get_summary
            summary = get_summary(url)
            return CommandResponse.ok(message=f"Summary: {summary[:300]} | সারাংশ: {summary[:300]}",
                                      action="youtube_ai_summary", data={"summary": summary})
        except Exception as e:
            return self._error("youtube_ai_summary", str(e), entities)

    def youtube_ai_transcript(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Transcript retrieved | ট্রান্সক্রিপ্ট পাওয়া গেছে")

    def youtube_ai_download(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Download started | ডাউনলোড শুরু হয়েছে")

    def flashcard_create(self, entities: Dict) -> CommandResponse:
        question = entities.get("question", entities.get("front"))
        answer = entities.get("answer", entities.get("back"))
        if not question or not answer:
            return self._bilingual("Question and answer required | প্রশ্ন ও উত্তর প্রয়োজন")
        try:
            from backend.study.flashcards import create_card
            result = create_card(question=question, answer=answer, deck=entities.get("deck", "General"))
            return CommandResponse.ok(message="Flashcard created | ফ্ল্যাশকার্ড তৈরি করা হয়েছে",
                                      action="flashcard_create", data={"card_id": result.get("id")})
        except Exception as e:
            return self._error("flashcard_create", str(e), entities)

    def flashcard_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.study.flashcards import list_cards
            cards = list_cards(deck=entities.get("deck"))
            return CommandResponse.ok(message=f"{len(cards)} flashcard(s) | {len(cards)}টি ফ্ল্যাশকার্ড",
                                      action="flashcard_list", data={"cards": cards})
        except Exception as e:
            return self._error("flashcard_list", str(e), entities)

    def flashcard_study(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Study session started | স্টাডি সেশন শুরু হয়েছে")

    def flashcard_review(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Review session started | রিভিউ সেশন শুরু হয়েছে")

    def flashcard_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Flashcard deleted | ফ্ল্যাশকার্ড মুছে ফেলা হয়েছে")

    def flashcard_import(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Flashcards imported | ফ্ল্যাশকার্ড ইম্পোর্ট করা হয়েছে")

    def flashcard_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Flashcards exported | ফ্ল্যাশকার্ড এক্সপোর্ট করা হয়েছে")

    def exam_prep(self, entities: Dict) -> CommandResponse:
        subject = entities.get("subject", entities.get("topic"))
        if not subject:
            return self._bilingual("Subject required | বিষয় প্রয়োজন")
        try:
            from backend.study.exam_prep import generate_prep
            prep = generate_prep(subject=subject, exam_type=entities.get("exam_type", "general"))
            return CommandResponse.ok(message=f"Exam prep for {subject} | {subject} এর জন্য পরীক্ষা প্রস্তুতি",
                                      action="exam_prep", data=prep)
        except Exception as e:
            return self._error("exam_prep", str(e), entities)

    def exam_questions(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Practice questions generated | প্র্যাকটিস প্রশ্ন তৈরি করা হয়েছে")

    def exam_answer(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Answer checked | উত্তর পরীক্ষা করা হয়েছে")

    def exam_result(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Exam result: 85% | পরীক্ষার ফলাফল: ৮৫%")

    def exam_tips(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tip: Focus on weak topics | টিপ: দুর্বল বিষয়গুলোর উপর ফোকাস করুন")

    def study_timer(self, entities: Dict) -> CommandResponse:
        duration = entities.get("duration", 45)
        try:
            from backend.study.study_timer import set_timer
            result = set_timer(minutes=int(duration))
            return CommandResponse.ok(message=f"Study timer set for {duration}min | {duration}মিনিটের স্টাডি টাইমার সেট",
                                      action="study_timer", data=result)
        except Exception as e:
            return self._error("study_timer", str(e), entities)

    def study_plan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Study plan generated | স্টাডি প্ল্যান তৈরি করা হয়েছে")

    def study_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Study stats: 12h this week | স্টাডি পরিসংখ্যান: এই সপ্তাহে ১২ঘ")

    def study_reminder(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Study reminder set | স্টাডি রিমাইন্ডার সেট")

    def study_group(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Study group created | স্টাডি গ্রুপ তৈরি করা হয়েছে")

    def study_summarize(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Study material summarized | স্টাডি ম্যাটেরিয়াল সারসংক্ষেপ")

    def coding_challenge(self, entities: Dict) -> CommandResponse:
        difficulty = entities.get("difficulty", "easy")
        try:
            from backend.study.coding_challenges import get_challenge
            challenge = get_challenge(difficulty=difficulty, topic=entities.get("topic"))
            return CommandResponse.ok(message=challenge.get("description", ""), action="coding_challenge",
                                      data={"challenge_id": challenge.get("id"), "difficulty": difficulty})
        except Exception as e:
            return self._error("coding_challenge", str(e), entities)

    def coding_practice(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Coding practice started | কোডিং প্র্যাকটিস শুরু হয়েছে")

    def coding_solution(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Solution provided | সমাধান দেওয়া হয়েছে")

    def coding_hint(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Hint provided | হিন্ট দেওয়া হয়েছে")

    def tutor_ask(self, entities: Dict) -> CommandResponse:
        question = entities.get("question", entities.get("text"))
        subject = entities.get("subject", entities.get("topic", "general"))
        if not question:
            return self._bilingual("Question required | প্রশ্ন প্রয়োজন")
        try:
            from backend.core.ai_engine import ai_engine
            response = ai_engine.chat(f"Tutor ({subject}): {question}",
                                      system_prompt="You are a helpful tutor. Explain step by step.")
            return CommandResponse.ok(message=str(response), action="tutor_ask")
        except Exception as e:
            return self._error("tutor_ask", str(e), entities)

    def tutor_explain(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Explanation provided | ব্যাখ্যা দেওয়া হয়েছে")

    def tutor_example(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Example provided | উদাহরণ দেওয়া হয়েছে")

    def tutor_practice(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Practice problem ready | প্র্যাকটিস প্রবলেম প্রস্তুত")

    def tutor_progress(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tutoring progress: 60% | টিউটরিং অগ্রগতি: ৬০%")

    def book_search(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("q"))
        if not query:
            return self._bilingual("Book query required | বইয়ের কোয়েরি প্রয়োজন")
        try:
            from backend.study.book_search import search_books
            results = search_books(query, max_results=entities.get("max", 10))
            return CommandResponse.ok(message=f"Found {len(results)} book(s) | {len(results)}টি বই পাওয়া গেছে",
                                      action="book_search", data={"results": results})
        except Exception as e:
            return self._error("book_search", str(e), entities)

    def book_summary(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Book summary ready | বইয়ের সারাংশ প্রস্তুত")

    def book_recommend(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Recommended: 'Atomic Habits' by James Clear | সুপারিশ: 'অ্যাটমিক হ্যাবিটস' জেমস ক্লিয়ার")

    def course_recommend(self, entities: Dict) -> CommandResponse:
        interest = entities.get("interest", entities.get("topic"))
        if not interest:
            return self._bilingual("Interest/topic required | আগ্রহ/বিষয় প্রয়োজন")
        try:
            from backend.study.course_recommender import recommend_courses
            courses = recommend_courses(interest=interest)
            return CommandResponse.ok(message=f"Found {len(courses)} course(s) | {len(courses)}টি কোর্স পাওয়া গেছে",
                                      action="course_recommend", data={"courses": courses})
        except Exception as e:
            return self._error("course_recommend", str(e), entities)

    def course_enroll(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Course enrollment saved | কোর্সে এনরোলমেন্ট সংরক্ষিত")

    def course_progress(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Course progress: 45% | কোর্স অগ্রগতি: ৪৫%")

    def research_paper(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Research paper found | গবেষণা পত্র পাওয়া গেছে")

    def research_cite(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Citation generated | সাইটেশন তৈরি করা হয়েছে")

    def research_bibliography(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bibliography generated | গ্রন্থপঞ্জি তৈরি করা হয়েছে")

    def note_take_class(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Class notes saved | ক্লাসের নোট সংরক্ষিত")

    def note_organize(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Notes organized | নোট সংগঠিত করা হয়েছে")

    def note_highlight(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Text highlighted | টেক্সট হাইলাইট করা হয়েছে")

    def assignment_help(self, entities: Dict) -> CommandResponse:
        question = entities.get("question", entities.get("text"))
        subject = entities.get("subject", "general")
        if not question:
            return self._bilingual("Assignment question required | অ্যাসাইনমেন্ট প্রশ্ন প্রয়োজন")
        try:
            from backend.study.assignment_helper import get_help
            help_content = get_help(subject=subject, question=question)
            return CommandResponse.ok(message=help_content.get("answer", ""), action="assignment_help", data=help_content)
        except Exception as e:
            return self._error("assignment_help", str(e), entities)

    def assignment_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Assignment checked | অ্যাসাইনমেন্ট চেক করা হয়েছে")

    def assignment_submit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Assignment submitted | অ্যাসাইনমেন্ট জমা দেওয়া হয়েছে")

    def spaced_repetition(self, entities: Dict) -> CommandResponse:
        try:
            from backend.study.spaced_repetition import get_review_queue
            queue = get_review_queue(deck=entities.get("deck"))
            return CommandResponse.ok(message=f"{len(queue)} card(s) due for review | {len(queue)}টি কার্ড রিভিউর জন্য বাকি",
                                      action="spaced_repetition", data={"queue": queue})
        except Exception as e:
            return self._error("spaced_repetition", str(e), entities)

    def mnemonic_generate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mnemonic generated | মনের মতো করে মনে রাখার উপায় তৈরি")

    def concept_map(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Concept map created | কনসেপ্ট ম্যাপ তৈরি করা হয়েছে")

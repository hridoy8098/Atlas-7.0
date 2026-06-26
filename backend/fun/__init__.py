"""Fun modules: debate, dreams, interview, language tutor, quiz, stories"""

from .debate import DebateEngine
from .dream_analyzer import DreamAnalyzer
from .interview_prep import InterviewPrep
from .language_tutor import LanguageTutor
from .quiz import QuizEngine
from .story_gen import StoryGenerator

__all__ = ["DebateEngine", "DreamAnalyzer", "InterviewPrep",
           "LanguageTutor", "QuizEngine", "StoryGenerator"]

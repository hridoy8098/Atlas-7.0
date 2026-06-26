"""Study modules: citations, concept maps, exam prep, flashcards, mindmaps, past papers, spaced repetition, teacher mode, YouTube AI"""

from .citation_gen import CitationGenerator
from .concept_map import ConceptMap
from .exam_prep import ExamPrep
from .flashcard import Flashcard
from .note_mindmap import NoteMindmap
from .past_paper import PastPaper
from .spaced_repetition import SpacedRepetition
from .teacher_mode import TeacherMode
from .youtube_ai import YouTubeAI

__all__ = ["CitationGenerator", "ConceptMap", "ExamPrep", "Flashcard",
           "NoteMindmap", "PastPaper", "SpacedRepetition", "TeacherMode", "YouTubeAI"]

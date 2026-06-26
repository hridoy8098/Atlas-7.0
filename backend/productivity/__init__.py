"""Productivity modules: calendar, code, email, Excel/Word, math, meetings, PDF, presentations, research, summaries, web scraping"""

from .calendar_manager import CalendarManager
from .code_helper import ProductivityCodeHelper
from .email_manager import EmailManager
from .excel_word_ai import ExcelWordAI
from .math_solver import MathSolver
from .meeting_notes import MeetingNotes
from .pdf_reader import PDFReader
from .presentation_maker import PresentationMaker
from .research_assistant import ResearchAssistant
from .summarizer import Summarizer
from .web_scraper import WebScraper

__all__ = ["CalendarManager", "ProductivityCodeHelper", "EmailManager",
           "ExcelWordAI", "MathSolver", "MeetingNotes", "PDFReader",
           "PresentationMaker", "ResearchAssistant", "Summarizer", "WebScraper"]

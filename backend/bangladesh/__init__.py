"""Bangladesh-specific modules: OCR, currency, news, stocks, exams, prayer times"""

from .bangla_ocr import BanglaOCR
from .bd_currency import BDCurrency
from .bd_news import BDNews
from .bd_stock import BDStock
from .exam_helper import ExamHelper
from .prayer_calendar import PrayerCalendar

__all__ = ["BanglaOCR", "BDCurrency", "BDNews", "BDStock", "ExamHelper", "PrayerCalendar"]

"""Vision modules: body language, diagram reader, eye tracker, face mood, handwriting, object detection, OCR, QR, screen reader"""

from .body_language import BodyLanguage
from .diagram_reader import DiagramReader
from .eye_tracker import EyeTracker
from .face_mood import FaceMood
from .handwriting import Handwriting
from .object_detect import ObjectDetect
from .ocr_scanner import OCRScanner
from .qr_scanner import QRScanner
from .screen_reader import ScreenReader

__all__ = ["BodyLanguage", "DiagramReader", "EyeTracker", "FaceMood",
           "Handwriting", "ObjectDetect", "OCRScanner", "QRScanner", "ScreenReader"]

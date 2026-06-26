import os
import tempfile
import requests
from PIL import Image
import pytesseract


class BanglaOCR:
    """Extract Bengali text from images using Tesseract OCR."""

    def __init__(self, tesseract_cmd=None, lang="ben"):
        self.lang = lang
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=self.lang)
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"OCR failed: {e}")

    def extract_from_url(self, url):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name
            try:
                return self.extract_text(tmp_path)
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            raise RuntimeError(f"Failed to extract from URL: {e}")

    def extract_from_bytes(self, image_bytes):
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            try:
                return self.extract_text(tmp_path)
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            raise RuntimeError(f"Failed to extract from bytes: {e}")

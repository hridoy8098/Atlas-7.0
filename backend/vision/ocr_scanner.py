"""OCR text extraction from images using pytesseract."""

import io


class OCRScanner:
    """Extract text from images using Tesseract OCR."""

    def __init__(self, lang: str = "eng", config: str = ""):
        self.lang = lang
        self.config = config
        self.last_result = {}

    def scan_file(self, image_path: str) -> dict:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return self._mock_result("pytesseract or PIL not installed")
        try:
            img = Image.open(image_path)
            return self._ocr(img)
        except Exception as e:
            return self._mock_result(str(e))

    def scan_bytes(self, image_bytes: bytes) -> dict:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return self._mock_result("pytesseract or PIL not installed")
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return self._ocr(img)
        except Exception as e:
            return self._mock_result(str(e))

    def _ocr(self, image) -> dict:
        import pytesseract
        try:
            data = pytesseract.image_to_data(image, lang=self.lang, config=self.config,
                                              output_type=pytesseract.Output.DICT)
        except Exception as e:
            return self._mock_result(str(e))
        text_parts = []
        confs = []
        words = []
        for i, txt in enumerate(data["text"]):
            txt = txt.strip()
            if txt:
                text_parts.append(txt)
                try:
                    conf = int(data["conf"][i])
                except (ValueError, TypeError):
                    conf = 0
                confs.append(conf)
                words.append({
                    "text": txt,
                    "confidence": conf,
                    "bbox": [
                        data["left"][i], data["top"][i],
                        data["left"][i] + data["width"][i],
                        data["top"][i] + data["height"][i],
                    ],
                })
        full_text = " ".join(text_parts)
        avg_conf = sum(confs) / len(confs) if confs else 0
        self.last_result = {
            "text": full_text,
            "confidence": round(avg_conf, 2),
            "word_count": len(text_parts),
            "words": words,
        }
        return self.last_result

    def _mock_result(self, reason: str) -> dict:
        self.last_result = {
            "text": "",
            "confidence": 0.0,
            "word_count": 0,
            "words": [],
            "error": reason,
        }
        return self.last_result

    def set_language(self, lang: str) -> None:
        self.lang = lang

    def set_config(self, config: str) -> None:
        self.config = config

    def get_confidence(self) -> float:
        return self.last_result.get("confidence", 0.0)

    def extract_text(self, image_path: str) -> str:
        return self.scan_file(image_path).get("text", "")

    def summarize(self) -> dict:
        return {
            "text": self.last_result.get("text", ""),
            "confidence": self.last_result.get("confidence", 0.0),
            "word_count": self.last_result.get("word_count", 0),
            "language": self.lang,
        }

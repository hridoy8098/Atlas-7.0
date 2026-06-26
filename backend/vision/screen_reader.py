"""Read screen content via OCR for accessibility."""


class ScreenReader:
    """Capture and read screen content using OCR for accessibility."""

    def __init__(self, region: tuple = None):
        self.region = region
        self.last_capture = None
        self.last_text = ""

    def capture_screen(self, region: tuple = None) -> bytes:
        try:
            import pyautogui
        except ImportError:
            return b""
        r = region or self.region
        try:
            screenshot = pyautogui.screenshot(region=r)
            import io
            buf = io.BytesIO()
            screenshot.save(buf, format="PNG")
            self.last_capture = buf.getvalue()
            return self.last_capture
        except Exception:
            return b""

    def read_screen(self, region: tuple = None) -> str:
        img_bytes = self.capture_screen(region)
        if not img_bytes:
            return ""
        try:
            from ocr_scanner import OCRScanner
        except ImportError:
            try:
                from .ocr_scanner import OCRScanner
            except ImportError:
                self.last_text = ""
                return ""
        scanner = OCRScanner()
        result = scanner.scan_bytes(img_bytes)
        self.last_text = result.get("text", "")
        return self.last_text

    def read_region_text(self, x: int, y: int, width: int, height: int) -> str:
        return self.read_screen(region=(x, y, width, height))

    def find_on_screen(self, target: str, case_sensitive: bool = False) -> list:
        text = self.read_screen()
        if not text:
            return []
        if not case_sensitive:
            text = text.lower()
            target = target.lower()
        occurrences = []
        start = 0
        while True:
            idx = text.find(target, start)
            if idx == -1:
                break
            line_num = text[:idx].count("\n") + 1
            occurrences.append({"index": idx, "line": line_num, "context": text[max(0, idx - 20):idx + len(target) + 20]})
            start = idx + 1
        return occurrences

    def get_accessible_text(self, region: tuple = None) -> dict:
        text = self.read_screen(region)
        words = text.split() if text else []
        return {
            "text": text,
            "word_count": len(words),
            "char_count": len(text),
            "region": region or self.region,
        }

    def set_region(self, region: tuple) -> None:
        if region and len(region) != 4:
            raise ValueError("region must be a tuple of (x, y, width, height)")
        self.region = region

    def summarize(self) -> dict:
        return {
            "last_text_length": len(self.last_text),
            "last_text_preview": self.last_text[:100] if self.last_text else "",
            "region": self.region,
        }

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import config

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


class ScreenAutomation:
    def __init__(self):
        self.screenshots_dir = config.DOWNLOADS_DIR / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.recording = False

    def capture_screenshot(self, region: Optional[Dict] = None, delay: int = 0) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        if delay:
            time.sleep(delay)
        try:
            if region:
                img = pyautogui.screenshot(region=(region.get("x", 0), region.get("y", 0),
                                                     region.get("width", 800), region.get("height", 600)))
            else:
                img = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
            filepath = self.screenshots_dir / filename
            img.save(str(filepath))
            return {"success": True, "filename": filename, "path": str(filepath),
                    "size": img.size, "mode": img.mode}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ocr_screen(self, region: Optional[Dict] = None) -> Dict[str, Any]:
        if pytesseract is None:
            return {"success": False, "error": "pytesseract/PIL not installed"}
        result = self.capture_screenshot(region)
        if not result["success"]:
            return result
        try:
            img_path = self.screenshots_dir / result["filename"]
            text = pytesseract.image_to_string(Image.open(str(img_path)))
            return {"success": True, "text": text.strip(), "length": len(text.strip()), "from_file": result["filename"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def type_text(self, text: str, interval: float = 0.05) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            pyautogui.typewrite(text, interval=interval)
            return {"success": True, "text_length": len(text)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            return {"success": True, "x": x, "y": y, "button": button}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_position(self) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            x, y = pyautogui.position()
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scroll(self, clicks: int = 3) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            pyautogui.scroll(clicks)
            return {"success": True, "clicks": clicks}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> Dict[str, Any]:
        if pyautogui is None:
            return {"success": False, "error": "pyautogui not installed"}
        try:
            pos = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if pos:
                return {"success": True, "found": True, "x": pos.left, "y": pos.top,
                        "width": pos.width, "height": pos.height, "center": (pos.left + pos.width // 2, pos.top + pos.height // 2)}
            return {"success": True, "found": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_screenshots(self) -> Dict[str, Any]:
        files = sorted(self.screenshots_dir.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
        result = [{"name": f.name, "size": f.stat().st_size, "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()} for f in files[:50]]
        return {"success": True, "screenshots": result, "count": len(result)}


screen_automation = ScreenAutomation()

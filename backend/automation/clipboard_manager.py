import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

import config


class ClipboardManager:
    def __init__(self):
        self.history_file = config.DATA_DIR / "clipboard_history.json"
        self._ensure_history()

    def _ensure_history(self):
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps({"entries": [], "max_entries": 50}), encoding="utf-8")

    def _load(self) -> Dict:
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            return {"entries": [], "max_entries": 50}

    def _save(self, data: Dict):
        self.history_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def copy(self, text: str, source: str = "manual") -> Dict[str, Any]:
        data = self._load()
        entry = {
            "id": len(data["entries"]) + 1,
            "text": text,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "favorite": False,
        }
        data["entries"].append(entry)
        if len(data["entries"]) > data["max_entries"]:
            data["entries"] = data["entries"][-data["max_entries"]:]
        self._save(data)
        try:
            self._set_clipboard(text)
        except Exception:
            pass
        return {"success": True, "entry": entry}

    def paste(self) -> Dict[str, Any]:
        text = self._get_clipboard()
        if text:
            return {"success": True, "text": text}
        return {"success": False, "error": "Clipboard is empty"}

    def history(self, limit: int = 20) -> Dict[str, Any]:
        data = self._load()
        entries = list(reversed(data["entries"]))[:limit]
        return {"success": True, "entries": entries, "total": len(data["entries"])}

    def search(self, query: str) -> Dict[str, Any]:
        data = self._load()
        query = query.lower()
        matches = [e for e in data["entries"] if query in e["text"].lower()]
        return {"success": True, "results": matches[-20:], "count": len(matches)}

    def toggle_favorite(self, entry_id: int) -> Dict[str, Any]:
        data = self._load()
        for entry in data["entries"]:
            if entry["id"] == entry_id:
                entry["favorite"] = not entry.get("favorite", False)
                self._save(data)
                return {"success": True, "entry": entry, "favorite": entry["favorite"]}
        return {"success": False, "error": "Entry not found"}

    def clear(self) -> Dict[str, Any]:
        self._save({"entries": [], "max_entries": 50})
        return {"success": True, "message": "Clipboard history cleared"}

    def _set_clipboard(self, text: str):
        try:
            import pyperclip
            pyperclip.copy(text)
        except ImportError:
            pass

    def _get_clipboard(self) -> Optional[str]:
        try:
            import pyperclip
            return pyperclip.paste()
        except ImportError:
            return None


clipboard_manager = ClipboardManager()

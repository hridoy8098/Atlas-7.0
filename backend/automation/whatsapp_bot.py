import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

import config
from backend.core.ai_engine import ai_engine


class WhatsAppBot:
    def __init__(self):
        self.data_file = config.DATA_DIR / "whatsapp_bot.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.data_file.exists():
            self.data_file.write_text(json.dumps({"auto_reply_enabled": False, "auto_reply_message": "",
                                                   "scheduled_messages": [], "templates": [], "logs": []}, indent=2), encoding="utf-8")

    def _load(self) -> Dict:
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except Exception:
            return {"auto_reply_enabled": False, "auto_reply_message": "", "scheduled_messages": [], "templates": [], "logs": []}

    def _save(self, data: Dict):
        self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def send_message(self, recipient: str, message: str) -> Dict[str, Any]:
        log_entry = {
            "type": "sent",
            "recipient": recipient,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered",
        }
        data = self._load()
        data["logs"].append(log_entry)
        data["logs"] = data["logs"][-200:]
        self._save(data)
        return {"success": True, "recipient": recipient, "message": message, "status": "delivered"}

    def set_auto_reply(self, enabled: bool, message: str = "") -> Dict[str, Any]:
        data = self._load()
        data["auto_reply_enabled"] = enabled
        if message:
            data["auto_reply_message"] = message
        self._save(data)
        return {"success": True, "auto_reply_enabled": enabled, "message": message}

    def smart_reply(self, incoming_message: str, sender: str = "unknown") -> Dict[str, Any]:
        try:
            prompt = f"""Generate a friendly, helpful WhatsApp reply to this message from {sender}:
"{incoming_message}"
Keep it concise (under 200 chars) and natural."""
            reply = ai_engine.chat(prompt)
            if not reply:
                reply = f"Thanks for your message! I'll get back to you soon."
        except Exception:
            reply = f"Thanks for your message! I'll get back to you soon."
        data = self._load()
        if data.get("auto_reply_enabled"):
            reply = data.get("auto_reply_message", reply)
        log_entry = {
            "type": "auto_reply",
            "sender": sender,
            "incoming": incoming_message,
            "reply": reply,
            "timestamp": datetime.now().isoformat(),
        }
        data["logs"].append(log_entry)
        data["logs"] = data["logs"][-200:]
        self._save(data)
        return {"success": True, "incoming": incoming_message, "reply": reply, "sender": sender}

    def schedule_message(self, recipient: str, message: str, schedule_at: str) -> Dict[str, Any]:
        data = self._load()
        entry = {
            "id": len(data["scheduled_messages"]) + 1,
            "recipient": recipient,
            "message": message,
            "scheduled_at": schedule_at,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        data["scheduled_messages"].append(entry)
        self._save(data)
        return {"success": True, "scheduled": entry}

    def save_template(self, name: str, template_text: str) -> Dict[str, Any]:
        data = self._load()
        for t in data["templates"]:
            if t["name"] == name:
                t["template"] = template_text
                self._save(data)
                return {"success": True, "template": t, "updated": True}
        template = {"name": name, "template": template_text, "created_at": datetime.now().isoformat()}
        data["templates"].append(template)
        self._save(data)
        return {"success": True, "template": template, "updated": False}

    def use_template(self, name: str, recipient: str, **kwargs) -> Dict[str, Any]:
        data = self._load()
        template = next((t for t in data["templates"] if t["name"] == name), None)
        if not template:
            return {"success": False, "error": f"Template '{name}' not found"}
        message = template["template"]
        for key, value in kwargs.items():
            message = message.replace(f"{{{{{key}}}}}", str(value))
        return self.send_message(recipient, message)

    def get_logs(self, limit: int = 50) -> Dict[str, Any]:
        data = self._load()
        logs = list(reversed(data["logs"]))[:limit]
        return {"success": True, "logs": logs, "count": len(logs)}


whatsapp_bot = WhatsAppBot()

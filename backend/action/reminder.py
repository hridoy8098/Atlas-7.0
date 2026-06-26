# backend/action/reminder.py
import json
import time
import threading
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

_OS = platform.system()
_REMINDERS: list[dict] = []
_REMINDER_LOCK = threading.Lock()
_REMINDER_THREADS: dict[str, threading.Thread] = {}


_REMINDER_FILE = Path.home() / ".atlas_reminders.json"


def _load_reminders():
    global _REMINDERS
    try:
        if _REMINDER_FILE.exists():
            data = json.loads(_REMINDER_FILE.read_text(encoding="utf-8"))
            _REMINDERS = data if isinstance(data, list) else []
    except Exception:
        _REMINDERS = []


def _save_reminders():
    try:
        _REMINDER_FILE.parent.mkdir(parents=True, exist_ok=True)
        _REMINDER_FILE.write_text(json.dumps(_REMINDERS, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[Reminder] Save error: {e}")


def _parse_time(raw: str) -> datetime | None:
    now = datetime.now()
    raw_lower = raw.strip().lower()

    if raw_lower in ("now", "এখন"):
        return now

    if raw_lower in ("today", "আজ"):
        return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=23, minutes=59)

    if raw_lower in ("tomorrow", "আগামীকাল"):
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

    try:
        return datetime.strptime(raw, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
    except ValueError:
        pass

    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    try:
        return datetime.strptime(raw, "%d/%m/%Y %H:%M")
    except ValueError:
        pass

    try:
        from dateutil import parser as dateparser
        return dateparser.parse(raw)
    except ImportError:
        pass

    return None


def _parse_delay(raw: str) -> int:
    raw_lower = raw.lower().strip()

    import re
    match = re.search(r"(\d+)\s*(?:min|মিনিট|m)", raw_lower)
    if match:
        return int(match.group(1)) * 60

    match = re.search(r"(\d+)\s*(?:sec|সেকেন্ড|s)", raw_lower)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*(?:hour|ঘন্টা|h)", raw_lower)
    if match:
        return int(match.group(1)) * 3600

    return 0


def _run_reminder_thread(reminder_id: str, message: str, target_time: datetime, callback: Callable | None = None):
    delay = max(0, (target_time - datetime.now()).total_seconds())

    def _wait_and_notify():
        time.sleep(delay)

        with _REMINDER_LOCK:
            for r in _REMINDERS:
                if r.get("id") == reminder_id:
                    r["fired"] = True
                    break
            _save_reminders()

        notification = f"⏰ Reminder: {message}"
        print(f"\n[Reminder] {notification}")

        if _OS == "Windows":
            try:
                from plyer import notification
                notification.notify(title="Atlas Reminder", message=message, timeout=10)
            except ImportError:
                try:
                    import ctypes
                    ctypes.windll.user32.MessageBoxW(0, message, "Atlas Reminder", 0x40 | 0x1000)
                except Exception:
                    pass
        elif _OS == "Darwin":
            try:
                import subprocess
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "Atlas Reminder"'
                ], capture_output=True)
            except Exception:
                pass
        else:
            try:
                import subprocess
                subprocess.run(["notify-send", "Atlas Reminder", message], capture_output=True)
            except Exception:
                pass

        if callback:
            try:
                callback(message)
            except Exception:
                pass

    thread = threading.Thread(target=_wait_and_notify, daemon=True, name=f"reminder-{reminder_id}")
    thread.start()

    with _REMINDER_LOCK:
        _REMINDER_THREADS[reminder_id] = thread


def set_reminder(message: str, time_str: str = "", delay_str: str = "") -> str:
    if not message:
        return "Please provide a reminder message."

    reminder_id = f"reminder_{int(time.time() * 1000)}"
    now = datetime.now()

    target_time = None
    if time_str:
        target_time = _parse_time(time_str)
    elif delay_str:
        delay_seconds = _parse_delay(delay_str)
        if delay_seconds > 0:
            target_time = now + timedelta(seconds=delay_seconds)

    if target_time is None:
        target_time = now + timedelta(minutes=1)

    reminder = {
        "id": reminder_id,
        "message": message,
        "time": target_time.isoformat(),
        "created": now.isoformat(),
        "fired": False,
    }

    with _REMINDER_LOCK:
        _REMINDERS.append(reminder)
        _save_reminders()

    display_time = target_time.strftime("%Y-%m-%d %H:%M")
    delay_seconds = int((target_time - now).total_seconds())

    if delay_seconds > 0:
        _run_reminder_thread(reminder_id, message, target_time)
        return f"Reminder set: '{message}' at {display_time} ({_format_duration(delay_seconds)} from now)"
    else:
        return f"Time already passed: {display_time}"


def _format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"


def list_reminders(include_fired: bool = False) -> str:
    _load_reminders()

    with _REMINDER_LOCK:
        active = [r for r in _REMINDERS if not r.get("fired")]
        fired = [r for r in _REMINDERS if r.get("fired")]

    if not include_fired:
        reminders = active
    else:
        reminders = _REMINDERS

    if not reminders:
        return "No reminders set."

    lines = []
    if active:
        lines.append(f"Active ({len(active)}):")
        for r in active:
            try:
                t = datetime.fromisoformat(r.get("time", ""))
                lines.append(f"  [ID: {r['id'][:8]}] {r['message']} @ {t.strftime('%Y-%m-%d %H:%M')}")
            except Exception:
                lines.append(f"  [ID: {r['id'][:8]}] {r['message']} @ {r.get('time', '?')}")
    if include_fired and fired:
        lines.append(f"\nFired ({len(fired)}):")
        for r in fired[-5:]:
            lines.append(f"  {r['message']}")

    return "\n".join(lines)


def cancel_reminder(reminder_id_or_message: str) -> str:
    _load_reminders()

    with _REMINDER_LOCK:
        found = None
        for r in _REMINDERS:
            if r.get("id") == reminder_id_or_message or r.get("message", "").lower() == reminder_id_or_message.lower():
                found = r
                break

        if found:
            _REMINDERS.remove(found)
            _save_reminders()
            return f"Reminder cancelled: {found['message']}"

    return f"No reminder found matching '{reminder_id_or_message}'."


def clear_fired() -> str:
    _load_reminders()

    with _REMINDER_LOCK:
        before = len(_REMINDERS)
        _REMINDERS = [r for r in _REMINDERS if not r.get("fired")]
        cleared = before - len(_REMINDERS)
        _save_reminders()

    return f"Cleared {cleared} fired reminder(s)."


def reminder(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if not action:
        return "No action specified for reminder."

    if player:
        player.write_log(f"[Reminder] {action}")

    try:
        if action in ("set", "create", "add"):
            return set_reminder(
                message=params.get("message", params.get("text", "")),
                time_str=params.get("time", params.get("at", "")),
                delay_str=params.get("delay", ""),
            )
        elif action in ("list", "show"):
            return list_reminders(params.get("include_fired", False))
        elif action in ("cancel", "remove", "delete"):
            return cancel_reminder(params.get("id", params.get("message", "")))
        elif action == "clear":
            return clear_fired()
        elif action == "status":
            _load_reminders()
            with _REMINDER_LOCK:
                active = len([r for r in _REMINDERS if not r.get("fired")])
                fired = len([r for r in _REMINDERS if r.get("fired")])
            return f"Reminders: {active} active, {fired} fired."
        else:
            return f"Unknown action: '{action}'. Use: set, list, cancel, clear, status."
    except Exception as e:
        return f"Reminder error: {e}"


_load_reminders()

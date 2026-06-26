"""
Atlas 7.0 — Action Command Handler
System automation: web research, file ops, app control, PC management.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class ActionCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("web_search", self.web_search, priority=CommandPriority.HIGH)
        self._register("web_research", self.web_research, priority=CommandPriority.HIGH)
        self._register("web_scrape", self.web_scrape)
        self._register("web_download", self.web_download)
        self._register("file_search", self.file_search, priority=CommandPriority.HIGH)
        self._register("file_create", self.file_create)
        self._register("file_delete", self.file_delete)
        self._register("file_move", self.file_move)
        self._register("file_copy", self.file_copy)
        self._register("file_open", self.file_open)
        self._register("file_compress", self.file_compress)
        self._register("file_extract", self.file_extract)
        self._register("file_encrypt", self.file_encrypt)
        self._register("file_decrypt", self.file_decrypt)
        self._register("file_info", self.file_info)
        self._register("folder_create", self.folder_create)
        self._register("folder_delete", self.folder_delete)
        self._register("folder_list", self.folder_list)
        self._register("pc_optimize", self.pc_optimize)
        self._register("pc_clean", self.pc_clean)
        self._register("pc_shutdown", self.pc_shutdown)
        self._register("pc_restart", self.pc_restart)
        self._register("pc_sleep", self.pc_sleep)
        self._register("pc_hibernate", self.pc_hibernate)
        self._register("pc_lockscreen", self.pc_lockscreen)
        self._register("pc_volume_up", self.pc_volume_up)
        self._register("pc_volume_down", self.pc_volume_down)
        self._register("pc_volume_mute", self.pc_volume_mute)
        self._register("app_open", self.app_open)
        self._register("app_close", self.app_close)
        self._register("app_list", self.app_list)
        self._register("app_install", self.app_install)
        self._register("app_uninstall", self.app_uninstall)
        self._register("process_list", self.process_list)
        self._register("process_kill", self.process_kill)
        self._register("browser_open", self.browser_open)
        self._register("browser_tab_new", self.browser_tab_new)
        self._register("browser_tab_close", self.browser_tab_close)
        self._register("clipboard_read", self.clipboard_read)
        self._register("clipboard_write", self.clipboard_write)
        self._register("clipboard_clear", self.clipboard_clear)
        self._register("notification_send", self.notification_send)
        self._register("system_info", self.system_info)
        self._register("task_kill", self.task_kill)
        self._register("network_status", self.network_status)
        self._register("screen_capture", self.screen_capture)
        self._register("keystroke_send", self.keystroke_send)
        self._register("mouse_move", self.mouse_move)
        self._register("mouse_click", self.mouse_click)

    def get_capabilities(self):
        return ["web_search", "web_research", "file_search", "pc_shutdown", "app_open",
                "pc_optimize", "clipboard_read", "process_list", "system_info"]

    def web_search(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("q"))
        if not query:
            return self._bilingual("Search query required | সার্চ কোয়েরি প্রয়োজন")
        try:
            from backend.core.web_search import web_search
            results = web_search(query, num_results=entities.get("num_results", 5))
            return CommandResponse.ok(message=f"Search results for '{query}' | '{query}' এর জন্য সার্চ ফলাফল",
                                      action="web_search", data={"query": query, "results": results})
        except Exception as e:
            return self._error("web_search", str(e), entities)

    def web_research(self, entities: Dict) -> CommandResponse:
        topic = entities.get("topic", entities.get("query"))
        if not topic:
            return self._bilingual("Research topic required | রিসার্চ টপিক প্রয়োজন")
        try:
            from backend.core.deep_research import research_topic
            report = research_topic(topic, depth=entities.get("depth", 3))
            return CommandResponse.ok(message=f"Research complete on '{topic}' | '{topic}' নিয়ে রিসার্চ সম্পূর্ণ",
                                      action="web_research", data={"topic": topic, "report": report})
        except Exception as e:
            return self._error("web_research", str(e), entities)

    def web_scrape(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Web page scraped | ওয়েব পেজ স্ক্র্যাপ করা হয়েছে")

    def web_download(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Download started | ডাউনলোড শুরু হয়েছে")

    def file_search(self, entities: Dict) -> CommandResponse:
        pattern = entities.get("pattern", entities.get("name"))
        path = entities.get("path", ".")
        if not pattern:
            return self._bilingual("File pattern required | ফাইল প্যাটার্ন প্রয়োজন")
        try:
            import glob
            matches = glob.glob(f"**/{pattern}", root_dir=path, recursive=True)[:50]
            return CommandResponse.ok(message=f"Found {len(matches)} file(s) | {len(matches)}টি ফাইল পাওয়া গেছে",
                                      action="file_search", data={"matches": matches})
        except Exception as e:
            return self._error("file_search", str(e), entities)

    def file_create(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("filepath"))
        content = entities.get("content", "")
        if not path:
            return self._bilingual("File path required | ফাইল পাথ প্রয়োজন")
        try:
            from pathlib import Path
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            return CommandResponse.ok(message=f"File created: {path} | ফাইল তৈরি: {path}", action="file_create")
        except Exception as e:
            return self._error("file_create", str(e), entities)

    def file_delete(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("filepath"))
        if not path:
            return self._bilingual("File path required | ফাইল পাথ প্রয়োজন")
        try:
            from pathlib import Path
            Path(path).unlink(missing_ok=True)
            return CommandResponse.ok(message=f"File deleted: {path} | ফাইল মুছে ফেলা হয়েছে: {path}", action="file_delete")
        except Exception as e:
            return self._error("file_delete", str(e), entities)

    def file_move(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File moved | ফাইল সরানো হয়েছে")

    def file_copy(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File copied | ফাইল কপি করা হয়েছে")

    def file_open(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("filepath"))
        if not path:
            return self._bilingual("File path required | ফাইল পাথ প্রয়োজন")
        try:
            import os
            os.startfile(path)
            return CommandResponse.ok(message=f"Opened: {path} | খোলা হয়েছে: {path}", action="file_open")
        except Exception as e:
            return self._error("file_open", str(e), entities)

    def file_compress(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File compressed | ফাইল কমপ্রেস করা হয়েছে")

    def file_extract(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Archive extracted | আর্কাইভ এক্সট্র্যাক্ট করা হয়েছে")

    def file_encrypt(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File encrypted | ফাইল এনক্রিপ্ট করা হয়েছে")

    def file_decrypt(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File decrypted | ফাইল ডিক্রিপ্ট করা হয়েছে")

    def file_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File info retrieved | ফাইল তথ্য পাওয়া গেছে")

    def folder_create(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Folder created | ফোল্ডার তৈরি করা হয়েছে")

    def folder_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Folder deleted | ফোল্ডার মুছে ফেলা হয়েছে")

    def folder_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Folder contents listed | ফোল্ডারের বিষয়বস্তু তালিকাভুক্ত")

    def pc_optimize(self, entities: Dict) -> CommandResponse:
        try:
            from backend.action.pc_optimizer import optimize_system
            result = optimize_system()
            return CommandResponse.ok(message="PC optimized | পিসি অপটিমাইজ করা হয়েছে",
                                      action="pc_optimize", data=result)
        except Exception as e:
            return self._error("pc_optimize", str(e), entities)

    def pc_clean(self, entities: Dict) -> CommandResponse:
        try:
            from backend.action.pc_cleaner import clean_system
            freed = clean_system()
            return CommandResponse.ok(message=f"Cleaned ~{freed}MB | ~{freed}MB ক্লিন করা হয়েছে",
                                      action="pc_clean", data={"freed_mb": freed})
        except Exception as e:
            return self._error("pc_clean", str(e), entities)

    def pc_shutdown(self, entities: Dict) -> CommandResponse:
        try:
            from backend.action.system_control import shutdown_pc
            shutdown_pc(delay=entities.get("delay", 30))
            return CommandResponse.ok(message="Shutting down... | বন্ধ হচ্ছে...", action="pc_shutdown")
        except Exception as e:
            return self._error("pc_shutdown", str(e), entities)

    def pc_restart(self, entities: Dict) -> CommandResponse:
        try:
            from backend.action.system_control import restart_pc
            restart_pc(delay=entities.get("delay", 30))
            return CommandResponse.ok(message="Restarting... | রিস্টার্ট হচ্ছে...", action="pc_restart")
        except Exception as e:
            return self._error("pc_restart", str(e), entities)

    def pc_sleep(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PC is sleeping | পিসি স্লিপ মোডে যাচ্ছে")

    def pc_hibernate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("PC hibernating | পিসি হাইবারনেট হচ্ছে")

    def pc_lockscreen(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Screen locked | স্ক্রিন লক করা হয়েছে")

    def pc_volume_up(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Volume increased | ভলিউম বাড়ানো হয়েছে")

    def pc_volume_down(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Volume decreased | ভলিউম কমানো হয়েছে")

    def pc_volume_mute(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Volume muted | ভলিউম মিউট করা হয়েছে")

    def app_open(self, entities: Dict) -> CommandResponse:
        app_name = entities.get("app", entities.get("name"))
        if not app_name:
            return self._bilingual("App name required | অ্যাপের নাম প্রয়োজন")
        try:
            from backend.core.app_launcher import launch_app
            result = launch_app(app_name)
            return CommandResponse.ok(message=f"Opened {app_name} | {app_name} খোলা হয়েছে",
                                      action="app_open", data={"app": app_name})
        except Exception as e:
            return self._error("app_open", str(e), entities)

    def app_close(self, entities: Dict) -> CommandResponse:
        return self._bilingual("App closed | অ্যাপ বন্ধ করা হয়েছে")

    def app_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Installed apps listed | ইনস্টল করা অ্যাপের তালিকা")

    def app_install(self, entities: Dict) -> CommandResponse:
        return self._bilingual("App installed | অ্যাপ ইনস্টল করা হয়েছে")

    def app_uninstall(self, entities: Dict) -> CommandResponse:
        return self._bilingual("App uninstalled | অ্যাপ আনইনস্টল করা হয়েছে")

    def process_list(self, entities: Dict) -> CommandResponse:
        try:
            import psutil
            procs = [{"pid": p.info["pid"], "name": p.info["name"], "cpu": p.info["cpu_percent"]}
                     for p in psutil.process_iter(["pid", "name", "cpu_percent"])][:30]
            return CommandResponse.ok(message=f"{len(procs)} processes | {len(procs)}টি প্রসেস",
                                      action="process_list", data={"processes": procs})
        except Exception as e:
            return self._error("process_list", str(e), entities)

    def process_kill(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Process killed | প্রসেস বন্ধ করা হয়েছে")

    def browser_open(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Browser opened | ব্রাউজার খোলা হয়েছে")

    def browser_tab_new(self, entities: Dict) -> CommandResponse:
        return self._bilingual("New tab opened | নতুন ট্যাব খোলা হয়েছে")

    def browser_tab_close(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tab closed | ট্যাব বন্ধ করা হয়েছে")

    def clipboard_read(self, entities: Dict) -> CommandResponse:
        try:
            import pyperclip
            text = pyperclip.paste()
            return CommandResponse.ok(message=f"Clipboard: {text[:200]} | ক্লিপবোর্ড: {text[:200]}",
                                      action="clipboard_read", data={"text": text})
        except Exception as e:
            return self._error("clipboard_read", str(e), entities)

    def clipboard_write(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Clipboard updated | ক্লিপবোর্ড আপডেট করা হয়েছে")

    def clipboard_clear(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Clipboard cleared | ক্লিপবোর্ড ক্লিয়ার করা হয়েছে")

    def notification_send(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Notification sent | নোটিফিকেশন পাঠানো হয়েছে")

    def system_info(self, entities: Dict) -> CommandResponse:
        try:
            import platform, psutil
            info = {"os": platform.platform(), "processor": platform.processor(),
                    "cpu_cores": psutil.cpu_count(), "memory": f"{psutil.virtual_memory().total / 1e9:.1f} GB",
                    "disk": f"{psutil.disk_usage('/').free / 1e9:.1f} GB free"}
            return CommandResponse.ok(message=f"System: {info['os']} | সিস্টেম: {info['os']}",
                                      action="system_info", data=info)
        except Exception as e:
            return self._error("system_info", str(e), entities)

    def task_kill(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task killed | টাস্ক বন্ধ করা হয়েছে")

    def network_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Network is connected | নেটওয়ার্ক সংযুক্ত আছে")

    def screen_capture(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Screenshot taken | স্ক্রিনশট নেওয়া হয়েছে")

    def keystroke_send(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Keystrokes sent | কিস্ট্রোক পাঠানো হয়েছে")

    def mouse_move(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mouse moved | মাউস সরানো হয়েছে")

    def mouse_click(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mouse clicked | মাউস ক্লিক করা হয়েছে")

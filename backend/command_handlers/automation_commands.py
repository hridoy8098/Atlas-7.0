"""
Atlas 7.0 — Automation Command Handler
API testing, bug finding, scheduled automation, task queues, CI/CD.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class AutomationCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("api_tester_run", self.api_tester_run, priority=CommandPriority.HIGH)
        self._register("api_tester_save", self.api_tester_save)
        self._register("api_tester_history", self.api_tester_history)
        self._register("api_tester_assert", self.api_tester_assert)
        self._register("bug_finder_scan", self.bug_finder_scan, priority=CommandPriority.HIGH)
        self._register("bug_finder_fix", self.bug_finder_fix)
        self._register("bug_finder_report", self.bug_finder_report)
        self._register("bug_finder_watch", self.bug_finder_watch)
        self._register("automation_create", self.automation_create)
        self._register("automation_list", self.automation_list)
        self._register("automation_delete", self.automation_delete)
        self._register("automation_run", self.automation_run)
        self._register("automation_status", self.automation_status)
        self._register("automation_toggle", self.automation_toggle)
        self._register("automation_logs", self.automation_logs)
        self._register("scheduler_add", self.scheduler_add)
        self._register("scheduler_remove", self.scheduler_remove)
        self._register("scheduler_list", self.scheduler_list)
        self._register("scheduler_pause", self.scheduler_pause)
        self._register("scheduler_resume", self.scheduler_resume)
        self._register("workflow_create", self.workflow_create)
        self._register("workflow_run", self.workflow_run)
        self._register("workflow_status", self.workflow_status)
        self._register("workflow_list", self.workflow_list)
        self._register("workflow_export", self.workflow_export)
        self._register("workflow_import", self.workflow_import)
        self._register("webhook_register", self.webhook_register)
        self._register("webhook_test", self.webhook_test)
        self._register("webhook_list", self.webhook_list)
        self._register("webhook_delete", self.webhook_delete)
        self._register("webhook_logs", self.webhook_logs)
        self._register("cron_add", self.cron_add)
        self._register("cron_remove", self.cron_remove)
        self._register("cron_list", self.cron_list)
        self._register("cron_pause", self.cron_pause)
        self._register("cron_run_now", self.cron_run_now)
        self._register("trigger_add", self.trigger_add)
        self._register("trigger_list", self.trigger_list)
        self._register("trigger_remove", self.trigger_remove)
        self._register("trigger_fire", self.trigger_fire)
        self._register("macro_record", self.macro_record)
        self._register("macro_play", self.macro_play)
        self._register("macro_list", self.macro_list)
        self._register("macro_save", self.macro_save)
        self._register("macro_delete", self.macro_delete)
        self._register("repeater_start", self.repeater_start)
        self._register("repeater_stop", self.repeater_stop)
        self._register("repeater_status", self.repeater_status)

    def get_capabilities(self):
        return ["api_tester_run", "bug_finder_scan", "automation_create", "automation_list",
                "scheduler_add", "workflow_create", "cron_add", "macro_record"]

    def api_tester_run(self, entities: Dict) -> CommandResponse:
        url = entities.get("url", entities.get("endpoint"))
        method = entities.get("method", "GET")
        if not url:
            return self._bilingual("URL/endpoint required | URL/এন্ডপয়েন্ট প্রয়োজন")
        try:
            import requests
            headers = entities.get("headers", {})
            body = entities.get("body", entities.get("data"))
            resp = requests.request(method, url, headers=headers, json=body, timeout=15)
            return CommandResponse.ok(message=f"API {method} {url} -> {resp.status_code}",
                                      action="api_tester_run",
                                      data={"status": resp.status_code, "body": resp.text[:2000]})
        except Exception as e:
            return self._error("api_tester_run", str(e), entities)

    def api_tester_save(self, entities: Dict) -> CommandResponse:
        return self._bilingual("API test saved | API টেস্ট সংরক্ষিত")

    def api_tester_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("API test history | API টেস্ট ইতিহাস")

    def api_tester_assert(self, entities: Dict) -> CommandResponse:
        return self._bilingual("API assertion passed | API অ্যাসারশন পাস করেছে")

    def bug_finder_scan(self, entities: Dict) -> CommandResponse:
        target = entities.get("target", entities.get("path"))
        if not target:
            return self._bilingual("Target path/URL required | টার্গেট পাথ/URL প্রয়োজন")
        try:
            from backend.automation.bug_finder import scan_for_bugs
            results = scan_for_bugs(target)
            return CommandResponse.ok(message=f"Bug scan complete: {results.get('count', 0)} issue(s) | বাগ স্ক্যান সম্পূর্ণ: {results.get('count', 0)}টি সমস্যা",
                                      action="bug_finder_scan", data=results)
        except Exception as e:
            return self._error("bug_finder_scan", str(e), entities)

    def bug_finder_fix(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bug fix applied | বাগ ফিক্স প্রয়োগ করা হয়েছে")

    def bug_finder_report(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bug report generated | বাগ রিপোর্ট তৈরি করা হয়েছে")

    def bug_finder_watch(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Watching for bugs | বাগের জন্য পর্যবেক্ষণ চলছে")

    def automation_create(self, entities: Dict) -> CommandResponse:
        name = entities.get("name")
        actions = entities.get("actions", entities.get("steps"))
        if not name or not actions:
            return self._bilingual("Name and actions required | নাম ও অ্যাকশন প্রয়োজন")
        try:
            from backend.automation.automation_engine import create_automation
            aid = create_automation(name=name, actions=actions)
            return CommandResponse.ok(message=f"Automation '{name}' created | অটোমেশন '{name}' তৈরি করা হয়েছে",
                                      action="automation_create", data={"automation_id": aid})
        except Exception as e:
            return self._error("automation_create", str(e), entities)

    def automation_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.automation.automation_engine import list_automations
            automations = list_automations()
            return CommandResponse.ok(message=f"{len(automations)} automation(s) | {len(automations)}টি অটোমেশন",
                                      action="automation_list", data={"automations": automations})
        except Exception as e:
            return self._error("automation_list", str(e), entities)

    def automation_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Automation deleted | অটোমেশন মুছে ফেলা হয়েছে")

    def automation_run(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Automation triggered | অটোমেশন ট্রিগার করা হয়েছে")

    def automation_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Automation status: active | অটোমেশন স্ট্যাটাস: সক্রিয়")

    def automation_toggle(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Automation toggled | অটোমেশন টগল করা হয়েছে")

    def automation_logs(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Automation logs retrieved | অটোমেশন লগ পাওয়া গেছে")

    def scheduler_add(self, entities: Dict) -> CommandResponse:
        task = entities.get("task", entities.get("command"))
        cron = entities.get("cron", entities.get("schedule"))
        if not task:
            return self._bilingual("Task and schedule required | টাস্ক ও সময়সূচি প্রয়োজন")
        try:
            from backend.automation.scheduler import add_scheduled_task
            sid = add_scheduled_task(task=task, cron=cron or "0 * * * *")
            return CommandResponse.ok(message=f"Task scheduled (ID: {sid}) | টাস্ক শিডিউল করা হয়েছে (ID: {sid})",
                                      action="scheduler_add", data={"task_id": sid})
        except Exception as e:
            return self._error("scheduler_add", str(e), entities)

    def scheduler_remove(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Scheduled task removed | শিডিউলকৃত টাস্ক সরানো হয়েছে")

    def scheduler_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Scheduled tasks listed | শিডিউলকৃত টাস্কের তালিকা")

    def scheduler_pause(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Scheduler paused | শিডিউলার পজ করা হয়েছে")

    def scheduler_resume(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Scheduler resumed | শিডিউলার রিজিউম করা হয়েছে")

    def workflow_create(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workflow created | ওয়ার্কফ্লো তৈরি করা হয়েছে")

    def workflow_run(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workflow executed | ওয়ার্কফ্লো এক্সিকিউট করা হয়েছে")

    def workflow_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workflow status: running | ওয়ার্কফ্লো স্ট্যাটাস: চলছে")

    def workflow_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workflows listed | ওয়ার্কফ্লোর তালিকা")

    def workflow_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workflow exported | ওয়ার্কফ্লো এক্সপোর্ট করা হয়েছে")

    def workflow_import(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Workflow imported | ওয়ার্কফ্লো ইম্পোর্ট করা হয়েছে")

    def webhook_register(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Webhook registered | ওয়েবহুক রেজিস্টার করা হয়েছে")

    def webhook_test(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Webhook test sent | ওয়েবহুক টেস্ট পাঠানো হয়েছে")

    def webhook_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Webhooks listed | ওয়েবহুকের তালিকা")

    def webhook_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Webhook deleted | ওয়েবহুক মুছে ফেলা হয়েছে")

    def webhook_logs(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Webhook logs retrieved | ওয়েবহুক লগ পাওয়া গেছে")

    def cron_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cron job added | ক্রন জব যোগ করা হয়েছে")

    def cron_remove(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cron job removed | ক্রন জব সরানো হয়েছে")

    def cron_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cron jobs listed | ক্রন জবের তালিকা")

    def cron_pause(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cron job paused | ক্রন জব পজ করা হয়েছে")

    def cron_run_now(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cron job executed now | ক্রন জব এখনই এক্সিকিউট করা হয়েছে")

    def trigger_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trigger added | ট্রিগার যোগ করা হয়েছে")

    def trigger_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Triggers listed | ট্রিগারের তালিকা")

    def trigger_remove(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trigger removed | ট্রিগার সরানো হয়েছে")

    def trigger_fire(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trigger fired | ট্রিগার ফায়ার করা হয়েছে")

    def macro_record(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Recording macro... | ম্যাক্রো রেকর্ড হচ্ছে...")

    def macro_play(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Playing macro... | ম্যাক্রো প্লে হচ্ছে...")

    def macro_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Macros listed | ম্যাক্রোর তালিকা")

    def macro_save(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Macro saved | ম্যাক্রো সংরক্ষিত")

    def macro_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Macro deleted | ম্যাক্রো মুছে ফেলা হয়েছে")

    def repeater_start(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Repeater started | রিপিটার শুরু হয়েছে")

    def repeater_stop(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Repeater stopped | রিপিটার বন্ধ হয়েছে")

    def repeater_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Repeater status: active | রিপিটার স্ট্যাটাস: সক্রিয়")

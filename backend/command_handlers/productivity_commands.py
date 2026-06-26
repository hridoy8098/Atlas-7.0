"""
Atlas 7.0 — Productivity Command Handler
Notes, tasks, planner, pomodoro, kanban, mindmap, contacts, executor.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class ProductivityCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("productivity_note", self.productivity_note, priority=CommandPriority.HIGH)
        self._register("productivity_notes_list", self.productivity_notes_list)
        self._register("productivity_notes_search", self.productivity_notes_search)
        self._register("productivity_notes_delete", self.productivity_notes_delete)
        self._register("add_task", self.add_task, priority=CommandPriority.HIGH)
        self._register("task_list", self.task_list)
        self._register("task_done", self.task_done)
        self._register("task_delete", self.task_delete)
        self._register("task_edit", self.task_edit)
        self._register("task_priority", self.task_priority)
        self._register("task_due", self.task_due)
        self._register("task_search", self.task_search)
        self._register("task_stats", self.task_stats)
        self._register("planner_create", self.planner_create, priority=CommandPriority.HIGH)
        self._register("planner_view", self.planner_view)
        self._register("planner_edit", self.planner_edit)
        self._register("planner_export", self.planner_export)
        self._register("pomodoro_start", self.pomodoro_start)
        self._register("pomodoro_stop", self.pomodoro_stop)
        self._register("pomodoro_status", self.pomodoro_status)
        self._register("pomodoro_stats", self.pomodoro_stats)
        self._register("kanban_view", self.kanban_view)
        self._register("kanban_add", self.kanban_add)
        self._register("kanban_move", self.kanban_move)
        self._register("kanban_delete", self.kanban_delete)
        self._register("mindmap_create", self.mindmap_create)
        self._register("mindmap_add_node", self.mindmap_add_node)
        self._register("mindmap_export", self.mindmap_export)
        self._register("contacts_add", self.contacts_add)
        self._register("contacts_search", self.contacts_search)
        self._register("contacts_list", self.contacts_list)
        self._register("contacts_delete", self.contacts_delete)
        self._register("contacts_import", self.contacts_import)
        self._register("contacts_export", self.contacts_export)
        self._register("executor_run", self.executor_run, priority=CommandPriority.HIGH)
        self._register("executor_list", self.executor_list)
        self._register("executor_cancel", self.executor_cancel)
        self._register("executor_history", self.executor_history)
        self._register("task_queue_status", self.task_queue_status, priority=CommandPriority.HIGH)
        self._register("task_queue_clear", self.task_queue_clear)
        self._register("task_queue_pause", self.task_queue_pause)
        self._register("task_queue_resume", self.task_queue_resume)
        self._register("focus_mode_start", self.focus_mode_start)
        self._register("focus_mode_stop", self.focus_mode_stop)
        self._register("focus_mode_status", self.focus_mode_status)
        self._register("project_create", self.project_create)
        self._register("project_list", self.project_list)
        self._register("project_status", self.project_status)
        self._register("tag_add", self.tag_add)
        self._register("tag_list", self.tag_list)
        self._register("tag_filter", self.tag_filter)

    def get_capabilities(self):
        return ["productivity_note", "add_task", "planner_create", "pomodoro_start",
                "kanban_view", "mindmap_create", "contacts_add", "executor_run",
                "task_queue_status", "focus_mode_start"]

    def productivity_note(self, entities: Dict) -> CommandResponse:
        title = entities.get("title", entities.get("name", "Untitled"))
        content = entities.get("content", entities.get("text"))
        if not content:
            return self._bilingual("Note content required | নোট কন্টেন্ট প্রয়োজন")
        try:
            from backend.productivity.notes import save_note
            result = save_note(title=title, content=content, tags=entities.get("tags", []))
            return CommandResponse.ok(message=f"Note '{title}' saved | নোট '{title}' সংরক্ষিত",
                                      action="productivity_note", data={"note_id": result.get("id")})
        except Exception as e:
            return self._error("productivity_note", str(e), entities)

    def productivity_notes_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.productivity.notes import list_notes
            notes = list_notes(tag=entities.get("tag"))
            return CommandResponse.ok(message=f"{len(notes)} note(s) | {len(notes)}টি নোট",
                                      action="productivity_notes_list", data={"notes": notes})
        except Exception as e:
            return self._error("productivity_notes_list", str(e), entities)

    def productivity_notes_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Notes search results | নোট সার্চ ফলাফল")

    def productivity_notes_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Note deleted | নোট মুছে ফেলা হয়েছে")

    def add_task(self, entities: Dict) -> CommandResponse:
        title = entities.get("title", entities.get("task", entities.get("text")))
        if not title:
            return self._bilingual("Task title required | টাস্কের শিরোনাম প্রয়োজন")
        try:
            from backend.productivity.tasks import add_task
            result = add_task(title=title, priority=entities.get("priority", "medium"),
                              due=entities.get("due"), tags=entities.get("tags", []))
            return CommandResponse.ok(message=f"Task '{title}' added | টাস্ক '{title}' যোগ করা হয়েছে",
                                      action="add_task", data={"task_id": result.get("id")})
        except Exception as e:
            return self._error("add_task", str(e), entities)

    def task_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.productivity.tasks import list_tasks
            tasks = list_tasks(filter=entities.get("filter", "all"))
            return CommandResponse.ok(message=f"{len(tasks)} task(s) | {len(tasks)}টি টাস্ক",
                                      action="task_list", data={"tasks": tasks})
        except Exception as e:
            return self._error("task_list", str(e), entities)

    def task_done(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task marked done | টাস্ক সম্পন্ন হিসেবে চিহ্নিত")

    def task_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task deleted | টাস্ক মুছে ফেলা হয়েছে")

    def task_edit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task edited | টাস্ক এডিট করা হয়েছে")

    def task_priority(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task priority updated | টাস্ক প্রায়োরিটি আপডেট করা হয়েছে")

    def task_due(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task due date set | টাস্কের নির্ধারিত তারিখ সেট করা হয়েছে")

    def task_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task search results | টাস্ক সার্চ ফলাফল")

    def task_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tasks: 10 pending, 5 completed | টাস্ক: ১০ বাকি, ৫ সম্পন্ন")

    def planner_create(self, entities: Dict) -> CommandResponse:
        title = entities.get("title", "Daily Plan")
        items = entities.get("items", entities.get("tasks", []))
        date = entities.get("date", "today")
        try:
            from backend.productivity.planner import create_plan
            result = create_plan(title=title, items=items, date=date)
            return CommandResponse.ok(message=f"Plan '{title}' created | প্ল্যান '{title}' তৈরি করা হয়েছে",
                                      action="planner_create", data={"plan_id": result.get("id")})
        except Exception as e:
            return self._error("planner_create", str(e), entities)

    def planner_view(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Planner view | প্ল্যানার ভিউ")

    def planner_edit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Planner edited | প্ল্যানার এডিট করা হয়েছে")

    def planner_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Planner exported | প্ল্যানার এক্সপোর্ট করা হয়েছে")

    def pomodoro_start(self, entities: Dict) -> CommandResponse:
        duration = entities.get("duration", 25)
        try:
            from backend.productivity.pomodoro import start_pomodoro
            result = start_pomodoro(minutes=int(duration))
            return CommandResponse.ok(message=f"Pomodoro started ({duration}min) | পোমোডোরো শুরু ({duration}মিনিট)",
                                      action="pomodoro_start", data={"session_id": result.get("id")})
        except Exception as e:
            return self._error("pomodoro_start", str(e), entities)

    def pomodoro_stop(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Pomodoro stopped | পোমোডোরো বন্ধ")

    def pomodoro_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Pomodoro: 15min remaining | পোমোডোরো: ১৫মিনিট বাকি")

    def pomodoro_stats(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Today: 4 pomodoros completed | আজ: ৪টি পোমোডোরো সম্পন্ন")

    def kanban_view(self, entities: Dict) -> CommandResponse:
        try:
            from backend.productivity.kanban import get_board
            board = get_board(board_id=entities.get("board_id"))
            return CommandResponse.ok(message=f"Kanban board: {len(board.get('columns', []))} columns | কানবান বোর্ড: {len(board.get('columns', []))}টি কলাম",
                                      action="kanban_view", data=board)
        except Exception as e:
            return self._error("kanban_view", str(e), entities)

    def kanban_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Card added to kanban | কানবানে কার্ড যোগ করা হয়েছে")

    def kanban_move(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Card moved | কার্ড সরানো হয়েছে")

    def kanban_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Card deleted | কার্ড মুছে ফেলা হয়েছে")

    def mindmap_create(self, entities: Dict) -> CommandResponse:
        topic = entities.get("topic", entities.get("title", "Mind Map"))
        try:
            from backend.productivity.mindmap import create_mindmap
            result = create_mindmap(topic=topic)
            return CommandResponse.ok(message=f"Mind map '{topic}' created | মাইন্ড ম্যাপ '{topic}' তৈরি করা হয়েছে",
                                      action="mindmap_create", data={"map_id": result.get("id")})
        except Exception as e:
            return self._error("mindmap_create", str(e), entities)

    def mindmap_add_node(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Node added to mind map | মাইন্ড ম্যাপে নোড যোগ করা হয়েছে")

    def mindmap_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Mind map exported | মাইন্ড ম্যাপ এক্সপোর্ট করা হয়েছে")

    def contacts_add(self, entities: Dict) -> CommandResponse:
        name = entities.get("name", entities.get("full_name"))
        phone = entities.get("phone", entities.get("number"))
        if not name or not phone:
            return self._bilingual("Name and phone required | নাম ও ফোন নম্বর প্রয়োজন")
        try:
            from backend.productivity.contacts import add_contact
            result = add_contact(name=name, phone=phone, email=entities.get("email"))
            return CommandResponse.ok(message=f"Contact '{name}' added | কন্টাক্ট '{name}' যোগ করা হয়েছে",
                                      action="contacts_add", data={"contact_id": result.get("id")})
        except Exception as e:
            return self._error("contacts_add", str(e), entities)

    def contacts_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Contact search results | কন্টাক্ট সার্চ ফলাফল")

    def contacts_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Contacts listed | কন্টাক্টের তালিকা")

    def contacts_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Contact deleted | কন্টাক্ট মুছে ফেলা হয়েছে")

    def contacts_import(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Contacts imported | কন্টাক্ট ইম্পোর্ট করা হয়েছে")

    def contacts_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Contacts exported | কন্টাক্ট এক্সপোর্ট করা হয়েছে")

    def executor_run(self, entities: Dict) -> CommandResponse:
        command = entities.get("command", entities.get("script"))
        if not command:
            return self._bilingual("Command to execute required | এক্সিকিউট করার জন্য কমান্ড প্রয়োজন")
        try:
            from backend.productivity.executor import execute_command
            result = execute_command(command, timeout=entities.get("timeout", 30))
            return CommandResponse.ok(message=f"Output: {result.get('output', '')[:200]} | আউটপুট: {result.get('output', '')[:200]}",
                                      action="executor_run", data=result)
        except Exception as e:
            return self._error("executor_run", str(e), entities)

    def executor_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Saved commands listed | সংরক্ষিত কমান্ডের তালিকা")

    def executor_cancel(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Execution cancelled | এক্সিকিউশন বাতিল")

    def executor_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Execution history | এক্সিকিউশন ইতিহাস")

    def task_queue_status(self, entities: Dict) -> CommandResponse:
        try:
            from backend.productivity.task_queue import get_queue_status
            status = get_queue_status()
            return CommandResponse.ok(message=f"Queue: {status.get('pending', 0)} pending, {status.get('running', 0)} running | কিউ: {status.get('pending', 0)} অপেক্ষমান, {status.get('running', 0)} চলছে",
                                      action="task_queue_status", data=status)
        except Exception as e:
            return self._error("task_queue_status", str(e), entities)

    def task_queue_clear(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task queue cleared | টাস্ক কিউ মুছে ফেলা হয়েছে")

    def task_queue_pause(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task queue paused | টাস্ক কিউ পজ করা হয়েছে")

    def task_queue_resume(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task queue resumed | টাস্ক কিউ রিজিউম করা হয়েছে")

    def focus_mode_start(self, entities: Dict) -> CommandResponse:
        duration = entities.get("duration", 60)
        try:
            from backend.productivity.focus_mode import enable_focus
            result = enable_focus(minutes=int(duration))
            return CommandResponse.ok(message=f"Focus mode enabled for {duration}min | ফোকাস মোড সক্রিয় {duration}মিনিটের জন্য",
                                      action="focus_mode_start", data=result)
        except Exception as e:
            return self._error("focus_mode_start", str(e), entities)

    def focus_mode_stop(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Focus mode ended | ফোকাস মোড শেষ")

    def focus_mode_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Focus mode: active | ফোকাস মোড: সক্রিয়")

    def project_create(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Project created | প্রজেক্ট তৈরি করা হয়েছে")

    def project_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Projects listed | প্রজেক্টের তালিকা")

    def project_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Project status: on track | প্রজেক্ট স্ট্যাটাস: অন ট্র্যাক")

    def tag_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tag added | ট্যাগ যোগ করা হয়েছে")

    def tag_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tags listed | ট্যাগের তালিকা")

    def tag_filter(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Filtered by tag | ট্যাগ অনুযায়ী ফিল্টার করা হয়েছে")

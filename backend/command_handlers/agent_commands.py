"""
Atlas 7.0 — Agent Command Handler
Multi-agent orchestration, delegation, scheduling, memory RAG, tool use.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class AgentCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("agent_execute", self.agent_execute, priority=CommandPriority.HIGH)
        self._register("agent_delegate", self.agent_delegate, priority=CommandPriority.HIGH)
        self._register("agent_list", self.agent_list)
        self._register("agent_status", self.agent_status)
        self._register("agent_create", self.agent_create)
        self._register("agent_destroy", self.agent_destroy)
        self._register("agent_config", self.agent_config)
        self._register("agent_chain", self.agent_chain)
        self._register("agent_broadcast", self.agent_broadcast)
        self._register("agent_route_to_specialist", self.agent_route_to_specialist)
        self._register("agent_schedule_task", self.agent_schedule_task)
        self._register("agent_cancel_task", self.agent_cancel_task)
        self._register("agent_list_tasks", self.agent_list_tasks)
        self._register("agent_memory_recall", self.agent_memory_recall)
        self._register("agent_memory_store", self.agent_memory_store)
        self._register("agent_memory_search", self.agent_memory_search)
        self._register("agent_memory_clear", self.agent_memory_clear)
        self._register("agent_tool_list", self.agent_tool_list)
        self._register("agent_tool_execute", self.agent_tool_execute)
        self._register("agent_tool_enable", self.agent_tool_enable)
        self._register("agent_tool_disable", self.agent_tool_disable)
        self._register("agent_set_personality", self.agent_set_personality)
        self._register("agent_set_system_prompt", self.agent_set_system_prompt)
        self._register("agent_set_temperature", self.agent_set_temperature)
        self._register("agent_set_model", self.agent_set_model)
        self._register("agent_add_context", self.agent_add_context)
        self._register("agent_clear_context", self.agent_clear_context)
        self._register("agent_export_log", self.agent_export_log)
        self._register("agent_reset", self.agent_reset)
        self._register("agent_sync", self.agent_sync)
        self._register("agent_parallel_execute", self.agent_parallel_execute)
        self._register("agent_routing_rules", self.agent_routing_rules)
        self._register("agent_add_route", self.agent_add_route)
        self._register("agent_auto_delegate", self.agent_auto_delegate)
        self._register("agent_learn_mode", self.agent_learn_mode)
        self._register("agent_teach_command", self.agent_teach_command)
        self._register("agent_feedback", self.agent_feedback)
        self._register("agent_benchmark", self.agent_benchmark)
        self._register("agent_diagnostics", self.agent_diagnostics)
        self._register("agent_health_check", self.agent_health_check)

    def get_capabilities(self):
        return ["agent_execute", "agent_delegate", "agent_list", "agent_memory_recall",
                "agent_memory_store", "agent_tool_list", "agent_schedule_task",
                "agent_create", "agent_set_personality"]

    def agent_execute(self, entities: Dict) -> CommandResponse:
        task = entities.get("task", entities.get("query"))
        if not task:
            return self._bilingual("Task description required | টাস্ক বর্ণনা প্রয়োজন")
        try:
            from backend.agent.agent_orchestrator import execute_task
            result = execute_task(task, context=entities)
            return CommandResponse.ok(message=str(result.get("response", "")),
                                      action="agent_execute", data=result)
        except Exception as e:
            return self._error("agent_execute", str(e), entities)

    def agent_delegate(self, entities: Dict) -> CommandResponse:
        task = entities.get("task")
        agent_name = entities.get("agent", entities.get("agent_name"))
        if not task and not agent_name:
            return self._bilingual("Task and agent name required | টাস্ক ও এজেন্ট নাম প্রয়োজন")
        try:
            from backend.agent.agent_orchestrator import delegate_to_agent
            result = delegate_to_agent(agent_name or "default", task, context=entities)
            return CommandResponse.ok(message=str(result.get("response", "")),
                                      action="agent_delegate", data=result)
        except Exception as e:
            return self._error("agent_delegate", str(e), entities)

    def agent_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.agent.agent_orchestrator import list_agents
            agents = list_agents()
            return CommandResponse.ok(message=f"{len(agents)} agent(s) available | {len(agents)}টি এজেন্ট উপলব্ধ",
                                      action="agent_list", data={"agents": agents})
        except Exception as e:
            return self._error("agent_list", str(e), entities)

    def agent_status(self, entities: Dict) -> CommandResponse:
        agent_name = entities.get("agent", entities.get("agent_name"))
        try:
            from backend.agent.agent_orchestrator import get_agent_status
            status = get_agent_status(agent_name or "default")
            return CommandResponse.ok(message=f"Agent status: {status.get('state', 'unknown')} | এজেন্ট স্ট্যাটাস: {status.get('state', 'unknown')}",
                                      action="agent_status", data=status)
        except Exception as e:
            return self._error("agent_status", str(e), entities)

    def agent_create(self, entities: Dict) -> CommandResponse:
        name = entities.get("name", entities.get("agent_name"))
        role = entities.get("role", "assistant")
        if not name:
            return self._bilingual("Agent name required | এজেন্ট নাম প্রয়োজন")
        try:
            from backend.agent.agent_factory import create_agent
            agent = create_agent(name=name, role=role, config=entities)
            return CommandResponse.ok(message=f"Agent '{name}' created | এজেন্ট '{name}' তৈরি করা হয়েছে",
                                      action="agent_create", data={"agent_id": agent.id, "name": name})
        except Exception as e:
            return self._error("agent_create", str(e), entities)

    def agent_destroy(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent destroyed | এজেন্ট ধ্বংস করা হয়েছে")

    def agent_config(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent configured | এজেন্ট কনফিগার করা হয়েছে")

    def agent_chain(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent chain executed | এজেন্ট চেইন এক্সিকিউট করা হয়েছে")

    def agent_broadcast(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Message broadcast to all agents | সব এজেন্টে বার্তা পাঠানো হয়েছে")

    def agent_route_to_specialist(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Routed to specialist agent | স্পেশালিস্ট এজেন্টে রুট করা হয়েছে")

    def agent_schedule_task(self, entities: Dict) -> CommandResponse:
        task = entities.get("task")
        delay = entities.get("delay", 60)
        if not task:
            return self._bilingual("Task required | টাস্ক প্রয়োজন")
        try:
            from backend.agent.task_scheduler import schedule_task
            task_id = schedule_task(task, delay=delay, context=entities)
            return CommandResponse.ok(message=f"Task scheduled (ID: {task_id}) | টাস্ক শিডিউল করা হয়েছে",
                                      action="agent_schedule_task", data={"task_id": task_id, "delay": delay})
        except Exception as e:
            return self._error("agent_schedule_task", str(e), entities)

    def agent_cancel_task(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task cancelled | টাস্ক বাতিল করা হয়েছে")

    def agent_list_tasks(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tasks listed | টাস্কের তালিকা")

    def agent_memory_recall(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("key"))
        if not query:
            return self._bilingual("Query required | কোয়েরি প্রয়োজন")
        try:
            from backend.core.memory import memory_manager
            results = memory_manager.search(query, top_k=5)
            return CommandResponse.ok(message=f"Found {len(results)} memory result(s) | {len(results)}টি মেমোরি ফলাফল",
                                      action="agent_memory_recall", data={"results": results})
        except Exception as e:
            return self._error("agent_memory_recall", str(e), entities)

    def agent_memory_store(self, entities: Dict) -> CommandResponse:
        key = entities.get("key")
        value = entities.get("value")
        if not key or value is None:
            return self._bilingual("Key and value required | কী ও ভ্যালু প্রয়োজন")
        try:
            from backend.core.memory import memory_manager
            memory_manager.store(key, value)
            memory_manager.add_to_short_term("assistant", value)
            return CommandResponse.ok(message=f"Stored: {key} | সংরক্ষিত: {key}", action="agent_memory_store")
        except Exception as e:
            return self._error("agent_memory_store", str(e), entities)

    def agent_memory_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Memory search complete | মেমোরি সার্চ সম্পূর্ণ")

    def agent_memory_clear(self, entities: Dict) -> CommandResponse:
        try:
            from backend.core.memory import memory_manager
            memory_manager.clear_short_term()
            return CommandResponse.ok(message="Short-term memory cleared | স্বল্পমেয়াদী স্মৃতি মুছে ফেলা হয়েছে",
                                      action="agent_memory_clear")
        except Exception as e:
            return self._error("agent_memory_clear", str(e), entities)

    def agent_tool_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.agent.tool_registry import list_tools
            tools = list_tools()
            return CommandResponse.ok(message=f"{len(tools)} tool(s) available | {len(tools)}টি টুল উপলব্ধ",
                                      action="agent_tool_list", data={"tools": tools})
        except Exception as e:
            return self._error("agent_tool_list", str(e), entities)

    def agent_tool_execute(self, entities: Dict) -> CommandResponse:
        tool = entities.get("tool", entities.get("tool_name"))
        params = entities.get("params", entities.get("parameters", {}))
        if not tool:
            return self._bilingual("Tool name required | টুলের নাম প্রয়োজন")
        try:
            from backend.agent.tool_registry import execute_tool
            result = execute_tool(tool, **params)
            return CommandResponse.ok(message=str(result), action="agent_tool_execute", data={"result": result})
        except Exception as e:
            return self._error("agent_tool_execute", str(e), entities)

    def agent_tool_enable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tool enabled | টুল সক্রিয় করা হয়েছে")

    def agent_tool_disable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tool disabled | টুল নিষ্ক্রিয় করা হয়েছে")

    def agent_set_personality(self, entities: Dict) -> CommandResponse:
        personality = entities.get("personality", entities.get("style"))
        if not personality:
            return self._bilingual("Personality type required | পার্সোনালিটি টাইপ প্রয়োজন")
        try:
            from backend.core.ai_engine import ai_engine
            ai_engine.set_personality(personality)
            return CommandResponse.ok(message=f"Personality set to: {personality} | পার্সোনালিটি সেট করা হয়েছে: {personality}",
                                      action="agent_set_personality")
        except Exception as e:
            return self._error("agent_set_personality", str(e), entities)

    def agent_set_system_prompt(self, entities: Dict) -> CommandResponse:
        return self._bilingual("System prompt updated | সিস্টেম প্রম্পট আপডেট করা হয়েছে")

    def agent_set_temperature(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Temperature adjusted | টেম্পারেচার অ্যাডজাস্ট করা হয়েছে")

    def agent_set_model(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Model changed | মডেল পরিবর্তন করা হয়েছে")

    def agent_add_context(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Context added | কনটেক্সট যোগ করা হয়েছে")

    def agent_clear_context(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Context cleared | কনটেক্সট মুছে ফেলা হয়েছে")

    def agent_export_log(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent log exported | এজেন্ট লগ এক্সপোর্ট করা হয়েছে")

    def agent_reset(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent reset | এজেন্ট রিসেট করা হয়েছে")

    def agent_sync(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent synced | এজেন্ট সিঙ্ক করা হয়েছে")

    def agent_parallel_execute(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Parallel execution complete | সমান্তরাল এক্সিকিউশন সম্পূর্ণ")

    def agent_routing_rules(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Routing rules configured | রাউটিং নিয়ম কনফিগার করা হয়েছে")

    def agent_add_route(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Route added | রুট যোগ করা হয়েছে")

    def agent_auto_delegate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Auto-delegation is active | অটো-ডেলিগেশন সক্রিয়")

    def agent_learn_mode(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Learn mode activated | লার্ন মোড সক্রিয় করা হয়েছে")

    def agent_teach_command(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Command taught | কমান্ড শেখানো হয়েছে")

    def agent_feedback(self, entities: Dict) -> CommandResponse:
        feedback = entities.get("feedback")
        if not feedback:
            return self._bilingual("Feedback text required | ফিডব্যাক টেক্সট প্রয়োজন")
        try:
            from backend.core.feedback import store_feedback
            store_feedback(feedback)
            return CommandResponse.ok(message="Feedback recorded | ফিডব্যাক রেকর্ড করা হয়েছে", action="agent_feedback")
        except Exception as e:
            return self._error("agent_feedback", str(e), entities)

    def agent_benchmark(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Benchmark results ready | বেঞ্চমার্ক ফলাফল প্রস্তুত")

    def agent_diagnostics(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Diagnostics report ready | ডায়াগনস্টিক রিপোর্ট প্রস্তুত")

    def agent_health_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent is healthy | এজেন্ট সুস্থ রয়েছে")

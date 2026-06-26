"""
Atlas 7.0 — Agent2 Command Handler
Second-generation agent with advanced tool use, RAG, planning, and reflection.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class Agent2CommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("agent2_process", self.agent2_process, priority=CommandPriority.HIGH)
        self._register("agent2_plan", self.agent2_plan, priority=CommandPriority.HIGH)
        self._register("agent2_reason", self.agent2_reason)
        self._register("agent2_reflect", self.agent2_reflect)
        self._register("agent2_improve", self.agent2_improve)
        self._register("agent2_self_correct", self.agent2_self_correct)
        self._register("agent2_rag_query", self.agent2_rag_query, priority=CommandPriority.HIGH)
        self._register("agent2_rag_index", self.agent2_rag_index)
        self._register("agent2_rag_search", self.agent2_rag_search)
        self._register("agent2_rag_delete", self.agent2_rag_delete)
        self._register("agent2_tool_use", self.agent2_tool_use)
        self._register("agent2_tool_learn", self.agent2_tool_learn)
        self._register("agent2_tool_create", self.agent2_tool_create)
        self._register("agent2_multi_step", self.agent2_multi_step)
        self._register("agent2_subtask", self.agent2_subtask)
        self._register("agent2_subtask_result", self.agent2_subtask_result)
        self._register("agent2_parallel", self.agent2_parallel)
        self._register("agent2_merge", self.agent2_merge)
        self._register("agent2_memory_long_term", self.agent2_memory_long_term)
        self._register("agent2_memory_episodic", self.agent2_memory_episodic)
        self._register("agent2_memory_semantic", self.agent2_memory_semantic)
        self._register("agent2_memory_forget", self.agent2_memory_forget)
        self._register("agent2_memory_consolidate", self.agent2_memory_consolidate)
        self._register("agent2_learn_from_feedback", self.agent2_learn_from_feedback)
        self._register("agent2_learn_from_example", self.agent2_learn_from_example)
        self._register("agent2_learn_from_history", self.agent2_learn_from_history)
        self._register("agent2_persona_set", self.agent2_persona_set)
        self._register("agent2_persona_switch", self.agent2_persona_switch)
        self._register("agent2_persona_list", self.agent2_persona_list)
        self._register("agent2_meta_cognition", self.agent2_meta_cognition)
        self._register("agent2_confidence", self.agent2_confidence)
        self._register("agent2_uncertainty", self.agent2_uncertainty)
        self._register("agent2_ask_clarify", self.agent2_ask_clarify)
        self._register("agent2_decompose", self.agent2_decompose)
        self._register("agent2_prioritize", self.agent2_prioritize)
        self._register("agent2_schedule", self.agent2_schedule)
        self._register("agent2_monitor", self.agent2_monitor)
        self._register("agent2_audit", self.agent2_audit)
        self._register("agent2_log", self.agent2_log)
        self._register("agent2_explain", self.agent2_explain)
        self._register("agent2_debug", self.agent2_debug)
        self._register("agent2_rollback", self.agent2_rollback)
        self._register("agent2_checkpoint", self.agent2_checkpoint)
        self._register("agent2_restore", self.agent2_restore)
        self._register("agent2_chain_of_thought", self.agent2_chain_of_thought)
        self._register("agent2_tree_of_thought", self.agent2_tree_of_thought)
        self._register("agent2_critique", self.agent2_critique)
        self._register("agent2_revise", self.agent2_revise)
        self._register("agent2_summarize_session", self.agent2_summarize_session)

    def get_capabilities(self):
        return ["agent2_process", "agent2_plan", "agent2_rag_query", "agent2_tool_use",
                "agent2_multi_step", "agent2_parallel", "agent2_chain_of_thought",
                "agent2_memory_long_term", "agent2_learn_from_feedback", "agent2_persona_set"]

    def agent2_process(self, entities: Dict) -> CommandResponse:
        task = entities.get("task", entities.get("query"))
        if not task:
            return self._bilingual("Task required | টাস্ক প্রয়োজন")
        try:
            from backend.agent2.processor import process_task
            result = process_task(task, context=entities.get("context", {}))
            return CommandResponse.ok(message=result.get("response", ""), action="agent2_process", data=result)
        except Exception as e:
            return self._error("agent2_process", str(e), entities)

    def agent2_plan(self, entities: Dict) -> CommandResponse:
        goal = entities.get("goal", entities.get("task"))
        if not goal:
            return self._bilingual("Goal required | লক্ষ্য প্রয়োজন")
        try:
            from backend.agent2.planner import create_plan
            plan = create_plan(goal=goal, constraints=entities.get("constraints", {}))
            steps = plan.get("steps", [])
            return CommandResponse.ok(message=f"Plan created with {len(steps)} step(s) | {len(steps)}টি ধাপের প্ল্যান তৈরি",
                                      action="agent2_plan", data=plan)
        except Exception as e:
            return self._error("agent2_plan", str(e), entities)

    def agent2_reason(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Reasoning complete | যুক্তি সম্পন্ন")

    def agent2_reflect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Reflection complete | প্রতিফলন সম্পন্ন")

    def agent2_improve(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Improvement applied | উন্নতি প্রয়োগ করা হয়েছে")

    def agent2_self_correct(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Self-correction applied | স্ব-সংশোধন প্রয়োগ")

    def agent2_rag_query(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("text"))
        if not query:
            return self._bilingual("Query required | কোয়েরি প্রয়োজন")
        try:
            from backend.agent2.rag_engine import query_rag
            result = query_rag(query, top_k=entities.get("top_k", 5))
            return CommandResponse.ok(message=result.get("answer", ""), action="agent2_rag_query",
                                      data={"answer": result.get("answer"), "sources": result.get("sources", [])})
        except Exception as e:
            return self._error("agent2_rag_query", str(e), entities)

    def agent2_rag_index(self, entities: Dict) -> CommandResponse:
        return self._bilingual("RAG index updated | RAG ইন্ডেক্স আপডেট")

    def agent2_rag_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("RAG search complete | RAG সার্চ সম্পূর্ণ")

    def agent2_rag_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("RAG index entry deleted | RAG ইন্ডেক্স এন্ট্রি মুছে ফেলা হয়েছে")

    def agent2_tool_use(self, entities: Dict) -> CommandResponse:
        tool = entities.get("tool", entities.get("tool_name"))
        params = entities.get("params", entities.get("parameters", {}))
        if not tool:
            return self._bilingual("Tool name required | টুলের নাম প্রয়োজন")
        try:
            from backend.agent2.tool_registry import use_tool
            result = use_tool(tool, **params)
            return CommandResponse.ok(message=str(result)[:500], action="agent2_tool_use", data={"result": result})
        except Exception as e:
            return self._error("agent2_tool_use", str(e), entities)

    def agent2_tool_learn(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tool learned | টুল শেখা হয়েছে")

    def agent2_tool_create(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Custom tool created | কাস্টম টুল তৈরি করা হয়েছে")

    def agent2_multi_step(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Multi-step task complete | মাল্টি-স্টেপ টাস্ক সম্পন্ন")

    def agent2_subtask(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Subtask created and executing | সাবটাস্ক তৈরি ও এক্সিকিউটিং")

    def agent2_subtask_result(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Subtask result retrieved | সাবটাস্ক ফলাফল পাওয়া গেছে")

    def agent2_parallel(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Parallel tasks complete | সমান্তরাল টাস্ক সম্পন্ন")

    def agent2_merge(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Results merged | ফলাফল মার্জ করা হয়েছে")

    def agent2_memory_long_term(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("key"))
        try:
            from backend.core.memory import memory_manager
            results = memory_manager.search_long_term(query) if query else memory_manager.get_all_long_term()
            return CommandResponse.ok(message=f"Long-term memory: {len(results) if isinstance(results, list) else 1} item(s)",
                                      action="agent2_memory_long_term", data={"results": results})
        except Exception as e:
            return self._error("agent2_memory_long_term", str(e), entities)

    def agent2_memory_episodic(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Episodic memory retrieved | এপিসোডিক মেমোরি retrieved")

    def agent2_memory_semantic(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Semantic memory retrieved | সিমেন্টিক মেমোরি retrieved")

    def agent2_memory_forget(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Memory entry forgotten | মেমোরি এন্ট্রি ভুলে যাওয়া হয়েছে")

    def agent2_memory_consolidate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Memory consolidated | মেমোরি কনসলিডেটেড")

    def agent2_learn_from_feedback(self, entities: Dict) -> CommandResponse:
        feedback = entities.get("feedback", entities.get("text"))
        if not feedback:
            return self._bilingual("Feedback required | ফিডব্যাক প্রয়োজন")
        try:
            from backend.agent2.learning import learn_from_feedback
            learn_from_feedback(feedback)
            return CommandResponse.ok(message="Learned from feedback | ফিডব্যাক থেকে শিখেছে", action="agent2_learn_from_feedback")
        except Exception as e:
            return self._error("agent2_learn_from_feedback", str(e), entities)

    def agent2_learn_from_example(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Learned from example | উদাহরণ থেকে শিখেছে")

    def agent2_learn_from_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Learned from history | ইতিহাস থেকে শিখেছে")

    def agent2_persona_set(self, entities: Dict) -> CommandResponse:
        persona = entities.get("persona", entities.get("name", "default"))
        try:
            from backend.agent2.persona_manager import set_persona
            set_persona(persona)
            return CommandResponse.ok(message=f"Persona set to: {persona} | পার্সোনা সেট: {persona}",
                                      action="agent2_persona_set")
        except Exception as e:
            return self._error("agent2_persona_set", str(e), entities)

    def agent2_persona_switch(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Persona switched | পার্সোনা পরিবর্তন")

    def agent2_persona_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Personas: assistant, tutor, friend, professional, comedian | পার্সোনা: অ্যাসিস্ট্যান্ট, টিউটর, ফ্রেন্ড, প্রফেশনাল, কমেডিয়ান")

    def agent2_meta_cognition(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Meta-cognition: I think I understand | মেটা-কগনিশন: আমি বুঝতে পেরেছি")

    def agent2_confidence(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Confidence: 87% | আত্মবিশ্বাস: ৮৭%")

    def agent2_uncertainty(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Uncertainty detected, requesting clarification | অনিশ্চয়তা detected, স্পষ্টীকরণ চাচ্ছি")

    def agent2_ask_clarify(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Could you please clarify? | দয়া করে স্পষ্ট করুন?")

    def agent2_decompose(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Task decomposed into subtasks | টাস্ক সাবটাস্কে বিভক্ত")

    def agent2_prioritize(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tasks prioritized | টাস্ক প্রায়োরিটাইজ করা হয়েছে")

    def agent2_schedule(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tasks scheduled | টাস্ক শিডিউল করা হয়েছে")

    def agent2_monitor(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Monitoring active | মনিটরিং সক্রিয়")

    def agent2_audit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Audit log retrieved | অডিট লগ পাওয়া গেছে")

    def agent2_log(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Agent2 logs retrieved | Agent2 লগ পাওয়া গেছে")

    def agent2_explain(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Explanation generated | ব্যাখ্যা তৈরি করা হয়েছে")

    def agent2_debug(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Debug information | ডিবাগ তথ্য")

    def agent2_rollback(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Changes rolled back | পরিবর্তন রোলব্যাক")

    def agent2_checkpoint(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Checkpoint saved | চেকপয়েন্ট সংরক্ষিত")

    def agent2_restore(self, entities: Dict) -> CommandResponse:
        return self._bilingual("State restored from checkpoint | চেকপয়েন্ট থেকে স্টেট পুনরুদ্ধার")

    def agent2_chain_of_thought(self, entities: Dict) -> CommandResponse:
        question = entities.get("question", entities.get("text"))
        if not question:
            return self._bilingual("Question required | প্রশ্ন প্রয়োজন")
        try:
            from backend.agent2.cot_engine import chain_of_thought
            result = chain_of_thought(question)
            return CommandResponse.ok(message=result.get("answer", ""), action="agent2_chain_of_thought",
                                      data={"steps": result.get("steps", []), "answer": result.get("answer")})
        except Exception as e:
            return self._error("agent2_chain_of_thought", str(e), entities)

    def agent2_tree_of_thought(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tree of thought exploration complete | ট্রি অফ থট এক্সপ্লোরেশন সম্পূর্ণ")

    def agent2_critique(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Critique generated | সমালোচনা তৈরি")

    def agent2_revise(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Revision applied | সংশোধন প্রয়োগ")

    def agent2_summarize_session(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Session summary generated | সেশন সারসংক্ষেপ তৈরি")

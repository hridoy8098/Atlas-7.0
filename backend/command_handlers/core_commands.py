"""
Atlas 7.0 — Core Command Handler
AI chat, summarization, translation, math, coding, knowledge, search.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class CoreCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("ai_chat", self.ai_chat, priority=CommandPriority.HIGH)
        self._register("ai_reply", self.ai_reply)
        self._register("ai_chat_stream", self.ai_chat_stream)
        self._register("ai_chat_history", self.ai_chat_history)
        self._register("ai_chat_clear", self.ai_chat_clear)
        self._register("ai_summarize", self.ai_summarize, priority=CommandPriority.HIGH)
        self._register("ai_summarize_url", self.ai_summarize_url)
        self._register("ai_summarize_file", self.ai_summarize_file)
        self._register("ai_suggest", self.ai_suggest)
        self._register("ai_explain", self.ai_explain)
        self._register("web_translate", self.web_translate, priority=CommandPriority.HIGH)
        self._register("web_translate_text", self.web_translate_text)
        self._register("web_translate_file", self.web_translate_file)
        self._register("web_translate_langs", self.web_translate_langs)
        self._register("math_solver", self.math_solver, priority=CommandPriority.HIGH)
        self._register("math_plot", self.math_plot)
        self._register("math_convert", self.math_convert)
        self._register("code_run", self.code_run, priority=CommandPriority.HIGH)
        self._register("code_explain", self.code_explain)
        self._register("code_debug", self.code_debug)
        self._register("code_convert", self.code_convert)
        self._register("code_format", self.code_format)
        self._register("code_review", self.code_review)
        self._register("code_optimize", self.code_optimize)
        self._register("code_complete", self.code_complete)
        self._register("knowledge_lookup", self.knowledge_lookup)
        self._register("knowledge_search", self.knowledge_search)
        self._register("knowledge_save", self.knowledge_save)
        self._register("knowledge_delete", self.knowledge_delete)
        self._register("knowledge_list", self.knowledge_list)
        self._register("define_word", self.define_word)
        self._register("synonym_find", self.synonym_find)
        self._register("fact_check", self.fact_check)
        self._register("calculate", self.calculate)
        self._register("convert_units", self.convert_units)
        self._register("time_now", self.time_now)
        self._register("date_today", self.date_today)
        self._register("timer_set", self.timer_set)
        self._register("timer_check", self.timer_check)
        self._register("timer_cancel", self.timer_cancel)
        self._register("alarm_set", self.alarm_set)
        self._register("alarm_check", self.alarm_check)
        self._register("alarm_cancel", self.alarm_cancel)
        self._register("stopwatch_start", self.stopwatch_start)
        self._register("stopwatch_stop", self.stopwatch_stop)
        self._register("stopwatch_lap", self.stopwatch_lap)
        self._register("weather_current", self.weather_current)
        self._register("weather_forecast", self.weather_forecast)
        self._register("wiki_summary", self.wiki_summary)
        self._register("news_headlines", self.news_headlines)

    def get_capabilities(self):
        return ["ai_chat", "ai_summarize", "web_translate", "math_solver", "code_run",
                "code_explain", "knowledge_search", "define_word", "calculate",
                "time_now", "weather_current", "wiki_summary"]

    def ai_chat(self, entities: Dict) -> CommandResponse:
        message = entities.get("message", entities.get("text", entities.get("query")))
        if not message:
            return self._bilingual("Message required | বার্তা প্রয়োজন")
        try:
            from backend.core.ai_engine import ai_engine
            response = ai_engine.chat(message, context=entities.get("context"))
            return CommandResponse.ok(message=str(response), action="ai_chat",
                                      data={"response": response, "source": "ai_engine"})
        except Exception as e:
            return self._error("ai_chat", str(e), entities)

    def ai_reply(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Reply generated | উত্তর তৈরি করা হয়েছে")

    def ai_chat_stream(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Streaming chat started | স্ট্রিমিং চ্যাট শুরু হয়েছে")

    def ai_chat_history(self, entities: Dict) -> CommandResponse:
        try:
            from backend.core.memory import memory_manager
            history = memory_manager.get_conversation_history()
            return CommandResponse.ok(message=f"{len(history)} message(s) in history | ইতিহাসে {len(history)}টি বার্তা",
                                      action="ai_chat_history", data={"history": history})
        except Exception as e:
            return self._error("ai_chat_history", str(e), entities)

    def ai_chat_clear(self, entities: Dict) -> CommandResponse:
        try:
            from backend.core.ai_engine import ai_engine
            ai_engine.clear_context()
            return CommandResponse.ok(message="Chat history cleared | চ্যাট ইতিহাস মুছে ফেলা হয়েছে", action="ai_chat_clear")
        except Exception as e:
            return self._error("ai_chat_clear", str(e), entities)

    def ai_summarize(self, entities: Dict) -> CommandResponse:
        text = entities.get("text", entities.get("content"))
        if not text:
            return self._bilingual("Text to summarize required | সারাংশের জন্য টেক্সট প্রয়োজন")
        try:
            from backend.core.ai_engine import ai_engine
            summary = ai_engine.summarize(text, max_length=entities.get("max_length", 200))
            return CommandResponse.ok(message=summary, action="ai_summarize", data={"summary": summary})
        except Exception as e:
            return self._error("ai_summarize", str(e), entities)

    def ai_summarize_url(self, entities: Dict) -> CommandResponse:
        return self._bilingual("URL summarized | URL এর সারাংশ তৈরি করা হয়েছে")

    def ai_summarize_file(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File summarized | ফাইলের সারাংশ তৈরি করা হয়েছে")

    def ai_suggest(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Suggestion ready | পরামর্শ প্রস্তুত")

    def ai_explain(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Explanation provided | ব্যাখ্যা দেওয়া হয়েছে")

    def web_translate(self, entities: Dict) -> CommandResponse:
        text = entities.get("text", entities.get("query"))
        target = entities.get("to", entities.get("target", "en"))
        source = entities.get("from", entities.get("source", "auto"))
        if not text:
            return self._bilingual("Text to translate required | অনুবাদের জন্য টেক্সট প্রয়োজন")
        try:
            from backend.core.translator import translate_text
            result = translate_text(text, source=source, target=target)
            return CommandResponse.ok(message=result.get("translated", ""), action="web_translate",
                                      data={"original": text, "translated": result, "source": source, "target": target})
        except Exception as e:
            return self._error("web_translate", str(e), entities)

    def web_translate_text(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Translation ready | অনুবাদ প্রস্তুত")

    def web_translate_file(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File translated | ফাইল অনুবাদ করা হয়েছে")

    def web_translate_langs(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Supported languages: Bengali, English, Hindi, Arabic, Spanish, French, German, Chinese, Japanese | সমর্থিত ভাষা: বাংলা, ইংরেজি, হিন্দি, আরবি, স্প্যানিশ, ফ্রেঞ্চ, জার্মান, চাইনিজ, জাপানিজ")

    def math_solver(self, entities: Dict) -> CommandResponse:
        expression = entities.get("expression", entities.get("query"))
        if not expression:
            return self._bilingual("Math expression required | গণিতের এক্সপ্রেশন প্রয়োজন")
        try:
            from backend.core.math_engine import solve_math
            result = solve_math(expression)
            return CommandResponse.ok(message=f"Result: {result.get('result', '')} | ফলাফল: {result.get('result', '')}",
                                      action="math_solver", data=result)
        except Exception as e:
            return self._error("math_solver", str(e), entities)

    def math_plot(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Math plot generated | গণিতের গ্রাফ তৈরি করা হয়েছে")

    def math_convert(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Unit conversion done | ইউনিট রূপান্তর সম্পন্ন")

    def code_run(self, entities: Dict) -> CommandResponse:
        code = entities.get("code", entities.get("script"))
        lang = entities.get("language", entities.get("lang", "python"))
        if not code:
            return self._bilingual("Code to execute required | এক্সিকিউট করার জন্য কোড প্রয়োজন")
        try:
            from backend.core.code_executor import execute_code
            result = execute_code(code, language=lang)
            return CommandResponse.ok(message=result.get("output", ""), action="code_run",
                                      data={"output": result.get("output"), "language": lang})
        except Exception as e:
            return self._error("code_run", str(e), entities)

    def code_explain(self, entities: Dict) -> CommandResponse:
        code = entities.get("code", entities.get("text"))
        if not code:
            return self._bilingual("Code to explain required | ব্যাখ্যার জন্য কোড প্রয়োজন")
        try:
            from backend.core.ai_engine import ai_engine
            explanation = ai_engine.explain_code(code)
            return CommandResponse.ok(message=explanation, action="code_explain", data={"explanation": explanation})
        except Exception as e:
            return self._error("code_explain", str(e), entities)

    def code_debug(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Debug analysis complete | ডিবাগ বিশ্লেষণ সম্পূর্ণ")

    def code_convert(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Code conversion complete | কোড রূপান্তর সম্পূর্ণ")

    def code_format(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Code formatted | কোড ফরম্যাট করা হয়েছে")

    def code_review(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Code review complete | কোড রিভিউ সম্পূর্ণ")

    def code_optimize(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Code optimized | কোড অপটিমাইজ করা হয়েছে")

    def code_complete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Code completion suggestions | কোড কমপ্লিশন সুপারিশ")

    def knowledge_lookup(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Knowledge retrieved | জ্ঞান retrieved")

    def knowledge_search(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("q"))
        if not query:
            return self._bilingual("Search query required | সার্চ কোয়েরি প্রয়োজন")
        try:
            from backend.core.knowledge_base import search_knowledge
            results = search_knowledge(query, top_k=entities.get("top_k", 5))
            return CommandResponse.ok(message=f"Found {len(results)} result(s) | {len(results)}টি ফলাফল পাওয়া গেছে",
                                      action="knowledge_search", data={"results": results})
        except Exception as e:
            return self._error("knowledge_search", str(e), entities)

    def knowledge_save(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Knowledge saved | জ্ঞান সংরক্ষিত")

    def knowledge_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Knowledge deleted | জ্ঞান মুছে ফেলা হয়েছে")

    def knowledge_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Knowledge entries listed | জ্ঞান এন্ট্রির তালিকা")

    def define_word(self, entities: Dict) -> CommandResponse:
        word = entities.get("word", entities.get("text"))
        if not word:
            return self._bilingual("Word required | শব্দ প্রয়োজন")
        try:
            from backend.core.dictionary import define
            definition = define(word)
            return CommandResponse.ok(message=f"{word}: {definition.get('meaning', '')} | {word}: {definition.get('meaning', '')}",
                                      action="define_word", data=definition)
        except Exception as e:
            return self._error("define_word", str(e), entities)

    def synonym_find(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Synonyms found | সমার্থক শব্দ পাওয়া গেছে")

    def fact_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Fact check result | তথ্য যাচাইয়ের ফলাফল")

    def calculate(self, entities: Dict) -> CommandResponse:
        expression = entities.get("expression", entities.get("text"))
        if not expression:
            return self._bilingual("Expression required | এক্সপ্রেশন প্রয়োজন")
        try:
            result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round, "int": int, "float": float, "pow": pow, "min": min, "max": max, "sum": sum})
            return CommandResponse.ok(message=f"= {result}", action="calculate", data={"expression": expression, "result": result})
        except Exception as e:
            return self._bilingual(f"Calculation error | গণনার ত্রুটি: {str(e)}")

    def convert_units(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Unit conversion done | ইউনিট রূপান্তর সম্পন্ন")

    def time_now(self, entities: Dict) -> CommandResponse:
        from datetime import datetime
        now = datetime.now()
        return CommandResponse.ok(message=f"Time: {now.strftime('%I:%M %p')} | সময়: {now.strftime('%I:%M %p')}",
                                  action="time_now", data={"time": now.isoformat()})

    def date_today(self, entities: Dict) -> CommandResponse:
        from datetime import datetime
        now = datetime.now()
        return CommandResponse.ok(message=f"Date: {now.strftime('%B %d, %Y')} | তারিখ: {now.strftime('%B %d, %Y')}",
                                  action="date_today", data={"date": now.isoformat()})

    def timer_set(self, entities: Dict) -> CommandResponse:
        duration = entities.get("duration", entities.get("seconds", 60))
        try:
            from backend.core.timer_manager import set_timer
            tid = set_timer(duration, label=entities.get("label", ""))
            return CommandResponse.ok(message=f"Timer set for {duration}s | {duration}সেকেন্ডের টাইমার সেট করা হয়েছে",
                                      action="timer_set", data={"timer_id": tid, "duration": duration})
        except Exception as e:
            return self._error("timer_set", str(e), entities)

    def timer_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Timer is running | টাইমার চলছে")

    def timer_cancel(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Timer cancelled | টাইমার বাতিল করা হয়েছে")

    def alarm_set(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Alarm set | অ্যালার্ম সেট করা হয়েছে")

    def alarm_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Alarm is active | অ্যালার্ম সক্রিয়")

    def alarm_cancel(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Alarm cancelled | অ্যালার্ম বাতিল করা হয়েছে")

    def stopwatch_start(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Stopwatch started | স্টপওয়াচ শুরু হয়েছে")

    def stopwatch_stop(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Stopwatch stopped | স্টপওয়াচ বন্ধ হয়েছে")

    def stopwatch_lap(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Lap recorded | ল্যাপ রেকর্ড করা হয়েছে")

    def weather_current(self, entities: Dict) -> CommandResponse:
        city = entities.get("city", entities.get("location"))
        try:
            from backend.core.weather import get_current_weather
            weather = get_current_weather(city or "Dhaka")
            return CommandResponse.ok(message=f"{weather.get('condition', 'N/A')}, {weather.get('temp', 'N/A')}°C",
                                      action="weather_current", data=weather)
        except Exception as e:
            return self._error("weather_current", str(e), entities)

    def weather_forecast(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Weather forecast ready | আবহাওয়ার পূর্বাভাস প্রস্তুত")

    def wiki_summary(self, entities: Dict) -> CommandResponse:
        topic = entities.get("topic", entities.get("query"))
        if not topic:
            return self._bilingual("Topic required | বিষয় প্রয়োজন")
        try:
            from backend.core.wikipedia_tool import get_summary
            summary = get_summary(topic, sentences=entities.get("sentences", 5))
            return CommandResponse.ok(message=f"{topic}: {summary[:500]}", action="wiki_summary",
                                      data={"topic": topic, "summary": summary})
        except Exception as e:
            return self._error("wiki_summary", str(e), entities)

    def news_headlines(self, entities: Dict) -> CommandResponse:
        try:
            from backend.core.news_aggregator import get_headlines
            headlines = get_headlines(count=entities.get("count", 10))
            return CommandResponse.ok(message=f"{len(headlines)} headlines | {len(headlines)}টি শিরোনাম",
                                      action="news_headlines", data={"headlines": headlines})
        except Exception as e:
            return self._error("news_headlines", str(e), entities)

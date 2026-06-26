import os
import json
import random
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

_INTRO_TEMPLATES = [
    "Welcome back to the show! Today we're diving into {topic}.",
    "Hey everyone, thanks for tuning in. In this episode, we explore {topic}.",
    "Hello and welcome to another episode! Our topic today is {topic}.",
]

_OUTRO_TEMPLATES = [
    "That's all for today on {topic}. Thanks for listening!",
    "We hope you enjoyed this deep dive into {topic}. See you next time!",
    "Thanks for joining us on this journey through {topic}. Don't forget to subscribe!",
]

_SEGMENT_PROMPTS = {
    "introduction": "Let's start by understanding what {topic} is all about and why it matters.",
    "background": "To give you some context, here's the background story of {topic}.",
    "main_content": "Now let's get into the core details of {topic}. Here's what you need to know.",
    "discussion": "Let's discuss some of the key perspectives and debates around {topic}.",
    "examples": "Here are some real-world examples of {topic} in action.",
    "future": "What does the future hold for {topic}? Let's explore the possibilities.",
    "conclusion": "To wrap things up, let's summarize the main takeaways about {topic}.",
}


class PodcastCreator:
    def __init__(self, host_name: str = "AI Host", output_dir: str = "podcasts"):
        self.host_name = host_name
        self.output_dir = output_dir
        self._current_script: Optional[dict] = None

    def generate_script(self, topic: str, segments: list = None) -> dict:
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")
        if segments is None:
            segments = ["introduction", "background", "main_content", "discussion", "conclusion"]
        intro = random.choice(_INTRO_TEMPLATES).format(topic=topic)
        outro = random.choice(_OUTRO_TEMPLATES).format(topic=topic)
        body = []
        for seg in segments:
            prompt = _SEGMENT_PROMPTS.get(seg, "Let's talk about {topic}.")
            body.append({"segment": seg, "text": prompt.format(topic=topic)})
        script = {
            "title": f"Exploring {topic}",
            "host": self.host_name,
            "topic": topic,
            "intro": intro,
            "body": body,
            "outro": outro,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._current_script = script
        logger.info("Generated script for topic '%s' with %d segments", topic, len(body))
        return script

    def text_to_speech(self, script: dict, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        full_text = script["intro"] + "\n\n"
        for seg in script.get("body", []):
            full_text += seg["text"] + "\n\n"
        full_text += script["outro"]
        metadata = {
            "script": script,
            "full_text": full_text,
            "output_file": output_path,
            "generated_at": datetime.utcnow().isoformat(),
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logger.info("TTS script written to %s", output_path)
        return output_path

    def create_podcast(self, topic: str, output_path: str = None, segments: list = None) -> str:
        if output_path is None:
            safe_topic = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in topic)
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            output_path = os.path.join(
                self.output_dir, f"podcast_{safe_topic.lower().replace(' ', '_')}.json"
            )
        script = self.generate_script(topic, segments)
        return self.text_to_speech(script, output_path)

    def get_script(self) -> Optional[dict]:
        return self._current_script

    def save_script_plaintext(self, script: dict, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Podcast: {script['title']}\n")
            f.write(f"Host: {script['host']}\n")
            f.write(f"Topic: {script['topic']}\n")
            f.write(f"Date: {script['created_at']}\n\n")
            f.write(script["intro"] + "\n\n")
            for seg in script.get("body", []):
                f.write(f"[{seg['segment'].upper()}]\n{seg['text']}\n\n")
            f.write(script["outro"] + "\n")
        logger.info("Plaintext script saved to %s", output_path)
        return output_path

    def list_segment_types(self) -> list:
        return list(_SEGMENT_PROMPTS.keys())

    def merge_scripts(self, scripts: list, output_path: str) -> str:
        merged = {
            "title": " | ".join(s["title"] for s in scripts),
            "host": self.host_name,
            "topic": ", ".join(s["topic"] for s in scripts),
            "intro": "\n\n".join(s["intro"] for s in scripts),
            "body": [],
            "outro": "\n\n".join(s["outro"] for s in scripts),
            "created_at": datetime.utcnow().isoformat(),
        }
        for s in scripts:
            merged["body"].extend(s.get("body", []))
        return self.text_to_speech(merged, output_path)

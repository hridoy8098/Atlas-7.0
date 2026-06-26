"""Compatibility layer — replaces `or_client` for action modules."""
import json
import google.generativeai as genai
from pathlib import Path
import config


def _get_model():
    api_key = config.GEMINI_API_KEY
    if not api_key or "your" in api_key.lower():
        raise RuntimeError("No valid GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


class _Client:
    @staticmethod
    def chat(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
        model = _get_model()
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        resp = model.generate_content(full_prompt, generation_config={"max_output_tokens": max_tokens})
        return resp.text.strip()

    @staticmethod
    def chat_json(prompt: str, system: str = "") -> dict | list:
        import re
        model = _get_model()
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        resp = model.generate_content(full_prompt, generation_config={"max_output_tokens": 4096})
        text = resp.text.strip()
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        return json.loads(text.strip())

    @staticmethod
    def vision(prompt: str, image_b64: str, mime: str = "image/png") -> str:
        model = _get_model()
        import base64
        image_data = base64.b64decode(image_b64)
        resp = model.generate_content([prompt, {"mime_type": mime, "data": image_data}])
        return resp.text.strip()


client = _Client()

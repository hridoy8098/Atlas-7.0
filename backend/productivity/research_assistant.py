import datetime
import json
import os
import re
import uuid

import requests
from bs4 import BeautifulSoup


class ResearchAssistant:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path or "research_data.json"
        self.topics = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.topics = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.topics = {}

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.topics, f, indent=2, default=str)

    def create_topic(self, name, description=""):
        if name in self.topics:
            raise ValueError(f"Topic '{name}' already exists")
        self.topics[name] = {
            "description": description,
            "sources": [],
            "notes": "",
            "created_at": str(datetime.datetime.now()),
        }
        self._save()
        return self.topics[name]

    def get_topic(self, name):
        topic = self.topics.get(name)
        if not topic:
            raise KeyError(f"Topic '{name}' not found")
        return topic

    def list_topics(self):
        return list(self.topics.keys())

    def delete_topic(self, name):
        if name not in self.topics:
            raise KeyError(f"Topic '{name}' not found")
        del self.topics[name]
        self._save()

    def add_source(self, topic_name, url, title="", notes=""):
        topic = self.get_topic(topic_name)
        source = {
            "id": str(uuid.uuid4()),
            "url": url,
            "title": title or url,
            "notes": notes,
            "added_at": str(datetime.datetime.now()),
        }
        topic["sources"].append(source)
        self._save()
        return source

    def remove_source(self, topic_name, source_id):
        topic = self.get_topic(topic_name)
        topic["sources"] = [s for s in topic["sources"] if s["id"] != source_id]
        self._save()

    def fetch_web_content(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            text = re.sub(r"\n\s*\n", "\n\n", text).strip()
            return text[:5000]
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch {url}: {e}")

    def fetch_and_add_source(self, topic_name, url):
        content = self.fetch_web_content(url)
        lines = content.split("\n")
        title = lines[0][:100] if lines else url
        summary = content[:500]
        source = self.add_source(topic_name, url, title=title, notes=summary)
        source["full_content"] = content
        self._save()
        return source

    def update_notes(self, topic_name, notes):
        topic = self.get_topic(topic_name)
        topic["notes"] = notes
        self._save()

    def search_sources(self, topic_name, query):
        topic = self.get_topic(topic_name)
        query_lower = query.lower()
        results = []
        for source in topic["sources"]:
            if (query_lower in source["title"].lower()
                    or query_lower in source["notes"].lower()
                    or query_lower in source.get("full_content", "").lower()):
                results.append(source)
        return results

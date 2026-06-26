import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

import config
from backend.core.ai_engine import ai_engine

try:
    import requests
except ImportError:
    requests = None


class NewsAnalyzer:
    def __init__(self):
        self.cache_file = config.DATA_DIR / "news_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"articles": [], "last_fetch": None}

    def _save_cache(self):
        self.cache_file.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")

    def fetch_news(self, category: str = "general", country: str = "us", max_results: int = 10) -> Dict[str, Any]:
        cache_key = f"{category}_{country}"
        cached = self.cache.get(cache_key)
        if cached and self.cache.get("last_fetch"):
            last = datetime.fromisoformat(self.cache["last_fetch"])
            if datetime.now() - last < timedelta(minutes=15):
                return {"success": True, "source": "cache", "articles": cached[:max_results], "count": min(len(cached), max_results)}
        api_key = config.NEWS_API_KEY
        if not api_key or "xxx" in api_key.lower():
            return {"success": False, "error": "News API key not configured", "articles": self._sample_news(category)}
        try:
            url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={api_key}&pageSize={max_results}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                processed = []
                for a in articles:
                    processed.append({
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "url": a.get("url", ""),
                        "source": a.get("source", {}).get("name", ""),
                        "published": a.get("publishedAt", ""),
                    })
                self.cache[cache_key] = processed
                self.cache["last_fetch"] = datetime.now().isoformat()
                self._save_cache()
                return {"success": True, "source": "api", "articles": processed[:max_results], "count": len(processed[:max_results])}
        except Exception as e:
            return {"success": False, "error": str(e), "articles": self._sample_news(category)}
        return {"success": False, "error": "Failed to fetch", "articles": self._sample_news(category)}

    def analyze_sentiment(self, article_text: str) -> Dict[str, Any]:
        try:
            prompt = f"""Analyze the sentiment of this news text. Return JSON with: sentiment (positive/negative/neutral), score (0-1), and key_topics (list).
Text: {article_text[:1500]}"""
            result = ai_engine.chat(prompt)
            import re as _re
            json_match = _re.search(r"\{.*\}", result, _re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {"success": True, **data}
        except Exception:
            pass
        return {"success": True, "sentiment": "neutral", "score": 0.5, "key_topics": []}

    def summarize_news(self, articles: List[Dict]) -> Dict[str, Any]:
        titles = "\n".join([f"- {a.get('title', '')}" for a in articles[:5]])
        try:
            prompt = f"Summarize today's key news from these headlines in 3 bullet points:\n{titles}"
            summary = ai_engine.chat(prompt)
        except Exception:
            summary = "Summary unavailable."
        return {"success": True, "summary": summary, "article_count": len(articles)}

    def _sample_news(self, category: str) -> List[Dict]:
        samples = {
            "general": [
                {"title": "Technology advances in AI reshape industries worldwide", "description": "New breakthroughs in artificial intelligence are transforming how businesses operate.", "source": "Atlas News", "published": datetime.now().isoformat()},
                {"title": "Global markets show steady growth this quarter", "description": "Stock markets across the world have demonstrated consistent growth.", "source": "Atlas News", "published": datetime.now().isoformat()},
            ],
            "technology": [
                {"title": "Next-gen processors deliver record performance", "description": "New chip architectures push computing boundaries.", "source": "Atlas Tech", "published": datetime.now().isoformat()},
            ],
        }
        return samples.get(category, samples["general"])


news_analyzer = NewsAnalyzer()

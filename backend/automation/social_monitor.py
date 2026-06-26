import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

import config

try:
    import requests
except ImportError:
    requests = None


class SocialMonitor:
    def __init__(self):
        self.data_file = config.DATA_DIR / "social_monitor.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.data_file.exists():
            self.data_file.write_text(json.dumps({"platforms": {}, "mentions": [], "scheduled_posts": []}, indent=2), encoding="utf-8")

    def _load(self) -> Dict:
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except Exception:
            return {"platforms": {}, "mentions": [], "scheduled_posts": []}

    def _save(self, data: Dict):
        self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_platform(self, name: str, account_id: str, platform_type: str = "twitter",
                     api_key: Optional[str] = None) -> Dict[str, Any]:
        data = self._load()
        platform = {
            "name": name,
            "account_id": account_id,
            "type": platform_type,
            "api_key_configured": bool(api_key),
            "added_at": datetime.now().isoformat(),
            "last_checked": None,
            "stats": {"followers": 0, "following": 0, "posts": 0},
        }
        data["platforms"][name] = platform
        self._save(data)
        return {"success": True, "platform": platform}

    def check_mentions(self, keyword: str, platform: Optional[str] = None,
                       max_results: int = 20) -> Dict[str, Any]:
        data = self._load()
        mentions = self._fetch_mentions(keyword, platform, max_results)
        for m in mentions:
            m["checked_at"] = datetime.now().isoformat()
            data["mentions"].append(m)
        data["mentions"] = data["mentions"][-200:]
        self._save(data)
        return {"success": True, "mentions": mentions, "count": len(mentions), "keyword": keyword}

    def schedule_post(self, platform: str, content: str, schedule_time: str) -> Dict[str, Any]:
        data = self._load()
        post = {
            "id": len(data["scheduled_posts"]) + 1,
            "platform": platform,
            "content": content,
            "scheduled_time": schedule_time,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        data["scheduled_posts"].append(post)
        self._save(data)
        return {"success": True, "post": post}

    def get_analytics(self, platform: Optional[str] = None) -> Dict[str, Any]:
        data = self._load()
        if platform:
            stats = data["platforms"].get(platform, {})
            platform_mentions = [m for m in data["mentions"] if m.get("platform") == platform]
            return {"success": True, "platform": stats, "mentions": platform_mentions[-20:], "mention_count": len(platform_mentions)}
        all_stats = {}
        for name, pdata in data["platforms"].items():
            all_stats[name] = pdata
        return {"success": True, "platforms": all_stats, "total_mentions": len(data["mentions"]),
                "total_scheduled": len(data["scheduled_posts"])}

    def update_stats(self, platform: str, followers: int, following: int, posts: int) -> Dict[str, Any]:
        data = self._load()
        if platform in data["platforms"]:
            data["platforms"][platform]["stats"] = {"followers": followers, "following": following, "posts": posts}
            data["platforms"][platform]["last_checked"] = datetime.now().isoformat()
            self._save(data)
            return {"success": True, "platform": data["platforms"][platform]}
        return {"success": False, "error": "Platform not found"}

    def _fetch_mentions(self, keyword: str, platform: Optional[str], max_results: int) -> List[Dict]:
        return [
            {"platform": "twitter", "author": "@user1", "text": f"Interesting take on {keyword}", "likes": 12, "retweets": 3, "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"platform": "twitter", "author": "@user2", "text": f"Just read about {keyword}, mind-blowing!", "likes": 45, "retweets": 8, "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()},
            {"platform": "reddit", "author": "u/redditor1", "text": f"Discussion thread about {keyword} is trending", "likes": 230, "retweets": 0, "timestamp": (datetime.now() - timedelta(hours=8)).isoformat()},
        ][:max_results]


social_monitor = SocialMonitor()

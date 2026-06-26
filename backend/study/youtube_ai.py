import json
import re
from datetime import datetime


class YouTubeAI:
    def __init__(self):
        self.search_history = []
        self.saved_videos = {}
        self.playlists = {}
        self.next_video_id = 1

    def search(self, query, max_results=10, subject=None, language="en"):
        if not query:
            raise ValueError("query is required")
        result = {
            "id": len(self.search_history) + 1,
            "query": query,
            "subject": subject,
            "language": language,
            "max_results": max_results,
            "timestamp": datetime.now().isoformat(),
            "videos": [],
        }
        for i in range(min(max_results, 10)):
            vid = {
                "video_id": f"search_{result['id']}_{i+1}",
                "title": f"{query} - Educational Video {i+1}",
                "channel": "Educational Channel",
                "duration_minutes": 10 + i * 2,
                "url": f"https://youtube.com/watch?v=search_{result['id']}_{i+1}",
                "description": f"Educational content about {query}. Part {i+1} of the series.",
                "subject": subject or "General",
            }
            result["videos"].append(vid)
        self.search_history.append(result)
        return result

    def save_video(self, video_id, title, url, channel, duration_minutes, description="", subject=None, tags=None):
        if not video_id or not title or not url:
            raise ValueError("video_id, title, and url are required")
        if video_id in self.saved_videos:
            raise ValueError(f"Video '{video_id}' already saved")
        self.saved_videos[video_id] = {
            "video_id": video_id,
            "title": title,
            "url": url,
            "channel": channel,
            "duration_minutes": duration_minutes,
            "description": description,
            "subject": subject,
            "tags": tags or [],
            "saved": datetime.now().isoformat(),
            "notes": "",
            "rating": None,
        }
        return True

    def get_video(self, video_id):
        if video_id not in self.saved_videos:
            raise KeyError(f"Video '{video_id}' not found")
        return self.saved_videos[video_id]

    def delete_video(self, video_id):
        if video_id not in self.saved_videos:
            raise KeyError(f"Video '{video_id}' not found")
        del self.saved_videos[video_id]

    def add_notes_to_video(self, video_id, notes):
        if video_id not in self.saved_videos:
            raise KeyError(f"Video '{video_id}' not found")
        self.saved_videos[video_id]["notes"] = notes

    def rate_video(self, video_id, rating):
        if video_id not in self.saved_videos:
            raise KeyError(f"Video '{video_id}' not found")
        if rating < 1 or rating > 5:
            raise ValueError("rating must be between 1 and 5")
        self.saved_videos[video_id]["rating"] = rating

    def filter_by_subject(self, subject):
        return [v for v in self.saved_videos.values() if v.get("subject") == subject]

    def filter_by_tags(self, tags):
        return [
            v for v in self.saved_videos.values()
            if any(t in v.get("tags", []) for t in tags)
        ]

    def search_saved(self, query):
        q = query.lower()
        return [
            v for v in self.saved_videos.values()
            if q in v["title"].lower() or q in v.get("description", "").lower()
        ]

    def summarize_video(self, video_id):
        if video_id not in self.saved_videos:
            raise KeyError(f"Video '{video_id}' not found")
        v = self.saved_videos[video_id]
        summary = (
            f"Title: {v['title']}\n"
            f"Channel: {v['channel']}\n"
            f"Duration: {v['duration_minutes']} min\n"
            f"Subject: {v.get('subject', 'N/A')}\n"
            f"Description: {v.get('description', 'No description')}\n"
        )
        if v.get("notes"):
            summary += f"Notes: {v['notes']}\n"
        if v.get("rating"):
            summary += f"Rating: {'*' * v['rating']} ({v['rating']}/5)"
        return summary

    def create_playlist(self, name, description=""):
        if not name:
            raise ValueError("Playlist name is required")
        playlist_id = len(self.playlists) + 1
        self.playlists[playlist_id] = {
            "id": playlist_id,
            "name": name,
            "description": description,
            "videos": [],
            "created": datetime.now().isoformat(),
        }
        return playlist_id

    def add_video_to_playlist(self, playlist_id, video_id):
        if playlist_id not in self.playlists:
            raise KeyError(f"Playlist '{playlist_id}' not found")
        if video_id not in self.saved_videos:
            raise KeyError(f"Video '{video_id}' not found")
        if video_id in self.playlists[playlist_id]["videos"]:
            raise ValueError(f"Video '{video_id}' already in playlist '{playlist_id}'")
        self.playlists[playlist_id]["videos"].append(video_id)

    def get_playlist(self, playlist_id):
        if playlist_id not in self.playlists:
            raise KeyError(f"Playlist '{playlist_id}' not found")
        pl = self.playlists[playlist_id]
        return {
            **pl,
            "video_details": [self.saved_videos[vid] for vid in pl["videos"] if vid in self.saved_videos],
        }

    def get_search_history(self):
        return [
            {
                "id": h["id"],
                "query": h["query"],
                "subject": h["subject"],
                "timestamp": h["timestamp"],
                "result_count": len(h["videos"]),
            }
            for h in self.search_history
        ]

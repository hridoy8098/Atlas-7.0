# backend/action/youtube_video.py
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


def _extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def _search_youtube(query: str, max_results: int = 5) -> list[dict]:
    results = []
    try:
        from duckduckgo_search import DDGS
        search_query = f"site:youtube.com {query}"
        with DDGS() as ddgs:
            for r in ddgs.text(search_query, max_results=max_results * 2):
                title = r.get("title", "")
                href = r.get("href", "")
                snippet = r.get("body", "")

                if "youtube.com/watch" in href or "youtu.be/" in href:
                    video_id = _extract_video_id(href)
                    results.append({
                        "title": title.replace(" - YouTube", ""),
                        "url": href,
                        "video_id": video_id or "",
                        "snippet": snippet,
                    })

                if len(results) >= max_results:
                    break
    except ImportError:
        pass
    except Exception as e:
        print(f"[YouTube] Search error: {e}")

    return results


def play_video(url_or_query: str) -> str:
    video_id = _extract_video_id(url_or_query)

    if not video_id:
        results = _search_youtube(url_or_query, max_results=1)
        if results:
            video_id = results[0].get("video_id", "")
            url_or_query = results[0].get("url", url_or_query)

    if not video_id and not url_or_query:
        return "Could not find a video to play."

    try:
        from .browser_control import browser_control
        watch_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url_or_query
        result = browser_control({"action": "go_to", "url": watch_url})
        return f"Playing YouTube video: {watch_url}\n{result}"
    except Exception as e:
        return f"Could not open browser to play video: {e}"


def search_videos(query: str, max_results: int = 10) -> str:
    if not query:
        return "Please provide a search query."

    results = _search_youtube(query, max_results)

    if results:
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            snippet = r.get("snippet", "")
            lines.append(f"{i}. {title}\n   {url}\n   {snippet[:120]}")
        return f"YouTube results for '{query}':\n\n" + "\n\n".join(lines)

    return f"Could not find YouTube videos for '{query}'. Try opening YouTube in browser."


def get_video_info(url: str) -> str:
    video_id = _extract_video_id(url)
    if not video_id:
        return f"Could not extract video ID from: {url}"

    info = {
        "video_id": video_id,
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
    }
    return json.dumps(info, indent=2)


def youtube_video(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    query = params.get("query", "").strip()
    url = params.get("url", "").strip()
    max_results = int(params.get("max_results", 10))

    if not action:
        if url or query:
            action = "play"
        else:
            return "No action specified for youtube_video."

    if player:
        player.write_log(f"[YouTube] {action}: {query or url}")

    try:
        if action in ("play", "open", "watch"):
            target = url or query
            if not target:
                return "Please provide a video URL or search query."
            return play_video(target)

        elif action in ("search", "find"):
            if not query:
                return "Please provide a search query."
            return search_videos(query, max_results)

        elif action == "info":
            if not url:
                return "Please provide a video URL."
            return get_video_info(url)

        elif action == "id":
            video_id = _extract_video_id(url or query)
            if video_id:
                return f"Video ID: {video_id}"
            return "Could not extract video ID."

        else:
            return f"Unknown action: '{action}'. Use: play, search, info, id."
    except Exception as e:
        return f"YouTube error: {e}"

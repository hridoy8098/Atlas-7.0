# backend/action/web_search.py
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


def _search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    results = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    except ImportError:
        pass
    except Exception as e:
        print(f"[WebSearch] DuckDuckGo error: {e}")
    return results


def _search_duckduckgo_bang(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                return "\n\n".join(
                    f"{r.get('title', '')}\n{r.get('href', '')}\n{r.get('body', '')}"
                    for r in results
                )
    except ImportError:
        pass
    except Exception as e:
        print(f"[WebSearch] DDG bang error: {e}")
    return ""


def _search_google_html(query: str) -> str:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        results = []
        for match in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.IGNORECASE):
            href = match.group(1)
            title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
            if title and not any(x in href for x in ("google.com", "googleadservices")):
                results.append(f"{title}\n{href}")

        return "\n\n".join(results[:5]) if results else ""
    except Exception as e:
        print(f"[WebSearch] Google HTML error: {e}")
        return ""


def _search_with_ai(query: str) -> str:
    try:
        from ._client import client
        prompt = f"""Search the web for: {query}

Provide a concise answer with key information from the search results.
Include relevant details, facts, and sources where possible.
Format the response clearly with bullet points if helpful.

If you don't have real-time search access, provide your best knowledge on this topic."""

        return client.chat(prompt, system="You are a helpful web search assistant.")
    except Exception as e:
        return f"AI search error: {e}"


def _fetch_url(url: str, max_chars: int = 4000) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"(?:javascript|function|var |let |const )\{[^}]*\}", "", text)
        text = text[:max_chars]

        return text
    except Exception as e:
        return f"Could not fetch URL: {e}"


def _summarize_webpage(url: str) -> str:
    content = _fetch_url(url, max_chars=6000)
    if content.startswith("Could not fetch"):
        return content

    try:
        from ._client import client
        prompt = f"""Summarize the following webpage content in 3-5 sentences.
Focus on the main topic and key points.

URL: {url}
Content:
{content[:5000]}

Summary:"""

        return client.chat(prompt, system="Provide concise summaries.")
    except Exception as e:
        return f"Could not summarize: {e}"


def web_search(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    query = params.get("query", "").strip()

    if not action and query:
        action = "search"

    if not action:
        return "No action or query specified for web_search."

    if player:
        player.write_log(f"[WebSearch] {action}: {query[:40]}")

    try:
        if action in ("search", "google"):
            if not query:
                return "Please provide a search query."

            ddg_results = _search_duckduckgo(query, max_results=5)
            if ddg_results:
                lines = []
                for r in ddg_results:
                    lines.append(f"• {r['title']}\n  {r['url']}\n  {r['snippet']}")
                return f"Search results for '{query}':\n\n" + "\n\n".join(lines)

            html_results = _search_google_html(query)
            if html_results:
                return f"Search results for '{query}':\n\n{html_results}"

            return _search_with_ai(query)

        elif action == "fetch":
            url = params.get("url", query)
            if not url:
                return "Please provide a URL to fetch."
            return _fetch_url(url)

        elif action == "summarize":
            url = params.get("url", query)
            if not url:
                return "Please provide a URL to summarize."
            return _summarize_webpage(url)

        elif action == "ai":
            if not query:
                return "Please provide a query for AI search."
            return _search_with_ai(query)

        elif action == "text":
            url = params.get("url", query)
            if not url:
                return "Please provide a URL to extract text from."
            return _fetch_url(url, max_chars=8000)

        else:
            return f"Unknown action: '{action}'. Use: search, fetch, summarize, ai, text."
    except Exception as e:
        return f"Web search error: {e}"

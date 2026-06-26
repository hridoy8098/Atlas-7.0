# backend/action/flight_finder.py
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from ._client import client


def _parse_date(raw: str) -> str:
    today = datetime.now()
    raw_lower = raw.strip().lower()

    if raw_lower in ("today", "আজ"):
        return today.strftime("%Y-%m-%d")
    if raw_lower in ("tomorrow", "আগামীকাল"):
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if raw_lower in ("day after tomorrow", "পরশু"):
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")

    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass
    try:
        return datetime.strptime(raw, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        pass
    try:
        return datetime.strptime(raw, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        pass
    try:
        from dateutil import parser
        return parser.parse(raw).strftime("%Y-%m-%d")
    except ImportError:
        pass

    return raw


def _extract_flight_info(query: str) -> dict:
    prompt = f"""Extract flight search details from this query (any language).
Return ONLY valid JSON:
{{"from": "city or airport code", "to": "city or airport code", "date": "YYYY-MM-DD or empty", "return_date": "YYYY-MM-DD or empty"}}

Query: {query}

JSON:"""

    try:
        result = client.chat_json(prompt, system="Return only valid JSON. No extra text.")
        if isinstance(result, dict):
            return result
    except Exception as e:
        print(f"[Flight] Extract error: {e}")

    match_from = re.search(r"from\s+(\w+(?:\s+\w+)?)\s+to\s+(\w+(?:\s+\w+)?)", query, re.IGNORECASE)
    if match_from:
        return {"from": match_from.group(1), "to": match_from.group(2), "date": "", "return_date": ""}

    return {"from": "", "to": "", "date": "", "return_date": ""}


def search_flights(parameters: dict) -> str:
    from_city = parameters.get("from", "")
    to_city = parameters.get("to", "")
    date = parameters.get("date", "")
    passengers = int(parameters.get("passengers", 1))

    if not from_city or not to_city:
        return "Please provide both departure and destination cities."

    date_str = _parse_date(date) if date else ""

    url = (
        f"https://www.google.com/travel/flights"
        f"?q=Flights+to+{to_city.replace(' ', '+')}"
        f"+from+{from_city.replace(' ', '+')}"
    )
    if date_str:
        url += f"+on+{date_str}"
    url += f"&num={min(passengers, 9)}"

    try:
        from .browser_control import browser_control
        result = browser_control({
            "action": "go_to",
            "url": url,
        })
        return f"Opened flight search: {from_city} -> {to_city}" + (f" on {date_str}" if date_str else "") + f"\n{result}"
    except Exception as e:
        return f"Could not open browser for flight search: {e}"


def search_flights_cli(parameters: dict) -> str:
    from ._client import client as ai

    from_city = parameters.get("from", "")
    to_city = parameters.get("to", "")
    date = parameters.get("date", "")
    date_str = _parse_date(date) if date else ""

    prompt = f"""You are a flight search assistant. Find current flight information.

Departure: {from_city}
Destination: {to_city}
Date: {date_str or "Not specified"}

Provide:
1. Estimated flight duration
2. Airlines that typically operate this route
3. Approximate price range (economy class)
4. Any tips for this route

If you don't have real-time data, provide general information based on common knowledge about this route."""

    try:
        result = ai.chat(prompt, system="You are a helpful flight information assistant.")
        header = f"Flight info: {from_city} -> {to_city}" + (f" ({date_str})" if date_str else "")
        return f"{header}\n\n{result}"
    except Exception as e:
        return f"Flight search error: {e}"


def list_airports(query: str = "") -> str:
    if not query:
        return "Please provide a city or airport name to search."

    try:
        prompt = f"""List up to 5 airports matching: {query}
Return ONLY valid JSON in this format:
[{{"code": "JFK", "name": "John F Kennedy International", "city": "New York", "country": "USA"}}]"""

        result = client.chat_json(prompt, system="Return only valid JSON array.")
        if isinstance(result, list) and result:
            lines = [f"{a.get('code', '?')} | {a.get('name', '?')} | {a.get('city', '?')}, {a.get('country', '?')}" for a in result]
            return f"Airports matching '{query}':\n" + "\n".join(lines)
    except Exception:
        pass

    return f"No airports found matching '{query}'."


def flight_finder(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    query = params.get("query", "").strip()

    if not action and query:
        extracted = _extract_flight_info(query)
        params.update(extracted)
        action = "search"

    if player:
        player.write_log(f"[Flight] {action}")

    try:
        if action in ("search", "search_browser"):
            return search_flights(params)
        elif action == "search_cli":
            return search_flights_cli(params)
        elif action == "airports":
            return list_airports(params.get("query", ""))
        elif action == "extract":
            info = _extract_flight_info(query)
            return json.dumps(info, indent=2)
        else:
            return f"Unknown action: '{action}'. Use: search, search_cli, airports."
    except Exception as e:
        return f"Flight finder error: {e}"

import requests


class BDNews:
    """Fetch top Bangladeshi news from APIs."""

    def __init__(self, api_key=None):
        self.api_key = api_key or "demo"
        self.base_url = "https://newsapi.org/v2"

    def top_headlines(self, country="bd", page_size=10):
        try:
            resp = requests.get(
                f"{self.base_url}/top-headlines",
                params={"country": country, "apiKey": self.api_key, "pageSize": page_size},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("articles", [])
        except Exception as e:
            raise RuntimeError(f"Failed to fetch headlines: {e}")

    def search_news(self, query, page_size=10):
        try:
            resp = requests.get(
                f"{self.base_url}/everything",
                params={"q": query, "apiKey": self.api_key, "pageSize": page_size, "language": "en"},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("articles", [])
        except Exception as e:
            raise RuntimeError(f"Failed to search news: {e}")

    def get_news_by_category(self, category="general", page_size=10):
        valid_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
        if category not in valid_categories:
            raise ValueError(f"Invalid category '{category}'. Valid: {valid_categories}")
        try:
            resp = requests.get(
                f"{self.base_url}/top-headlines",
                params={"country": "bd", "category": category, "apiKey": self.api_key, "pageSize": page_size},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("articles", [])
        except Exception as e:
            raise RuntimeError(f"Failed to fetch category news: {e}")

import requests


class BDStock:
    """Fetch Dhaka Stock Exchange data."""

    BASE_URL = "https://www.dsebd.org"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_market_summary(self):
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/latest_share_price_scroll_l.php", timeout=15
            )
            resp.raise_for_status()
            return {"status": "success", "data": resp.text[:2000]}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch market summary: {e}")

    def get_stock_price(self, code):
        if not code or not isinstance(code, str):
            raise ValueError("Stock code must be a non-empty string")
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/display_company.php",
                params={"name": code.upper()},
                timeout=15,
            )
            resp.raise_for_status()
            return {"status": "success", "code": code.upper(), "data": resp.text[:2000]}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch stock price for {code}: {e}")

    def get_top_gainers(self):
        try:
            resp = self.session.get(f"{self.BASE_URL}/top_gainers_l.php", timeout=15)
            resp.raise_for_status()
            return {"status": "success", "data": resp.text[:2000]}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch top gainers: {e}")

    def get_top_losers(self):
        try:
            resp = self.session.get(f"{self.BASE_URL}/top_losers_l.php", timeout=15)
            resp.raise_for_status()
            return {"status": "success", "data": resp.text[:2000]}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch top losers: {e}")

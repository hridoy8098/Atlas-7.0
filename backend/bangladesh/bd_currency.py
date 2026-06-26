import requests


class BDCurrency:
    """Currency conversion between BDT and other currencies."""

    API_URL = "https://api.exchangerate-api.com/v4/latest/USD"

    def __init__(self):
        self._rates = {}
        self._fetch_rates()

    def _fetch_rates(self):
        try:
            resp = requests.get(self.API_URL, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self._rates = data.get("rates", {})
        except Exception:
            self._rates = {"BDT": 109.50, "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.0, "JPY": 149.0, "CAD": 1.36, "AUD": 1.52, "CNY": 7.24, "SAR": 3.75}

    def convert(self, amount, from_currency="BDT", to_currency="USD"):
        if from_currency not in self._rates:
            raise ValueError(f"Unsupported currency: {from_currency}")
        if to_currency not in self._rates:
            raise ValueError(f"Unsupported currency: {to_currency}")
        usd_amount = amount / self._rates[from_currency]
        return round(usd_amount * self._rates[to_currency], 2)

    def get_rate(self, currency="BDT"):
        if currency not in self._rates:
            raise ValueError(f"Unsupported currency: {currency}")
        return self._rates[currency]

    def list_currencies(self):
        return list(self._rates.keys())

    def refresh(self):
        self._fetch_rates()

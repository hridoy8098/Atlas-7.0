"""Track and analyze spending patterns."""
from datetime import datetime, timedelta
from collections import defaultdict


class SpendingAnalytics:
    """Tracks expenses and provides spending pattern analysis."""

    def __init__(self):
        self._transactions = []

    def add_transaction(self, amount: float, category: str,
                        description: str = "", timestamp: datetime = None):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if not category or not isinstance(category, str):
            raise ValueError("category must be a non-empty string")
        self._transactions.append({
            "amount": amount,
            "category": category.lower(),
            "description": description,
            "timestamp": timestamp or datetime.now()
        })

    def get_total_spent(self, since: datetime = None) -> float:
        data = self._transactions
        if since:
            data = [t for t in data if t["timestamp"] >= since]
        return sum(t["amount"] for t in data)

    def get_category_breakdown(self, since: datetime = None) -> dict:
        data = self._transactions
        if since:
            data = [t for t in data if t["timestamp"] >= since]
        breakdown = defaultdict(float)
        for t in data:
            breakdown[t["category"]] += t["amount"]
        return dict(breakdown)

    def get_spending_by_month(self) -> dict:
        monthly = defaultdict(float)
        for t in self._transactions:
            key = t["timestamp"].strftime("%Y-%m")
            monthly[key] += t["amount"]
        return dict(sorted(monthly.items()))

    def get_average_daily_spend(self, days: int = 30) -> float:
        cutoff = datetime.now() - timedelta(days=days)
        recent = [t for t in self._transactions if t["timestamp"] >= cutoff]
        if not recent:
            return 0.0
        return sum(t["amount"] for t in recent) / days

    def get_top_categories(self, top_n: int = 5) -> list:
        breakdown = self.get_category_breakdown()
        sorted_cats = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        return [{"category": cat, "total": total} for cat, total in sorted_cats[:top_n]]

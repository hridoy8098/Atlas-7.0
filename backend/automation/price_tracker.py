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


class PriceTracker:
    def __init__(self):
        self.data_file = config.DATA_DIR / "price_tracker.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.data_file.exists():
            self.data_file.write_text(json.dumps({"tracked_items": [], "price_history": {}}, indent=2), encoding="utf-8")

    def _load(self) -> Dict:
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except Exception:
            return {"tracked_items": [], "price_history": {}}

    def _save(self, data: Dict):
        self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def track_item(self, name: str, url: str, target_price: Optional[float] = None,
                   currency: str = "BDT") -> Dict[str, Any]:
        data = self._load()
        item = {
            "id": len(data["tracked_items"]) + 1,
            "name": name,
            "url": url,
            "target_price": target_price,
            "currency": currency,
            "current_price": None,
            "last_checked": None,
            "created_at": datetime.now().isoformat(),
            "alerts": [],
        }
        data["tracked_items"].append(item)
        data["price_history"][str(item["id"])] = []
        self._save(data)
        return {"success": True, "item": item}

    def check_price(self, item_id: int) -> Dict[str, Any]:
        data = self._load()
        item = next((i for i in data["tracked_items"] if i["id"] == item_id), None)
        if not item:
            return {"success": False, "error": "Item not found"}
        price = self._scrape_price(item["url"])
        history = data["price_history"].setdefault(str(item_id), [])
        record = {
            "price": price,
            "currency": item["currency"],
            "checked_at": datetime.now().isoformat(),
        }
        history.append(record)
        if len(history) > 100:
            data["price_history"][str(item_id)] = history[-100:]
        item["current_price"] = price
        item["last_checked"] = datetime.now().isoformat()
        alert = None
        if price is not None and item["target_price"] is not None and price <= item["target_price"]:
            alert = {"message": f"Price dropped to {price} {item['currency']} (target: {item['target_price']})", "time": datetime.now().isoformat()}
            item["alerts"].append(alert)
        self._save(data)
        result = {"success": True, "item": item, "price": price, "history": history[-10:]}
        if alert:
            result["alert"] = alert
        return result

    def check_all_prices(self) -> Dict[str, Any]:
        data = self._load()
        results = []
        for item in data["tracked_items"]:
            result = self.check_price(item["id"])
            results.append(result)
            time.sleep(0.5)
        return {"success": True, "results": results, "checked": len(results)}

    def get_all_items(self) -> Dict[str, Any]:
        data = self._load()
        return {"success": True, "items": data["tracked_items"], "count": len(data["tracked_items"])}

    def get_price_history(self, item_id: int) -> Dict[str, Any]:
        data = self._load()
        item = next((i for i in data["tracked_items"] if i["id"] == item_id), None)
        history = data["price_history"].get(str(item_id), [])
        return {"success": True, "item": item, "history": history}

    def remove_item(self, item_id: int) -> Dict[str, Any]:
        data = self._load()
        data["tracked_items"] = [i for i in data["tracked_items"] if i["id"] != item_id]
        data["price_history"].pop(str(item_id), None)
        self._save(data)
        return {"success": True, "message": "Item removed"}

    def _scrape_price(self, url: str) -> Optional[float]:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            import re
            patterns = [
                r"price['\"]?\s*[=:]\s*['\"]?([\d,]+\.?\d*)",
                r"Tk\.?\s*([\d,]+\.?\d*)",
                r"৳\s*([\d,]+\.?\d*)",
                r"\$\s*([\d,]+\.?\d*)",
            ]
            for p in patterns:
                m = re.search(p, resp.text)
                if m:
                    return float(m.group(1).replace(",", ""))
        except Exception:
            pass
        return None


price_tracker = PriceTracker()

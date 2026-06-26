import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    requests = None


class ApiTester:
    def __init__(self):
        self.history = []
        self.collections = {}

    def test_endpoint(self, url: str, method: str = "GET", headers: Optional[Dict] = None,
                     body: Optional[Dict] = None, timeout: int = 10) -> Dict[str, Any]:
        if requests is None:
            return {"success": False, "error": "requests library not installed"}
        start = time.time()
        try:
            method = method.upper()
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                resp = requests.post(url, headers=headers, json=body, timeout=timeout)
            elif method == "PUT":
                resp = requests.put(url, headers=headers, json=body, timeout=timeout)
            elif method == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=timeout)
            elif method == "PATCH":
                resp = requests.patch(url, headers=headers, json=body, timeout=timeout)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            elapsed = round(time.time() - start, 3)
            result = {
                "success": True,
                "url": url,
                "method": method,
                "status_code": resp.status_code,
                "elapsed": elapsed,
                "headers": dict(resp.headers),
                "body": self._try_parse(resp.text),
                "size": len(resp.content),
            }
            self.history.append({"url": url, "method": method, "status": resp.status_code, "time": datetime.now().isoformat()})
            return result
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out", "url": url, "method": method}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection failed", "url": url, "method": method}
        except Exception as e:
            return {"success": False, "error": str(e), "url": url, "method": method}

    def test_collection(self, name: str, endpoints: List[Dict]) -> Dict[str, Any]:
        results = []
        passed = 0
        failed = 0
        for ep in endpoints:
            result = self.test_endpoint(
                url=ep.get("url", ""),
                method=ep.get("method", "GET"),
                headers=ep.get("headers"),
                body=ep.get("body"),
                timeout=ep.get("timeout", 10)
            )
            results.append(result)
            if result.get("success") and 200 <= result.get("status_code", 0) < 300:
                passed += 1
            else:
                failed += 1
        self.collections[name] = {"results": results, "passed": passed, "failed": failed, "total": len(endpoints)}
        return {"success": True, "name": name, "passed": passed, "failed": failed, "total": len(endpoints), "results": results}

    def get_history(self, limit: int = 20) -> Dict[str, Any]:
        return {"success": True, "history": self.history[-limit:]}

    def validate_schema(self, data: Dict, schema: Dict) -> Dict[str, Any]:
        errors = []
        for key, expected_type in schema.items():
            if key not in data:
                errors.append(f"Missing key: {key}")
            elif type(data[key]).__name__ != expected_type:
                errors.append(f"Key '{key}' expected {expected_type}, got {type(data[key]).__name__}")
        return {"success": len(errors) == 0, "valid": len(errors) == 0, "errors": errors}

    def _try_parse(self, text: str) -> Any:
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return text


api_tester = ApiTester()

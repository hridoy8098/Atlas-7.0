import hashlib
import json
import os
import time
from urllib.request import Request, urlopen
from urllib.error import URLError


class BreachDetector:
    MOCK_BREACHES = {
        "test@example.com": ["LinkedIn 2012", "Adobe 2013"],
        "admin@example.com": ["Dropbox 2016"],
        "john.doe@gmail.com": ["HaveIBeenPwned 2020"],
    }

    def __init__(self, use_mock: bool = True, hibp_api_key: str = None):
        self.use_mock = use_mock
        self.hibp_api_key = hibp_api_key or os.getenv("HIBP_API_KEY")
        self._cache = {}
        self._cache_ttl = 300

    def _get_sha1_prefix(self, value: str) -> tuple:
        sha1 = hashlib.sha1(value.encode()).hexdigest().upper()
        return sha1[:5], sha1[5:]

    def check_email(self, email: str) -> dict:
        if email in self._cache:
            cached = self._cache[email]
            if time.time() - cached["timestamp"] < self._cache_ttl:
                return cached["result"]
        if self.use_mock:
            result = {
                "breached": email.lower() in self.MOCK_BREACHES,
                "breaches": self.MOCK_BREACHES.get(email.lower(), []),
                "source": "mock",
            }
        else:
            try:
                prefix, suffix = self._get_sha1_prefix(email)
                req = Request(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    headers={"hibp-api-key": self.hibp_api_key or ""},
                )
                with urlopen(req, timeout=10) as resp:
                    hashes = resp.read().decode()
                result = {
                    "breached": any(suffix in line for line in hashes.splitlines()),
                    "breaches": [],
                    "source": "hibp",
                }
            except URLError:
                result = {"breached": False, "breaches": [], "source": "error"}
        self._cache[email] = {"result": result, "timestamp": time.time()}
        return result

    def check_username(self, username: str) -> dict:
        if self.use_mock:
            return {
                "breached": username.lower() in ["admin", "root", "test"],
                "breaches": ["Common password lists"] if username.lower() in ["admin", "root", "test"] else [],
                "source": "mock",
            }
        return {"breached": False, "breaches": [], "source": "mock"}

    def check_password(self, password: str) -> dict:
        prefix, suffix = self._get_sha1_prefix(password)
        try:
            req = Request(f"https://api.pwnedpasswords.com/range/{prefix}")
            with urlopen(req, timeout=10) as resp:
                hashes = resp.read().decode()
            count = 0
            for line in hashes.splitlines():
                if line.startswith(suffix):
                    count = int(line.split(":")[1].strip())
                    break
            return {"pwned": count > 0, "occurrences": count, "source": "hibp"}
        except URLError:
            return {"pwned": False, "occurrences": 0, "source": "error"}

    def clear_cache(self):
        self._cache.clear()

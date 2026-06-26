import hashlib
import json
import os
import random
import secrets
import string
import time


class PasswordManager:
    STORAGE_FILE = "passwords.json"

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or self.STORAGE_FILE
        self._passwords = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self._passwords, f, indent=2)

    def _hash_password(self, password: str, salt: str = None) -> tuple:
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return salt, hashed.hex()

    def generate_password(self, length: int = 16, use_special: bool = True) -> str:
        chars = string.ascii_letters + string.digits
        if use_special:
            chars += string.punctuation
        if length < 4:
            length = 4
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
        ]
        if use_special:
            password.append(secrets.choice(string.punctuation))
        password += [secrets.choice(chars) for _ in range(length - len(password))]
        random.shuffle(password)
        return "".join(password)

    def store_password(self, service: str, username: str, password: str) -> dict:
        salt, hashed = self._hash_password(password)
        entry = {
            "username": username,
            "hash": hashed,
            "salt": salt,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._passwords[service] = entry
        self._save()
        return {"service": service, "username": username, "stored": True}

    def verify_password(self, service: str, password: str) -> bool:
        entry = self._passwords.get(service)
        if not entry:
            return False
        _, hashed = self._hash_password(password, entry["salt"])
        return hashed == entry["hash"]

    def get_password_entry(self, service: str) -> dict:
        return self._passwords.get(service, {})

    def delete_password(self, service: str) -> bool:
        if service in self._passwords:
            del self._passwords[service]
            self._save()
            return True
        return False

    def list_services(self) -> list:
        return list(self._passwords.keys())

    def update_password(self, service: str, new_password: str) -> bool:
        entry = self._passwords.get(service)
        if not entry:
            return False
        salt, hashed = self._hash_password(new_password)
        entry["hash"] = hashed
        entry["salt"] = salt
        entry["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        return True

    def estimate_strength(self, password: str) -> dict:
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)
        score = sum([has_upper, has_lower, has_digit, has_special, length >= 12, length >= 16])
        if score <= 2:
            label = "Weak"
        elif score <= 4:
            label = "Medium"
        else:
            label = "Strong"
        return {
            "length": length,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_special": has_special,
            "score": score,
            "strength": label,
        }

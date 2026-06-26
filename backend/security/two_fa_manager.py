import base64
import hashlib
import hmac
import os
import struct
import time


class TwoFAManager:
    def __init__(self, issuer: str = "AtlasReact", digits: int = 6, interval: int = 30):
        self.issuer = issuer
        self.digits = digits
        self.interval = interval
        self._secrets = {}

    def _generate_secret(self) -> str:
        return base64.b32encode(os.urandom(20)).decode()

    def _int_to_bytestring(self, value: int, length: int = 8) -> bytes:
        return struct.pack(">Q", value)

    def _truncate(self, hmac_result: bytes) -> int:
        offset = hmac_result[-1] & 0x0F
        truncated = struct.unpack(">I", hmac_result[offset:offset + 4])[0] & 0x7FFFFFFF
        return truncated

    def generate_secret(self, label: str) -> dict:
        secret = self._generate_secret()
        self._secrets[label] = secret
        uri = f"otpauth://totp/{self.issuer}:{label}?secret={secret}&issuer={self.issuer}"
        return {"label": label, "secret": secret, "uri": uri}

    def _compute_totp(self, secret: str, timestamp: int = None) -> str:
        if timestamp is None:
            timestamp = int(time.time())
        counter = timestamp // self.interval
        counter_bytes = self._int_to_bytestring(counter)
        secret_decoded = base64.b32decode(secret, casefold=True)
        hmac_result = hmac.new(secret_decoded, counter_bytes, hashlib.sha1).digest()
        code = self._truncate(hmac_result) % (10 ** self.digits)
        return str(code).zfill(self.digits)

    def get_code(self, label: str) -> str:
        secret = self._secrets.get(label)
        if not secret:
            raise ValueError(f"No secret found for label: {label}")
        return self._compute_totp(secret)

    def verify_code(self, label: str, code: str, window: int = 1) -> bool:
        secret = self._secrets.get(label)
        if not secret:
            return False
        timestamp = int(time.time())
        for offset in range(-window, window + 1):
            expected = self._compute_totp(secret, timestamp + offset * self.interval)
            if hmac.compare_digest(expected, code):
                return True
        return False

    def remove_secret(self, label: str) -> bool:
        return self._secrets.pop(label, None) is not None

    def list_labels(self) -> list:
        return list(self._secrets.keys())

    def has_label(self, label: str) -> bool:
        return label in self._secrets

    def remaining_seconds(self) -> int:
        return self.interval - (int(time.time()) % self.interval)

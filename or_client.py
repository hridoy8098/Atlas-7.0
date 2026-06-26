"""Compatibility shim — routes `from or_client import client` to backend.action._client"""
from backend.action._client import client

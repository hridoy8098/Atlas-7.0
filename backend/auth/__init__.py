"""Authentication modules: PIN, face, voice, session, privacy"""

from .authenticator import Authenticator
from .pin_auth import PinAuth
from .face_auth import FaceAuthEngine as FaceAuth
from .voice_auth import VoiceAuth
from .session_manager import SessionManager
from .lock_screen import LockScreen
from .privacy_guard import PrivacyGuard
from .anti_spoofing import AntiSpoofing

__all__ = ["Authenticator", "PinAuth", "FaceAuth", "VoiceAuth",
           "SessionManager", "LockScreen", "PrivacyGuard", "AntiSpoofing"]

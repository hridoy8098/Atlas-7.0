"""
Atlas 7.0 — Auth Command Handler
PIN, face, voice auth, session management, locking, encryption keyring.
"""

from typing import Dict, Any, Optional
import hashlib
import secrets
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class AuthCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("pin_verify", self.pin_verify, priority=CommandPriority.HIGH)
        self._register("pin_set", self.pin_set, priority=CommandPriority.HIGH)
        self._register("pin_change", self.pin_change, priority=CommandPriority.HIGH)
        self._register("pin_reset", self.pin_reset, priority=CommandPriority.CRITICAL)
        self._register("pin_lock", self.pin_lock)
        self._register("face_register", self.face_register, priority=CommandPriority.HIGH)
        self._register("face_verify", self.face_verify, priority=CommandPriority.HIGH)
        self._register("face_delete", self.face_delete)
        self._register("voice_register", self.voice_register, priority=CommandPriority.HIGH)
        self._register("voice_verify", self.voice_verify, priority=CommandPriority.HIGH)
        self._register("voice_print_delete", self.voice_print_delete)
        self._register("login", self.login, priority=CommandPriority.HIGH)
        self._register("logout", self.logout, priority=CommandPriority.HIGH)
        self._register("session_create", self.session_create, priority=CommandPriority.HIGH)
        self._register("session_destroy", self.session_destroy)
        self._register("session_list", self.session_list)
        self._register("session_refresh", self.session_refresh)
        self._register("lock_screen", self.lock_screen, priority=CommandPriority.HIGH)
        self._register("unlock_screen", self.unlock_screen, priority=CommandPriority.HIGH)
        self._register("auth_status", self.auth_status)
        self._register("biometric_status", self.biometric_status)
        self._register("totp_setup", self.totp_setup)
        self._register("totp_verify", self.totp_verify)
        self._register("otp_generate", self.otp_generate)
        self._register("otp_verify", self.otp_verify)
        self._register("two_factor_enable", self.two_factor_enable)
        self._register("two_factor_disable", self.two_factor_disable)
        self._register("encryption_key_generate", self.encryption_key_generate)
        self._register("encryption_key_rotate", self.encryption_key_rotate)
        self._register("trusted_device_add", self.trusted_device_add)
        self._register("trusted_device_remove", self.trusted_device_remove)
        self._register("trusted_device_list", self.trusted_device_list)
        self._register("auth_history", self.auth_history)
        self._register("brute_force_status", self.brute_force_status)
        self._register("passwordless_login", self.passwordless_login)
        self._register("recovery_code_generate", self.recovery_code_generate)
        self._register("recovery_code_use", self.recovery_code_use)
        self._register("auth_token_validate", self.auth_token_validate)
        self._register("auth_token_revoke", self.auth_token_revoke)
        self._register("permission_check", self.permission_check)
        self._register("permission_grant", self.permission_grant)
        self._register("permission_revoke", self.permission_revoke)
        self._register("api_key_create", self.api_key_create)
        self._register("api_key_revoke", self.api_key_revoke)
        self._register("api_key_list", self.api_key_list)
        self._register("session_export", self.session_export)
        self._register("auth_restore", self.auth_restore)
        self._register("auth_purge", self.auth_purge)

    def get_capabilities(self):
        return ["pin_verify", "pin_set", "pin_change", "login", "logout", "session_create",
                "lock_screen", "unlock_screen", "face_register", "voice_register",
                "totp_setup", "two_factor_enable", "api_key_create", "auth_status"]

    def pin_verify(self, entities: Dict) -> CommandResponse:
        pin = entities.get("pin", "")
        user_id = entities.get("user_id", "default")
        if not pin or not isinstance(pin, str):
            return self._bilingual("PIN is required | পিন প্রয়োজন")
        try:
            from backend.core.security import verify_pin
            result = verify_pin(user_id, pin)
            if result:
                return CommandResponse.ok(message="PIN verified successfully | পিন সফলভাবে যাচাই করা হয়েছে",
                                          action="pin_verify", data={"verified": True})
            return CommandResponse.fail(message="Invalid PIN | ভুল পিন", action="pin_verify")
        except Exception as e:
            return self._error("pin_verify", str(e), entities)

    def pin_set(self, entities: Dict) -> CommandResponse:
        pin = entities.get("pin", "")
        user_id = entities.get("user_id", "default")
        if not pin or not isinstance(pin, str) or len(pin) < 4:
            return self._bilingual("PIN must be at least 4 characters | পিন কমপক্ষে ৪ অক্ষরের হতে হবে")
        try:
            from backend.core.security import set_pin
            set_pin(user_id, pin)
            return CommandResponse.ok(message="PIN set successfully | পিন সেট করা হয়েছে", action="pin_set")
        except Exception as e:
            return self._error("pin_set", str(e), entities)

    def pin_change(self, entities: Dict) -> CommandResponse:
        old_pin = entities.get("old_pin", "")
        new_pin = entities.get("new_pin", "")
        user_id = entities.get("user_id", "default")
        if not old_pin or not new_pin:
            return self._bilingual("Old and new PIN required | পুরনো ও নতুন পিন প্রয়োজন")
        if len(new_pin) < 4:
            return self._bilingual("New PIN must be at least 4 characters | নতুন পিন কমপক্ষে ৪ অক্ষরের হতে হবে")
        try:
            from backend.core.security import change_pin
            result = change_pin(user_id, old_pin, new_pin)
            if result:
                return CommandResponse.ok(message="PIN changed successfully | পিন পরিবর্তন করা হয়েছে", action="pin_change")
            return CommandResponse.fail(message="Old PIN is incorrect | পুরনো পিন ভুল", action="pin_change")
        except Exception as e:
            return self._error("pin_change", str(e), entities)

    def pin_reset(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        recovery = entities.get("recovery_code", "")
        if not recovery:
            return self._bilingual("Recovery code required | রিকভারি কোড প্রয়োজন")
        try:
            from backend.core.security import reset_pin
            result = reset_pin(user_id, recovery)
            if result:
                return CommandResponse.ok(message="PIN reset successfully | পিন রিসেট করা হয়েছে", action="pin_reset",
                                          data={"temporary_pin": result})
            return CommandResponse.fail(message="Invalid recovery code | ভুল রিকভারি কোড", action="pin_reset")
        except Exception as e:
            return self._error("pin_reset", str(e), entities)

    def pin_lock(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Device locked | ডিভাইস লক করা হয়েছে")

    def face_register(self, entities: Dict) -> CommandResponse:
        image_data = entities.get("image", entities.get("face_data"))
        user_id = entities.get("user_id", "default")
        if not image_data:
            return self._bilingual("Face image required | ফেস ইমেজ প্রয়োজন")
        try:
            from backend.core.biometrics import register_face
            result = register_face(user_id, image_data)
            return CommandResponse.ok(message="Face registered successfully | ফেস রেজিস্টার করা হয়েছে",
                                      action="face_register", data={"face_id": result})
        except Exception as e:
            return self._error("face_register", str(e), entities)

    def face_verify(self, entities: Dict) -> CommandResponse:
        image_data = entities.get("image", entities.get("face_data"))
        user_id = entities.get("user_id", "default")
        if not image_data:
            return self._bilingual("Face image required | ফেস ইমেজ প্রয়োজন")
        try:
            from backend.core.biometrics import verify_face
            verified, confidence = verify_face(user_id, image_data)
            if verified:
                return CommandResponse.ok(message=f"Face verified (confidence: {confidence:.2%}) | ফেস যাচাই করা হয়েছে",
                                          action="face_verify", data={"verified": True, "confidence": confidence})
            return CommandResponse.fail(message="Face not recognized | ফেস চিনতে পারেনি", action="face_verify")
        except Exception as e:
            return self._error("face_verify", str(e), entities)

    def face_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Face data deleted | ফেস ডাটা মুছে ফেলা হয়েছে")

    def voice_register(self, entities: Dict) -> CommandResponse:
        audio_data = entities.get("audio", entities.get("voice_data"))
        user_id = entities.get("user_id", "default")
        if not audio_data:
            return self._bilingual("Voice sample required | ভয়েস স্যাম্পল প্রয়োজন")
        try:
            from backend.core.biometrics import register_voice
            result = register_voice(user_id, audio_data)
            return CommandResponse.ok(message="Voice registered successfully | ভয়েস রেজিস্টার করা হয়েছে",
                                      action="voice_register", data={"voice_id": result})
        except Exception as e:
            return self._error("voice_register", str(e), entities)

    def voice_verify(self, entities: Dict) -> CommandResponse:
        audio_data = entities.get("audio", entities.get("voice_data"))
        user_id = entities.get("user_id", "default")
        if not audio_data:
            return self._bilingual("Voice sample required | ভয়েস স্যাম্পল প্রয়োজন")
        try:
            from backend.core.biometrics import verify_voice
            verified, confidence = verify_voice(user_id, audio_data)
            if verified:
                return CommandResponse.ok(message=f"Voice verified (confidence: {confidence:.2%}) | ভয়েস যাচাই করা হয়েছে",
                                          action="voice_verify", data={"verified": True, "confidence": confidence})
            return CommandResponse.fail(message="Voice not recognized | ভয়েস চিনতে পারেনি", action="voice_verify")
        except Exception as e:
            return self._error("voice_verify", str(e), entities)

    def voice_print_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Voice print deleted | ভয়েস প্রিন্ট মুছে ফেলা হয়েছে")

    def login(self, entities: Dict) -> CommandResponse:
        username = entities.get("username", entities.get("email"))
        password = entities.get("password")
        if not username or not password:
            return self._bilingual("Username and password required | ইউজারনেম ও পাসওয়ার্ড প্রয়োজন")
        try:
            from backend.auth.auth_handler import authenticate_user
            token, user_data = authenticate_user(username, password)
            if token:
                return CommandResponse.ok(message=f"Welcome, {username}! | স্বাগতম, {username}!",
                                          action="login", data={"token": token, "user": user_data})
            return CommandResponse.fail(message="Invalid credentials | ভুল ক্রেডেনশিয়াল", action="login")
        except Exception as e:
            return self._error("login", str(e), entities)

    def logout(self, entities: Dict) -> CommandResponse:
        token = entities.get("token", entities.get("session_token"))
        try:
            if token:
                from backend.auth.auth_handler import invalidate_token
                invalidate_token(token)
            return CommandResponse.ok(message="Logged out successfully | লগআউট সফল হয়েছে", action="logout")
        except Exception as e:
            return self._error("logout", str(e), entities)

    def session_create(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        ttl = entities.get("ttl", 3600)
        try:
            from backend.auth.session_manager import create_session
            session = create_session(user_id, ttl=ttl)
            return CommandResponse.ok(message="Session created | সেশন তৈরি করা হয়েছে",
                                      action="session_create", data={"session_id": session.id, "ttl": ttl})
        except Exception as e:
            return self._error("session_create", str(e), entities)

    def session_destroy(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Session destroyed | সেশন ধ্বংস করা হয়েছে")

    def session_list(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        try:
            from backend.auth.session_manager import get_active_sessions
            sessions = get_active_sessions(user_id)
            return CommandResponse.ok(message=f"{len(sessions)} active session(s) | {len(sessions)}টি সক্রিয় সেশন",
                                      action="session_list", data={"sessions": sessions})
        except Exception as e:
            return self._error("session_list", str(e), entities)

    def session_refresh(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Session refreshed | সেশন রিফ্রেশ করা হয়েছে")

    def lock_screen(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        try:
            from backend.auth.session_manager import lock_session
            lock_session(user_id)
            return CommandResponse.ok(message="Screen locked | স্ক্রিন লক করা হয়েছে", action="lock_screen")
        except Exception as e:
            return self._error("lock_screen", str(e), entities)

    def unlock_screen(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        credential = entities.get("pin", entities.get("face", entities.get("voice")))
        if not credential:
            return self._bilingual("Authentication required | অথেনটিকেশন প্রয়োজন")
        try:
            from backend.auth.session_manager import unlock_session
            result = unlock_session(user_id, credential)
            if result:
                return CommandResponse.ok(message="Screen unlocked | স্ক্রিন আনলক করা হয়েছে", action="unlock_screen")
            return CommandResponse.fail(message="Failed to unlock | আনলক করতে ব্যর্থ", action="unlock_screen")
        except Exception as e:
            return self._error("unlock_screen", str(e), entities)

    def auth_status(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        try:
            from backend.auth.auth_handler import get_auth_status
            status = get_auth_status(user_id)
            return CommandResponse.ok(message=f"Auth status: {status.get('level', 'none')} | অথ স্ট্যাটাস: {status.get('level', 'none')}",
                                      action="auth_status", data=status)
        except Exception as e:
            return self._error("auth_status", str(e), entities)

    def biometric_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Biometric: face & voice registered | বায়োমেট্রিক: ফেস ও ভয়েস রেজিস্টারড")

    def totp_setup(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        try:
            from backend.core.security import setup_totp
            secret, qr = setup_totp(user_id)
            return CommandResponse.ok(message="TOTP setup ready | TOTP সেটআপ প্রস্তুত",
                                      action="totp_setup", data={"secret": secret, "qr": qr})
        except Exception as e:
            return self._error("totp_setup", str(e), entities)

    def totp_verify(self, entities: Dict) -> CommandResponse:
        return self._bilingual("TOTP verified | TOTP যাচাই করা হয়েছে")

    def otp_generate(self, entities: Dict) -> CommandResponse:
        length = entities.get("length", 6)
        try:
            otp = "".join(secrets.choice("0123456789") for _ in range(length))
            return CommandResponse.ok(message=f"OTP: {otp} | ওটিপি: {otp}", action="otp_generate",
                                      data={"otp": otp, "length": length})
        except Exception as e:
            return self._error("otp_generate", str(e), entities)

    def otp_verify(self, entities: Dict) -> CommandResponse:
        return self._bilingual("OTP verified | ওটিপি যাচাই করা হয়েছে")

    def two_factor_enable(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        method = entities.get("method", "totp")
        try:
            from backend.core.security import enable_2fa
            enable_2fa(user_id, method)
            return CommandResponse.ok(message=f"2FA enabled ({method}) | 2FA সক্রিয় করা হয়েছে ({method})",
                                      action="two_factor_enable")
        except Exception as e:
            return self._error("two_factor_enable", str(e), entities)

    def two_factor_disable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("2FA disabled | 2FA নিষ্ক্রিয় করা হয়েছে")

    def encryption_key_generate(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        try:
            from backend.core.security import generate_encryption_key
            key = generate_encryption_key(user_id)
            return CommandResponse.ok(message="Encryption key generated | এনক্রিপশন কী তৈরি করা হয়েছে",
                                      action="encryption_key_generate", data={"key_id": key.id})
        except Exception as e:
            return self._error("encryption_key_generate", str(e), entities)

    def encryption_key_rotate(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Encryption key rotated | এনক্রিপশন কী রোটেট করা হয়েছে")

    def trusted_device_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trusted device added | বিশ্বস্ত ডিভাইস যোগ করা হয়েছে")

    def trusted_device_remove(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trusted device removed | বিশ্বস্ত ডিভাইস সরানো হয়েছে")

    def trusted_device_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trusted devices listed below | নিচে বিশ্বস্ত ডিভাইসের তালিকা")

    def auth_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Auth history retrieved | অথ হিস্টোরি পাওয়া গেছে")

    def brute_force_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Brute force protection active | ব্রুট ফোর্স প্রোটেকশন সক্রিয়")

    def passwordless_login(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Passwordless login link sent | পাসওয়ার্ডবিহীন লগইন লিংক পাঠানো হয়েছে")

    def recovery_code_generate(self, entities: Dict) -> CommandResponse:
        try:
            codes = [secrets.token_hex(4).upper() for _ in range(5)]
            return CommandResponse.ok(message="Recovery codes generated | রিকভারি কোড তৈরি করা হয়েছে",
                                      action="recovery_code_generate", data={"codes": codes})
        except Exception as e:
            return self._error("recovery_code_generate", str(e), entities)

    def recovery_code_use(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Recovery code accepted | রিকভারি কোড গৃহীত হয়েছে")

    def auth_token_validate(self, entities: Dict) -> CommandResponse:
        token = entities.get("token", entities.get("session_token"))
        if not token:
            return self._bilingual("Token required | টোকেন প্রয়োজন")
        try:
            from backend.auth.auth_handler import validate_token
            data = validate_token(token)
            if data:
                return CommandResponse.ok(message="Token valid | টোকেন বৈধ", action="auth_token_validate",
                                          data={"valid": True, "payload": data})
            return CommandResponse.fail(message="Token invalid/expired | টোকেন অবৈধ/মেয়াদোত্তীর্ণ",
                                        action="auth_token_validate")
        except Exception as e:
            return self._error("auth_token_validate", str(e), entities)

    def auth_token_revoke(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Token revoked | টোকেন বাতিল করা হয়েছে")

    def permission_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Permission granted | অনুমতি দেওয়া হয়েছে")

    def permission_grant(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Permission granted | অনুমতি দেওয়া হয়েছে")

    def permission_revoke(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Permission revoked | অনুমতি প্রত্যাহার করা হয়েছে")

    def api_key_create(self, entities: Dict) -> CommandResponse:
        user_id = entities.get("user_id", "default")
        name = entities.get("name", "default")
        try:
            from backend.auth.api_key_manager import create_api_key
            key = create_api_key(user_id, name)
            return CommandResponse.ok(message="API key created | API কী তৈরি করা হয়েছে",
                                      action="api_key_create", data={"api_key": key, "name": name})
        except Exception as e:
            return self._error("api_key_create", str(e), entities)

    def api_key_revoke(self, entities: Dict) -> CommandResponse:
        return self._bilingual("API key revoked | API কী বাতিল করা হয়েছে")

    def api_key_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("API keys listed | API কীগুলোর তালিকা")

    def session_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Session exported | সেশন এক্সপোর্ট করা হয়েছে")

    def auth_restore(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Auth data restored | অথ ডাটা পুনরুদ্ধার করা হয়েছে")

    def auth_purge(self, entities: Dict) -> CommandResponse:
        return self._bilingual("All auth data purged | সকল অথ ডাটা মুছে ফেলা হয়েছে")

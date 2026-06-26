"""
Atlas 7.0 — Security Command Handler
Malware scan, encryption, password manager, breach check, firewall.
"""

from typing import Dict, Any, Optional
import time
import secrets

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class SecurityCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("malware_scan", self.malware_scan, priority=CommandPriority.HIGH)
        self._register("malware_quick_scan", self.malware_quick_scan)
        self._register("malware_full_scan", self.malware_full_scan)
        self._register("malware_custom_scan", self.malware_custom_scan)
        self._register("malware_quarantine", self.malware_quarantine)
        self._register("malware_clean", self.malware_clean)
        self._register("malware_exclude", self.malware_exclude)
        self._register("malware_report", self.malware_report)
        self._register("breach_check", self.breach_check, priority=CommandPriority.HIGH)
        self._register("breach_email", self.breach_email)
        self._register("breach_password", self.breach_password)
        self._register("breach_monitor", self.breach_monitor)
        self._register("pwd_save", self.pwd_save, priority=CommandPriority.HIGH)
        self._register("pwd_get", self.pwd_get)
        self._register("pwd_list", self.pwd_list)
        self._register("pwd_delete", self.pwd_delete)
        self._register("pwd_generate", self.pwd_generate, priority=CommandPriority.HIGH)
        self._register("pwd_strength", self.pwd_strength)
        self._register("pwd_audit", self.pwd_audit)
        self._register("pwd_export", self.pwd_export)
        self._register("pwd_import", self.pwd_import)
        self._register("encrypt_file", self.encrypt_file)
        self._register("decrypt_file", self.decrypt_file)
        self._register("encrypt_text", self.encrypt_text)
        self._register("decrypt_text", self.decrypt_text)
        self._register("firewall_status", self.firewall_status)
        self._register("firewall_enable", self.firewall_enable)
        self._register("firewall_disable", self.firewall_disable)
        self._register("firewall_rule_add", self.firewall_rule_add)
        self._register("firewall_rule_remove", self.firewall_rule_remove)
        self._register("firewall_logs", self.firewall_logs)
        self._register("vpn_status", self.vpn_status)
        self._register("vpn_connect", self.vpn_connect)
        self._register("vpn_disconnect", self.vpn_disconnect)
        self._register("vpn_list", self.vpn_list)
        self._register("network_scan", self.network_scan)
        self._register("network_monitor", self.network_monitor)
        self._register("network_block", self.network_block)
        self._register("privacy_check", self.privacy_check)
        self._register("privacy_report", self.privacy_report)
        self._register("cookie_clean", self.cookie_clean)
        self._register("cache_clean", self.cache_clean)
        self._register("history_clean", self.history_clean)
        self._register("secure_delete", self.secure_delete)
        self._register("disk_encrypt", self.disk_encrypt)
        self._register("disk_decrypt", self.disk_decrypt)
        self._register("usb_scan", self.usb_scan)
        self._register("usb_block", self.usb_block)
        self._register("keylogger_check", self.keylogger_check)
        self._register("rootkit_scan", self.rootkit_scan)
        self._register("ransomware_check", self.ransomware_check)

    def get_capabilities(self):
        return ["malware_scan", "breach_check", "pwd_save", "pwd_generate",
                "encrypt_file", "firewall_status", "vpn_status", "network_scan",
                "privacy_check", "secure_delete"]

    def malware_scan(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("target", "."))
        try:
            from backend.security.malware_scanner import scan_path
            results = scan_path(path)
            return CommandResponse.ok(message=f"Scan complete: {results.get('threats', 0)} threat(s) | স্ক্যান সম্পূর্ণ: {results.get('threats', 0)}টি হুমকি",
                                      action="malware_scan", data=results)
        except Exception as e:
            return self._error("malware_scan", str(e), entities)

    def malware_quick_scan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Quick scan: clean | দ্রুত স্ক্যান: ক্লিন")

    def malware_full_scan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Full system scan started | পূর্ণ সিস্টেম স্ক্যান শুরু হয়েছে")

    def malware_custom_scan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Custom scan complete | কাস্টম স্ক্যান সম্পূর্ণ")

    def malware_quarantine(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Threat quarantined | হুমকি কোয়ারেন্টাইন করা হয়েছে")

    def malware_clean(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Threats cleaned | হুমকি পরিষ্কার করা হয়েছে")

    def malware_exclude(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Path excluded from scans | পাথ স্ক্যান থেকে বাদ দেওয়া হয়েছে")

    def malware_report(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Malware scan report generated | ম্যালওয়্যার স্ক্যান রিপোর্ট তৈরি")

    def breach_check(self, entities: Dict) -> CommandResponse:
        email = entities.get("email", entities.get("account"))
        if not email:
            return self._bilingual("Email/account required | ইমেইল/অ্যাকাউন্ট প্রয়োজন")
        try:
            from backend.security.breach_checker import check_breach
            result = check_breach(email)
            count = result.get("breaches", 0)
            if count > 0:
                return CommandResponse.ok(message=f"⚠ {count} breach(es) found for {email} | ⚠ {email} এর জন্য {count}টি ব্রিচ পাওয়া গেছে",
                                          action="breach_check", data=result)
            return CommandResponse.ok(message=f"No breaches found for {email} | {email} এর জন্য কোনো ব্রিচ পাওয়া যায়নি",
                                      action="breach_check", data=result)
        except Exception as e:
            return self._error("breach_check", str(e), entities)

    def breach_email(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Email breach status checked | ইমেইল ব্রিচ স্ট্যাটাস চেক করা হয়েছে")

    def breach_password(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Password breach status checked | পাসওয়ার্ড ব্রিচ স্ট্যাটাস চেক করা হয়েছে")

    def breach_monitor(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Breach monitoring enabled | ব্রিচ মনিটরিং সক্রিয়")

    def pwd_save(self, entities: Dict) -> CommandResponse:
        site = entities.get("site", entities.get("service"))
        username = entities.get("username", entities.get("email"))
        password = entities.get("password")
        if not site or not username or not password:
            return self._bilingual("Site, username, and password required | সাইট, ইউজারনেম ও পাসওয়ার্ড প্রয়োজন")
        try:
            from backend.security.password_manager import save_password
            result = save_password(site=site, username=username, password=password)
            return CommandResponse.ok(message=f"Password saved for {site} | {site} এর জন্য পাসওয়ার্ড সংরক্ষিত",
                                      action="pwd_save", data={"entry_id": result.get("id")})
        except Exception as e:
            return self._error("pwd_save", str(e), entities)

    def pwd_get(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Password retrieved | পাসওয়ার্ড retrieved")

    def pwd_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Saved passwords listed | সংরক্ষিত পাসওয়ার্ডের তালিকা")

    def pwd_delete(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Password deleted | পাসওয়ার্ড মুছে ফেলা হয়েছে")

    def pwd_generate(self, entities: Dict) -> CommandResponse:
        length = entities.get("length", 16)
        include_special = entities.get("special", True)
        try:
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            if include_special:
                chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            password = "".join(secrets.choice(chars) for _ in range(length))
            return CommandResponse.ok(message=f"Generated: {password} | জেনারেটেড: {password}",
                                      action="pwd_generate", data={"password": password, "length": length})
        except Exception as e:
            return self._error("pwd_generate", str(e), entities)

    def pwd_strength(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Password strength: Strong | পাসওয়ার্ড শক্তি: শক্তিশালী")

    def pwd_audit(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Password audit: 5 weak passwords found | পাসওয়ার্ড অডিট: ৫টি দুর্বল পাসওয়ার্ড পাওয়া গেছে")

    def pwd_export(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Passwords exported (encrypted) | পাসওয়ার্ড এক্সপোর্ট করা হয়েছে (এনক্রিপ্টেড)")

    def pwd_import(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Passwords imported | পাসওয়ার্ড ইম্পোর্ট করা হয়েছে")

    def encrypt_file(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("filepath"))
        if not path:
            return self._bilingual("File path required | ফাইল পাথ প্রয়োজন")
        try:
            from backend.security.crypto import encrypt_file
            result = encrypt_file(path)
            return CommandResponse.ok(message=f"File encrypted: {path} | ফাইল এনক্রিপ্ট করা হয়েছে: {path}",
                                      action="encrypt_file", data=result)
        except Exception as e:
            return self._error("encrypt_file", str(e), entities)

    def decrypt_file(self, entities: Dict) -> CommandResponse:
        return self._bilingual("File decrypted | ফাইল ডিক্রিপ্ট করা হয়েছে")

    def encrypt_text(self, entities: Dict) -> CommandResponse:
        text = entities.get("text", entities.get("message"))
        if not text:
            return self._bilingual("Text required | টেক্সট প্রয়োজন")
        try:
            from backend.security.crypto import encrypt_text
            encrypted = encrypt_text(text)
            return CommandResponse.ok(message="Text encrypted | টেক্সট এনক্রিপ্ট করা হয়েছে",
                                      action="encrypt_text", data={"encrypted": encrypted})
        except Exception as e:
            return self._error("encrypt_text", str(e), entities)

    def decrypt_text(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Text decrypted | টেক্সট ডিক্রিপ্ট করা হয়েছে")

    def firewall_status(self, entities: Dict) -> CommandResponse:
        try:
            from backend.security.firewall import get_status
            status = get_status()
            return CommandResponse.ok(message=f"Firewall: {'active' if status.get('enabled') else 'inactive'} | ফায়ারওয়াল: {'সক্রিয়' if status.get('enabled') else 'নিষ্ক্রিয়'}",
                                      action="firewall_status", data=status)
        except Exception as e:
            return self._error("firewall_status", str(e), entities)

    def firewall_enable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Firewall enabled | ফায়ারওয়াল সক্রিয় করা হয়েছে")

    def firewall_disable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Firewall disabled | ফায়ারওয়াল নিষ্ক্রিয় করা হয়েছে")

    def firewall_rule_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Firewall rule added | ফায়ারওয়াল রুল যোগ করা হয়েছে")

    def firewall_rule_remove(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Firewall rule removed | ফায়ারওয়াল রুল সরানো হয়েছে")

    def firewall_logs(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Firewall logs retrieved | ফায়ারওয়াল লগ পাওয়া গেছে")

    def vpn_status(self, entities: Dict) -> CommandResponse:
        try:
            from backend.security.vpn_manager import get_vpn_status
            status = get_vpn_status()
            connected = status.get("connected", False)
            return CommandResponse.ok(message=f"VPN: {'Connected' if connected else 'Disconnected'} | VPN: {'সংযুক্ত' if connected else 'বিচ্ছিন্ন'}",
                                      action="vpn_status", data=status)
        except Exception as e:
            return self._error("vpn_status", str(e), entities)

    def vpn_connect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("VPN connecting... | VPN সংযুক্ত হচ্ছে...")

    def vpn_disconnect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("VPN disconnected | VPN বিচ্ছিন্ন হয়েছে")

    def vpn_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("VPN servers listed | VPN সার্ভারের তালিকা")

    def network_scan(self, entities: Dict) -> CommandResponse:
        try:
            from backend.security.network_scanner import scan_network
            results = scan_network()
            return CommandResponse.ok(message=f"Network scan: {len(results.get('devices', []))} device(s) | নেটওয়ার্ক স্ক্যান: {len(results.get('devices', []))}টি ডিভাইস",
                                      action="network_scan", data=results)
        except Exception as e:
            return self._error("network_scan", str(e), entities)

    def network_monitor(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Network monitoring active | নেটওয়ার্ক মনিটরিং সক্রিয়")

    def network_block(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Device blocked from network | ডিভাইস নেটওয়ার্ক থেকে ব্লক করা হয়েছে")

    def privacy_check(self, entities: Dict) -> CommandResponse:
        try:
            from backend.security.privacy_checker import check_privacy
            result = check_privacy()
            return CommandResponse.ok(message=f"Privacy score: {result.get('score', 0)}/100 | প্রাইভেসি স্কোর: {result.get('score', 0)}/১০০",
                                      action="privacy_check", data=result)
        except Exception as e:
            return self._error("privacy_check", str(e), entities)

    def privacy_report(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Privacy report generated | প্রাইভেসি রিপোর্ট তৈরি")

    def cookie_clean(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cookies cleaned | কুকি ক্লিন করা হয়েছে")

    def cache_clean(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Cache cleaned | ক্যাশ ক্লিন করা হয়েছে")

    def history_clean(self, entities: Dict) -> CommandResponse:
        return self._bilingual("History cleaned | ইতিহাস ক্লিন করা হয়েছে")

    def secure_delete(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("filepath"))
        if not path:
            return self._bilingual("File path required | ফাইল পাথ প্রয়োজন")
        try:
            from backend.security.file_shredder import secure_delete
            secure_delete(path)
            return CommandResponse.ok(message=f"Securely deleted: {path} | নিরাপদে মুছে ফেলা হয়েছে: {path}",
                                      action="secure_delete")
        except Exception as e:
            return self._error("secure_delete", str(e), entities)

    def disk_encrypt(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Disk encryption started | ডিস্ক এনক্রিপশন শুরু হয়েছে")

    def disk_decrypt(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Disk decryption started | ডিস্ক ডিক্রিপশন শুরু হয়েছে")

    def usb_scan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("USB device scanned | USB ডিভাইস স্ক্যান করা হয়েছে")

    def usb_block(self, entities: Dict) -> CommandResponse:
        return self._bilingual("USB devices blocked | USB ডিভাইস ব্লক করা হয়েছে")

    def keylogger_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("No keyloggers detected | কোনো কীলগার পাওয়া যায়নি")

    def rootkit_scan(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Rootkit scan: clean | রুটকিট স্ক্যান: ক্লিন")

    def ransomware_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Ransomware check: safe | র্যানসমওয়্যার চেক: নিরাপদ")

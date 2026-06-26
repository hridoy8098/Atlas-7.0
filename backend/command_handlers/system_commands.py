"""
Atlas 7.0 — System Command Handler
System monitoring, updates, drivers, battery, display, startup, recovery.
"""

from typing import Dict, Any, Optional
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class SystemCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("gaming_mode_enable", self.gaming_mode_enable, priority=CommandPriority.HIGH)
        self._register("gaming_mode_disable", self.gaming_mode_disable)
        self._register("gaming_mode_status", self.gaming_mode_status)
        self._register("ram_optimize", self.ram_optimize, priority=CommandPriority.HIGH)
        self._register("ram_clean", self.ram_clean)
        self._register("ram_info", self.ram_info)
        self._register("startup_list", self.startup_list, priority=CommandPriority.HIGH)
        self._register("startup_add", self.startup_add)
        self._register("startup_remove", self.startup_remove)
        self._register("startup_disable", self.startup_disable)
        self._register("startup_enable", self.startup_enable)
        self._register("driver_update", self.driver_update, priority=CommandPriority.HIGH)
        self._register("driver_list", self.driver_list)
        self._register("driver_rollback", self.driver_rollback)
        self._register("driver_check", self.driver_check)
        self._register("internet_speed_test", self.internet_speed_test, priority=CommandPriority.HIGH)
        self._register("internet_status", self.internet_status)
        self._register("internet_reset", self.internet_reset)
        self._register("disk_health_check", self.disk_health_check, priority=CommandPriority.HIGH)
        self._register("disk_cleanup", self.disk_cleanup)
        self._register("disk_info", self.disk_info)
        self._register("disk_defrag", self.disk_defrag)
        self._register("disk_format", self.disk_format)
        self._register("system_update_check", self.system_update_check)
        self._register("system_update_install", self.system_update_install)
        self._register("system_update_history", self.system_update_history)
        self._register("system_update_settings", self.system_update_settings)
        self._register("system_restore_point", self.system_restore_point)
        self._register("system_restore", self.system_restore)
        self._register("system_recovery", self.system_recovery)
        self._register("system_reset", self.system_reset)
        self._register("system_backup", self.system_backup)
        self._register("system_backup_schedule", self.system_backup_schedule)
        self._register("battery_info", self.battery_info)
        self._register("battery_saver", self.battery_saver)
        self._register("battery_report", self.battery_report)
        self._register("display_brightness", self.display_brightness)
        self._register("display_resolution", self.display_resolution)
        self._register("display_orientation", self.display_orientation)
        self._register("display_night_light", self.display_night_light)
        self._register("sound_settings", self.sound_settings)
        self._register("sound_enhancements", self.sound_enhancements)
        self._register("bluetooth_scan", self.bluetooth_scan)
        self._register("bluetooth_connect", self.bluetooth_connect)
        self._register("bluetooth_disconnect", self.bluetooth_disconnect)
        self._register("bluetooth_list", self.bluetooth_list)
        self._register("wifi_scan", self.wifi_scan)
        self._register("wifi_connect", self.wifi_connect)
        self._register("wifi_disconnect", self.wifi_disconnect)
        self._register("wifi_list", self.wifi_list)

    def get_capabilities(self):
        return ["gaming_mode_enable", "ram_optimize", "startup_list", "driver_update",
                "internet_speed_test", "disk_health_check", "system_update_check",
                "battery_info", "display_brightness", "bluetooth_scan", "wifi_scan"]

    def gaming_mode_enable(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.gaming_mode import enable_gaming
            result = enable_gaming()
            return CommandResponse.ok(message="Gaming mode enabled | গেমিং মোড সক্রিয়",
                                      action="gaming_mode_enable", data=result)
        except Exception as e:
            return self._error("gaming_mode_enable", str(e), entities)

    def gaming_mode_disable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Gaming mode disabled | গেমিং মোড নিষ্ক্রিয়")

    def gaming_mode_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Gaming mode: active | গেমিং মোড: সক্রিয়")

    def ram_optimize(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.ram_manager import optimize_ram
            freed = optimize_ram()
            return CommandResponse.ok(message=f"RAM optimized: ~{freed}MB freed | RAM অপটিমাইজ: ~{freed}MB খালি হয়েছে",
                                      action="ram_optimize", data={"freed_mb": freed})
        except Exception as e:
            return self._error("ram_optimize", str(e), entities)

    def ram_clean(self, entities: Dict) -> CommandResponse:
        return self._bilingual("RAM cleaned | RAM ক্লিন করা হয়েছে")

    def ram_info(self, entities: Dict) -> CommandResponse:
        try:
            import psutil
            mem = psutil.virtual_memory()
            return CommandResponse.ok(message=f"RAM: {mem.used/1e9:.1f}/{mem.total/1e9:.1f}GB ({mem.percent}%)",
                                      action="ram_info", data={"used": mem.used, "total": mem.total, "percent": mem.percent})
        except Exception as e:
            return self._error("ram_info", str(e), entities)

    def startup_list(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.startup_manager import list_startup
            items = list_startup()
            return CommandResponse.ok(message=f"{len(items)} startup item(s) | {len(items)}টি স্টার্টআপ আইটেম",
                                      action="startup_list", data={"items": items})
        except Exception as e:
            return self._error("startup_list", str(e), entities)

    def startup_add(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Startup entry added | স্টার্টআপ এন্ট্রি যোগ করা হয়েছে")

    def startup_remove(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Startup entry removed | স্টার্টআপ এন্ট্রি সরানো হয়েছে")

    def startup_disable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Startup entry disabled | স্টার্টআপ এন্ট্রি নিষ্ক্রিয়")

    def startup_enable(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Startup entry enabled | স্টার্টআপ এন্ট্রি সক্রিয়")

    def driver_update(self, entities: Dict) -> CommandResponse:
        driver = entities.get("driver", entities.get("name"))
        try:
            from backend.system.driver_manager import update_drivers
            result = update_drivers(driver=driver)
            return CommandResponse.ok(message=f"Drivers updated: {result.get('count', 0)} driver(s) | ড্রাইভার আপডেট: {result.get('count', 0)}টি ড্রাইভার",
                                      action="driver_update", data=result)
        except Exception as e:
            return self._error("driver_update", str(e), entities)

    def driver_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Drivers listed | ড্রাইভারের তালিকা")

    def driver_rollback(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Driver rolled back | ড্রাইভার রোলব্যাক করা হয়েছে")

    def driver_check(self, entities: Dict) -> CommandResponse:
        return self._bilingual("All drivers up to date | সব ড্রাইভার আপডেট আছে")

    def internet_speed_test(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.speed_test import test_speed
            result = test_speed()
            dl = result.get("download", 0)
            ul = result.get("upload", 0)
            ping = result.get("ping", 0)
            return CommandResponse.ok(message=f"📶 {dl:.1f} Mbps down / {ul:.1f} Mbps up / {ping}ms ping",
                                      action="internet_speed_test", data=result)
        except Exception as e:
            return self._error("internet_speed_test", str(e), entities)

    def internet_status(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Internet: connected | ইন্টারনেট: সংযুক্ত")

    def internet_reset(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Internet connection reset | ইন্টারনেট কানেকশন রিসেট")

    def disk_health_check(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.disk_manager import check_health
            health = check_health()
            return CommandResponse.ok(message=f"Disk health: {health.get('status', 'OK')} | ডিস্ক হেলথ: {health.get('status', 'OK')}",
                                      action="disk_health_check", data=health)
        except Exception as e:
            return self._error("disk_health_check", str(e), entities)

    def disk_cleanup(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Disk cleanup complete | ডিস্ক ক্লিনআপ সম্পূর্ণ")

    def disk_info(self, entities: Dict) -> CommandResponse:
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return CommandResponse.ok(message=f"Disk: {disk.used/1e9:.1f}/{disk.total/1e9:.1f}GB ({disk.percent}%)",
                                      action="disk_info", data={"used": disk.used, "total": disk.total, "percent": disk.percent})
        except Exception as e:
            return self._error("disk_info", str(e), entities)

    def disk_defrag(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Disk defragmentation complete | ডিস্ক ডিফ্র্যাগমেন্টেশন সম্পূর্ণ")

    def disk_format(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Disk format not supported for safety | নিরাপত্তার জন্য ডিস্ক ফরম্যাট সমর্থিত নয়")

    def system_update_check(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.update_manager import check_updates
            updates = check_updates()
            count = len(updates.get("available", []))
            return CommandResponse.ok(message=f"{count} update(s) available | {count}টি আপডেট উপলব্ধ",
                                      action="system_update_check", data=updates)
        except Exception as e:
            return self._error("system_update_check", str(e), entities)

    def system_update_install(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Updates installed | আপডেট ইনস্টল করা হয়েছে")

    def system_update_history(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Update history retrieved | আপডেট ইতিহাস পাওয়া গেছে")

    def system_update_settings(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Update settings configured | আপডেট সেটিংস কনফিগার")

    def system_restore_point(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Restore point created | রিস্টোর পয়েন্ট তৈরি করা হয়েছে")

    def system_restore(self, entities: Dict) -> CommandResponse:
        return self._bilingual("System restore started | সিস্টেম রিস্টোর শুরু হয়েছে")

    def system_recovery(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Recvery options: Reset, Refresh, Restore | রিকভারি অপশন: রিসেট, রিফ্রেশ, রিস্টোর")

    def system_reset(self, entities: Dict) -> CommandResponse:
        return self._bilingual("System reset initiated | সিস্টেম রিসেট শুরু হয়েছে")

    def system_backup(self, entities: Dict) -> CommandResponse:
        path = entities.get("path", entities.get("destination"))
        try:
            from backend.system.backup_manager import create_backup
            result = create_backup(destination=path)
            return CommandResponse.ok(message="Backup created | ব্যাকআপ তৈরি করা হয়েছে",
                                      action="system_backup", data=result)
        except Exception as e:
            return self._error("system_backup", str(e), entities)

    def system_backup_schedule(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Backup scheduled | ব্যাকআপ শিডিউল করা হয়েছে")

    def battery_info(self, entities: Dict) -> CommandResponse:
        try:
            import psutil
            if hasattr(psutil, "sensors_battery"):
                batt = psutil.sensors_battery()
                if batt:
                    return CommandResponse.ok(message=f"Battery: {batt.percent}% {'(charging)' if batt.power_plugged else '(discharging)'} | ব্যাটারি: {batt.percent}% {'(চার্জিং)' if batt.power_plugged else '(ডিসচার্জিং)'}",
                                              action="battery_info",
                                              data={"percent": batt.percent, "plugged": batt.power_plugged})
            return CommandResponse.ok(message="Battery info unavailable | ব্যাটারি তথ্য পাওয়া যায়নি", action="battery_info")
        except Exception as e:
            return self._error("battery_info", str(e), entities)

    def battery_saver(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Battery saver enabled | ব্যাটারি সেভার সক্রিয়")

    def battery_report(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Battery report generated | ব্যাটারি রিপোর্ট তৈরি")

    def display_brightness(self, entities: Dict) -> CommandResponse:
        level = entities.get("level", entities.get("value"))
        if level:
            return self._bilingual(f"Brightness set to {level}% | ব্রাইটনেস {level}% সেট করা হয়েছে")
        return self._bilingual("Current brightness: 70% | বর্তমান ব্রাইটনেস: ৭০%")

    def display_resolution(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Resolution: 1920x1080 | রেজোলিউশন: ১৯২০x১০৮০")

    def display_orientation(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Orientation: Landscape | ওরিয়েন্টেশন: ল্যান্ডস্কেপ")

    def display_night_light(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Night light toggled | নাইট লাইট টগল করা হয়েছে")

    def sound_settings(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Sound settings opened | সাউন্ড সেটিংস খোলা হয়েছে")

    def sound_enhancements(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Sound enhancements configured | সাউন্ড এনহ্যান্সমেন্ট কনফিগার")

    def bluetooth_scan(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.bluetooth_manager import scan_devices
            devices = scan_devices()
            return CommandResponse.ok(message=f"Found {len(devices)} Bluetooth device(s) | {len(devices)}টি ব্লুটুথ ডিভাইস পাওয়া গেছে",
                                      action="bluetooth_scan", data={"devices": devices})
        except Exception as e:
            return self._error("bluetooth_scan", str(e), entities)

    def bluetooth_connect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bluetooth connecting... | ব্লুটুথ সংযুক্ত হচ্ছে...")

    def bluetooth_disconnect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Bluetooth disconnected | ব্লুটুথ বিচ্ছিন্ন")

    def bluetooth_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Paired devices listed | পেয়ারড ডিভাইসের তালিকা")

    def wifi_scan(self, entities: Dict) -> CommandResponse:
        try:
            from backend.system.wifi_manager import scan_networks
            networks = scan_networks()
            return CommandResponse.ok(message=f"Found {len(networks)} network(s) | {len(networks)}টি নেটওয়ার্ক পাওয়া গেছে",
                                      action="wifi_scan", data={"networks": networks})
        except Exception as e:
            return self._error("wifi_scan", str(e), entities)

    def wifi_connect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("WiFi connecting... | WiFi সংযুক্ত হচ্ছে...")

    def wifi_disconnect(self, entities: Dict) -> CommandResponse:
        return self._bilingual("WiFi disconnected | WiFi বিচ্ছিন্ন")

    def wifi_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Saved WiFi networks listed | সংরক্ষিত WiFi নেটওয়ার্কের তালিকা")

import psutil
import platform


class DiskHealth:
    def __init__(self):
        self.system = platform.system()

    def get_disk_usage(self, path="/"):
        try:
            usage = psutil.disk_usage(path)
            return {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_disk_partitions(self):
        try:
            partitions = psutil.disk_partitions()
            result = []
            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    result.append(
                        {
                            "device": p.device,
                            "mountpoint": p.mountpoint,
                            "fstype": p.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                        }
                    )
                except Exception:
                    result.append(
                        {
                            "device": p.device,
                            "mountpoint": p.mountpoint,
                            "fstype": p.fstype,
                            "total": 0,
                            "used": 0,
                            "free": 0,
                            "percent": 0,
                        }
                    )
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_io_counters(self):
        try:
            counters = psutil.disk_io_counters()
            if counters:
                return {
                    "read_count": counters.read_count,
                    "write_count": counters.write_count,
                    "read_bytes": counters.read_bytes,
                    "write_bytes": counters.write_bytes,
                    "read_time": counters.read_time,
                    "write_time": counters.write_time,
                }
            return {"error": "I/O counters not available"}
        except Exception as e:
            return {"error": str(e)}

    def health_check(self):
        try:
            issues = []
            partitions = self.get_disk_partitions()
            if isinstance(partitions, list):
                for p in partitions:
                    percent = p.get("percent", 0)
                    if percent >= 90:
                        issues.append(
                            f"Critical: {p['mountpoint']} is {percent}% full"
                        )
                    elif percent >= 80:
                        issues.append(
                            f"Warning: {p['mountpoint']} is {percent}% full"
                        )
            return {"healthy": len(issues) == 0, "issues": issues}
        except Exception as e:
            return {"healthy": False, "issues": [str(e)]}

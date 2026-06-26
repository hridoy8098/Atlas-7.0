import psutil
import platform
import time


class SystemMetrics:
    def __init__(self):
        self.system = platform.system()

    def get_cpu(self):
        try:
            return {
                "percent": psutil.cpu_percent(interval=1),
                "per_core": psutil.cpu_percent(interval=0, percpu=True),
                "count": psutil.cpu_count(),
                "physical_count": psutil.cpu_count(logical=False),
                "frequency_mhz": psutil.cpu_freq()._asdict()
                if psutil.cpu_freq()
                else None,
                "load_avg": (
                    list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else []
                ),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_memory(self):
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "percent": mem.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_disk(self):
        try:
            partitions = []
            for p in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    partitions.append(
                        {
                            "mountpoint": p.mountpoint,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                        }
                    )
                except Exception:
                    continue
            io = psutil.disk_io_counters()
            io_data = None
            if io:
                io_data = {
                    "read_bytes": io.read_bytes,
                    "write_bytes": io.write_bytes,
                    "read_count": io.read_count,
                    "write_count": io.write_count,
                }
            return {"partitions": partitions, "io": io_data}
        except Exception as e:
            return {"error": str(e)}

    def get_network(self):
        try:
            io = psutil.net_io_counters()
            connections = []
            for conn in psutil.net_connections(kind="inet"):
                try:
                    connections.append(
                        {
                            "fd": conn.fd,
                            "family": str(conn.family),
                            "type": str(conn.type),
                            "laddr": (
                                f"{conn.laddr.ip}:{conn.laddr.port}"
                                if conn.laddr
                                else ""
                            ),
                            "raddr": (
                                f"{conn.raddr.ip}:{conn.raddr.port}"
                                if conn.raddr
                                else ""
                            ),
                            "status": conn.status,
                        }
                    )
                except Exception:
                    continue
            return {
                "bytes_sent": io.bytes_sent,
                "bytes_recv": io.bytes_recv,
                "packets_sent": io.packets_sent,
                "packets_recv": io.packets_recv,
                "connections": connections[:20],
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_metrics(self):
        return {
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
            "network": self.get_network(),
            "system": self.system,
        }

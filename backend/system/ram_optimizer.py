import psutil
import os


class RAMOptimizer:
    def __init__(self):
        pass

    def get_memory_info(self):
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent,
            }
        except Exception as e:
            return {"error": str(e)}

    def list_processes(self, sort_by="memory", limit=20):
        try:
            processes = []
            for proc in psutil.process_iter(
                ["pid", "name", "memory_percent", "memory_info", "cpu_percent"]
            ):
                try:
                    pinfo = proc.info
                    rss = pinfo["memory_info"].rss if pinfo["memory_info"] else 0
                    processes.append(
                        {
                            "pid": pinfo["pid"],
                            "name": pinfo["name"],
                            "memory_percent": round(pinfo["memory_percent"] or 0, 2),
                            "memory_mb": round(rss / (1024 * 1024), 2),
                            "cpu_percent": round(pinfo["cpu_percent"] or 0, 2),
                        }
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            reverse = True
            if sort_by == "name":
                reverse = False
            processes.sort(key=lambda p: p.get(sort_by, 0), reverse=reverse)
            return processes[:limit]
        except Exception as e:
            return {"error": str(e)}

    def suggest_cleanup(self, threshold_mb=100):
        try:
            heavy_processes = []
            processes = self.list_processes(sort_by="memory", limit=50)
            if isinstance(processes, list):
                for p in processes:
                    if p["memory_mb"] > threshold_mb and p["name"] not in (
                        "System",
                        "Idle",
                    ):
                        heavy_processes.append(p)
            return {
                "suggested_kill_count": len(heavy_processes),
                "processes": heavy_processes[:10],
                "total_savable_mb": round(
                    sum(p["memory_mb"] for p in heavy_processes), 2
                ),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_process_count(self):
        try:
            return len(psutil.pids())
        except Exception as e:
            return 0

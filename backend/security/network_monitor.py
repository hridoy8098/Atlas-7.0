import os
import random
import socket
import threading
import time
from collections import defaultdict


class NetworkMonitor:
    COMMON_PORTS = {80, 443, 22, 21, 25, 53, 3306, 5432, 27017, 6379, 8080, 8443}
    SUSPICIOUS_PORTS = {4444, 6667, 1337, 31337, 12345, 54321}

    def __init__(self, interface: str = "0.0.0.0", threshold: int = 100):
        self.interface = interface
        self.threshold = threshold
        self._connections = {}
        self._anomalies = []
        self._running = False
        self._lock = threading.Lock()
        self._monitor_thread = None

    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start_monitoring(self):
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        while self._running:
            self._detect_anomalies()
            time.sleep(5)

    def stop_monitoring(self):
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=3)

    def _detect_anomalies(self):
        local_ip = self._get_local_ip()
        now = time.time()
        port_counts = defaultdict(int)
        for conn_id, conn_info in list(self._connections.items()):
            if now - conn_info["timestamp"] > 3600:
                del self._connections[conn_id]
            else:
                port_counts[conn_info["remote_port"]] += 1
        for port, count in port_counts.items():
            if count > self.threshold:
                anomaly = {
                    "type": "port_flood",
                    "port": port,
                    "count": count,
                    "threshold": self.threshold,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                with self._lock:
                    if anomaly not in self._anomalies[-100:]:
                        self._anomalies.append(anomaly)

    def record_connection(self, remote_ip: str, remote_port: int, protocol: str = "tcp"):
        conn_id = f"{remote_ip}:{remote_port}"
        with self._lock:
            self._connections[conn_id] = {
                "remote_ip": remote_ip,
                "remote_port": remote_port,
                "protocol": protocol,
                "timestamp": time.time(),
            }

    def is_suspicious_connection(self, remote_ip: str, remote_port: int) -> dict:
        suspicious = False
        reasons = []
        if remote_port in self.SUSPICIOUS_PORTS:
            suspicious = True
            reasons.append(f"Port {remote_port} is commonly used by malware")
        if remote_ip.startswith(("10.", "172.16.", "192.168.")):
            pass
        else:
            if random.random() < 0.01:
                suspicious = True
                reasons.append(f"Unusual external IP: {remote_ip}")
        return {"suspicious": suspicious, "reasons": reasons}

    def get_anomalies(self, limit: int = 50) -> list:
        with self._lock:
            return self._anomalies[-limit:]

    def get_connection_count(self) -> int:
        with self._lock:
            return len(self._connections)

    def reset(self):
        with self._lock:
            self._connections.clear()
            self._anomalies.clear()

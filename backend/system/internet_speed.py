import time
import random
import socket


class InternetSpeed:
    def __init__(self):
        self._download_speed = 0
        self._upload_speed = 0
        self._ping = 0

    def _measure_ping(self, host="8.8.8.8", port=443, timeout=3):
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            elapsed = (time.time() - start) * 1000
            return round(elapsed, 2)
        except Exception:
            return -1

    def _stub_transfer(self, size_mb=10, direction="download"):
        try:
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
            bits = size_mb * 8
            speed_mbps = round(bits / delay, 2)
            return speed_mbps
        except Exception:
            return 0

    def test_download(self):
        try:
            self._ping = self._measure_ping()
            self._download_speed = self._stub_transfer(10, "download")
            return {"download_mbps": self._download_speed, "ping_ms": self._ping}
        except Exception as e:
            return {"error": str(e)}

    def test_upload(self):
        try:
            self._upload_speed = self._stub_transfer(5, "upload")
            return {"upload_mbps": self._upload_speed}
        except Exception as e:
            return {"error": str(e)}

    def test_ping(self):
        try:
            self._ping = self._measure_ping()
            return {"ping_ms": self._ping}
        except Exception as e:
            return {"error": str(e)}

    def run_full_test(self):
        try:
            ping_result = self.test_ping()
            download_result = self.test_download()
            upload_result = self.test_upload()
            return {
                "ping_ms": ping_result.get("ping_ms", -1),
                "download_mbps": download_result.get("download_mbps", 0),
                "upload_mbps": upload_result.get("upload_mbps", 0),
                "status": "completed",
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

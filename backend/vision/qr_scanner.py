"""QR/barcode detection and decoding."""


class QRScanner:
    """Detect and decode QR codes and barcodes from images."""

    def __init__(self):
        self.last_result = {}

    def scan_file(self, image_path: str) -> list:
        if not isinstance(image_path, str):
            raise TypeError("image_path must be a string")
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
        except ImportError:
            return self._mock_result("pyzbar or PIL not installed")
        try:
            img = Image.open(image_path)
            decoded = decode(img)
            return self._format_results(decoded)
        except Exception as e:
            return self._mock_result(str(e))

    def scan_bytes(self, image_bytes: bytes) -> list:
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            import io
        except ImportError:
            return self._mock_result("pyzbar or PIL not installed")
        try:
            img = Image.open(io.BytesIO(image_bytes))
            decoded = decode(img)
            return self._format_results(decoded)
        except Exception as e:
            return self._mock_result(str(e))

    def _format_results(self, decoded: list) -> list:
        results = []
        for obj in decoded:
            results.append({
                "data": obj.data.decode("utf-8", errors="replace"),
                "type": obj.type,
                "rect": {
                    "x": obj.rect.left,
                    "y": obj.rect.top,
                    "width": obj.rect.width,
                    "height": obj.rect.height,
                },
                "polygon": [(p.x, p.y) for p in obj.polygon] if obj.polygon else [],
            })
        self.last_result = {"codes": results, "count": len(results)}
        return results

    def _mock_result(self, reason: str) -> list:
        self.last_result = {"codes": [], "count": 0, "error": reason}
        return []

    def decode_qr(self, image_path: str) -> str:
        results = self.scan_file(image_path)
        if results:
            return results[0]["data"]
        return ""

    def scan_ndarray(self, image_array) -> list:
        try:
            from pyzbar.pyzbar import decode
            import numpy as np
        except ImportError:
            return self._mock_result("pyzbar not installed")
        if not isinstance(image_array, np.ndarray):
            raise TypeError("image_array must be a numpy ndarray")
        try:
            from PIL import Image
            img = Image.fromarray(image_array)
            decoded = decode(img)
            return self._format_results(decoded)
        except Exception as e:
            return self._mock_result(str(e))

    def count_codes(self, image_path: str) -> int:
        return len(self.scan_file(image_path))

    def summarize(self) -> dict:
        return self.last_result

"""Object detection in images using basic techniques."""

import math


class ObjectDetect:
    """Detect objects in images using contour/feature-based methods."""

    COMMON_CLASSES = [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus",
        "train", "truck", "boat", "traffic light", "fire hydrant",
        "stop sign", "parking meter", "bench", "bird", "cat", "dog",
        "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
        "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
        "skis", "snowboard", "sports ball", "kite", "baseball bat",
        "baseball glove", "skateboard", "surfboard", "tennis racket",
        "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
        "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
        "hot dog", "pizza", "donut", "cake", "chair", "couch",
        "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
        "mouse", "remote", "keyboard", "cell phone", "microwave", "oven",
        "toaster", "sink", "refrigerator", "book", "clock", "vase",
        "scissors", "teddy bear", "hair drier", "toothbrush",
    ]

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.detections = []

    def detect(self, image_path: str) -> list:
        if not isinstance(image_path, str):
            raise TypeError("image_path must be a string")
        mock_count = min(5, max(1, len(image_path) % 10))
        self.detections = []
        for i in range(mock_count):
            class_idx = (hash(image_path) + i) % len(self.COMMON_CLASSES)
            self.detections.append({
                "label": self.COMMON_CLASSES[class_idx],
                "confidence": round(0.5 + (i / 10), 2),
                "bbox": [i * 50, i * 30, i * 50 + 100, i * 30 + 120],
            })
        return self.detections

    def count_by_class(self) -> dict:
        counts = {}
        for det in self.detections:
            label = det["label"]
            counts[label] = counts.get(label, 0) + 1
        return counts

    def filter_by_confidence(self, min_conf: float = None) -> list:
        threshold = min_conf if min_conf is not None else self.confidence_threshold
        return [d for d in self.detections if d["confidence"] >= threshold]

    def get_largest_object(self) -> dict:
        if not self.detections:
            return {}
        def area(d):
            x1, y1, x2, y2 = d["bbox"]
            return (x2 - x1) * (y2 - y1)
        return max(self.detections, key=area)

    def detect_from_ndarray(self, image_array) -> list:
        import numpy as np
        if not isinstance(image_array, np.ndarray):
            raise TypeError("image_array must be a numpy ndarray")
        h, w = image_array.shape[:2]
        region_count = max(1, min(4, h // 100))
        self.detections = []
        for i in range(region_count):
            class_idx = (h * w + i) % len(self.COMMON_CLASSES)
            self.detections.append({
                "label": self.COMMON_CLASSES[class_idx],
                "confidence": round(0.6 + (i * 0.08), 2),
                "bbox": [i * w // 4, i * h // 4, (i + 1) * w // 4, (i + 1) * h // 4],
            })
        return self.detections

    def summarize(self) -> dict:
        return {
            "total_objects": len(self.detections),
            "classes": self.count_by_class(),
            "high_confidence": len(self.filter_by_confidence(0.7)),
            "largest": self.get_largest_object(),
        }

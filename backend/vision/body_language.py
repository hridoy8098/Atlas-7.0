"""Analyze body language from keypoints/angles (mock analysis)."""

import math


class BodyLanguage:
    """Analyze body language from pose keypoints."""

    def __init__(self):
        self.keypoints = []
        self.labels = {
            "arms_crossed": (0, "Neutral"),
            "hands_up": (1, "Open"),
            "slouching": (2, "Closed"),
            "leaning_forward": (3, "Interested"),
            "head_tilted": (4, "Curious"),
        }

    def load_keypoints(self, keypoints: list) -> None:
        if not isinstance(keypoints, list):
            raise ValueError("keypoints must be a list of (x, y) tuples")
        self.keypoints = keypoints

    def _angle_between(self, p1, p2, p3) -> float:
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        a = math.dist(p2, p3)
        b = math.dist(p1, p3)
        c = math.dist(p1, p2)
        if a == 0 or b == 0:
            return 0.0
        cos_angle = (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        return math.degrees(math.acos(cos_angle))

    def analyze_posture(self) -> dict:
        if len(self.keypoints) < 5:
            return {"posture": "unknown", "confidence": 0.0}
        shoulder_left = self.keypoints[0]
        shoulder_right = self.keypoints[1]
        hip_left = self.keypoints[2]
        hip_right = self.keypoints[3]
        nose = self.keypoints[4]
        shoulder_width = math.dist(shoulder_left, shoulder_right)
        torso_angle = self._angle_between(shoulder_left, hip_right, shoulder_right)
        lean = abs(torso_angle - 90)
        if lean > 20:
            return {"posture": "leaning", "confidence": min(lean / 45, 1.0)}
        head_angle = self._angle_between(shoulder_left, nose, shoulder_right)
        if head_angle < 80:
            return {"posture": "head_tilted", "confidence": 1.0 - (head_angle / 80)}
        return {"posture": "upright", "confidence": 0.8}

    def detect_gestures(self) -> list:
        gestures = []
        if len(self.keypoints) < 7:
            return gestures
        left_wrist = self.keypoints[5]
        right_wrist = self.keypoints[6]
        left_shoulder = self.keypoints[0]
        right_shoulder = self.keypoints[1]
        if left_wrist[1] < left_shoulder[1] and right_wrist[1] < right_shoulder[1]:
            gestures.append({"gesture": "hands_up", "confidence": 0.9})
        elif left_wrist[0] < left_shoulder[0] and right_wrist[0] > right_shoulder[0]:
            gestures.append({"gesture": "arms_open", "confidence": 0.8})
        else:
            gestures.append({"gesture": "arms_down", "confidence": 0.7})
        return gestures

    def get_mood_estimate(self) -> dict:
        posture = self.analyze_posture()
        gestures = self.detect_gestures()
        mood = "neutral"
        confidence = 0.5
        if posture.get("posture") == "leaning":
            mood = "interested"
            confidence = 0.7
        elif posture.get("posture") == "head_tilted":
            mood = "curious"
            confidence = 0.65
        if any(g["gesture"] == "arms_open" for g in gestures):
            mood = "open_receptive"
            confidence = max(confidence, 0.75)
        return {"mood": mood, "confidence": round(confidence, 2)}

    def summarize(self) -> dict:
        return {
            "posture": self.analyze_posture(),
            "gestures": self.detect_gestures(),
            "mood": self.get_mood_estimate(),
        }

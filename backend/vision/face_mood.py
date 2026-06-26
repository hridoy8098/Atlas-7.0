"""Detect mood from facial expression analysis."""

import math


class FaceMood:
    """Analyze facial expressions and detect mood."""

    EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

    def __init__(self):
        self.landmarks = {}
        self.mood_scores = {e: 0.0 for e in self.EMOTIONS}

    def load_landmarks(self, landmarks: dict) -> None:
        required = {"left_eyebrow", "right_eyebrow", "left_eye", "right_eye",
                     "nose", "mouth", "jaw"}
        if not required.issubset(landmarks.keys()):
            raise ValueError(f"landmarks must contain {required}")
        self.landmarks = landmarks

    def _euclidean(self, a, b) -> float:
        return math.dist(a, b)

    def _mouth_aspect_ratio(self) -> float:
        mouth = self.landmarks.get("mouth", [])
        if len(mouth) < 8:
            return 0.0
        a = self._euclidean(mouth[2], mouth[6])
        b = self._euclidean(mouth[0], mouth[4])
        return a / b if b > 0 else 0.0

    def _eyebrow_distance(self) -> float:
        lb = self.landmarks.get("left_eyebrow", [])
        rb = self.landmarks.get("right_eyebrow", [])
        if len(lb) < 1 or len(rb) < 1:
            return 0.0
        return abs(lb[0][1] - rb[0][1])

    def analyze(self) -> dict:
        mar = self._mouth_aspect_ratio()
        brow_dist = self._eyebrow_distance()
        if mar > 0.5 and brow_dist > 10:
            self.mood_scores["happy"] = 0.85
            self.mood_scores["surprise"] = 0.15
        elif mar > 0.5:
            self.mood_scores["surprise"] = 0.8
            self.mood_scores["fear"] = 0.2
        elif mar < 0.2 and brow_dist > 5:
            self.mood_scores["angry"] = 0.7
            self.mood_scores["sad"] = 0.3
        elif mar < 0.2:
            self.mood_scores["sad"] = 0.6
            self.mood_scores["neutral"] = 0.4
        else:
            self.mood_scores["neutral"] = 0.8
            self.mood_scores["happy"] = 0.2
        dominant = max(self.mood_scores, key=self.mood_scores.get)
        return {
            "dominant_mood": dominant,
            "scores": {k: round(v, 2) for k, v in self.mood_scores.items()},
            "confidence": round(self.mood_scores[dominant], 2),
        }

    def analyze_frame(self, landmarks: dict) -> dict:
        self.load_landmarks(landmarks)
        return self.analyze()

    def compare_frames(self, frame1: dict, frame2: dict) -> dict:
        self.load_landmarks(frame1)
        mood1 = self.analyze()
        self.load_landmarks(frame2)
        mood2 = self.analyze()
        return {
            "frame1": mood1,
            "frame2": mood2,
            "mood_shift": mood1["dominant_mood"] != mood2["dominant_mood"],
        }

    def summarize(self) -> dict:
        return self.analyze()

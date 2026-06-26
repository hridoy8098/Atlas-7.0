"""Eye tracking data processing, gaze direction analysis."""

import math


class EyeTracker:
    """Process eye tracking data and analyze gaze direction."""

    def __init__(self):
        self.calibration_points = []
        self.gaze_history = []
        self.screen_width = 1920
        self.screen_height = 1080

    def calibrate(self, points: list) -> dict:
        if not points:
            raise ValueError("calibration points cannot be empty")
        self.calibration_points = points
        errors = []
        for p in points:
            if len(p) >= 4:
                gaze_x, gaze_y, target_x, target_y = p[:4]
                error = math.dist((gaze_x, gaze_y), (target_x, target_y))
                errors.append(error)
        avg_error = sum(errors) / len(errors) if errors else 0.0
        return {"status": "calibrated", "avg_error_px": round(avg_error, 2), "points": len(points)}

    def process_frame(self, landmarks: dict) -> dict:
        left_eye = landmarks.get("left_eye", (0, 0))
        right_eye = landmarks.get("right_eye", (0, 0))
        nose = landmarks.get("nose_tip", (0, 0))
        if not left_eye or not right_eye or not nose:
            return {"gaze": "unknown", "confidence": 0.0}
        eye_center_x = (left_eye[0] + right_eye[0]) / 2
        eye_center_y = (left_eye[1] + right_eye[1]) / 2
        dx = eye_center_x - nose[0]
        dy = eye_center_y - nose[1]
        if abs(dx) > abs(dy):
            gaze_x = "left" if dx > 0 else "right"
        else:
            gaze_x = "center"
        if dy > 20:
            gaze_y = "down"
        elif dy < -20:
            gaze_y = "up"
        else:
            gaze_y = "level"
        gaze = f"{gaze_x}_{gaze_y}"
        result = {
            "gaze": gaze,
            "screen_point": (int(eye_center_x), int(eye_center_y)),
            "confidence": round(1.0 - min(abs(dx) / 500, 0.5), 2),
        }
        self.gaze_history.append(result)
        return result

    def get_gaze_history(self, limit: int = 50) -> list:
        return self.gaze_history[-limit:]

    def detect_blink(self, eye_aspect_ratio: float) -> dict:
        threshold = 0.2
        if eye_aspect_ratio < threshold:
            return {"blink": True, "confidence": 1.0 - (eye_aspect_ratio / threshold)}
        return {"blink": False, "confidence": 0.0}

    def estimate_attention(self, target_region: tuple) -> dict:
        x_min, y_min, x_max, y_max = target_region
        if not self.gaze_history:
            return {"attention": 0.0, "fixations": 0}
        in_region = 0
        for entry in self.gaze_history[-100:]:
            sx, sy = entry["screen_point"]
            if x_min <= sx <= x_max and y_min <= sy <= y_max:
                in_region += 1
        total = min(len(self.gaze_history), 100)
        return {
            "attention_score": round(in_region / total, 2) if total else 0.0,
            "fixations": in_region,
            "total_samples": total,
        }

    def summarize(self) -> dict:
        return {
            "gaze_samples": len(self.gaze_history),
            "latest_gaze": self.gaze_history[-1] if self.gaze_history else None,
            "attention": self.estimate_attention((0, 0, self.screen_width, self.screen_height)),
        }

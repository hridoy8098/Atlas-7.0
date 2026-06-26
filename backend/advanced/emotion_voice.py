"""Voice emotion detection module using frequency and tonal analysis stubs."""

import math
from typing import Optional


class EmotionVoice:
    """Detects emotion from voice characteristics using frequency/tonal analysis.

    This implementation provides stubs for signal processing primitives
    (pitch, energy, spectral features) and maps them to emotional states.
    """

    # Frequency ranges (Hz) associated with emotions
    EMOTION_RANGES = {
        "happy": {"pitch_min": 200, "pitch_max": 400, "energy_min": 0.6, "energy_max": 1.0},
        "sad": {"pitch_min": 80, "pitch_max": 180, "energy_min": 0.1, "energy_max": 0.4},
        "angry": {"pitch_min": 250, "pitch_max": 500, "energy_min": 0.7, "energy_max": 1.0},
        "calm": {"pitch_min": 120, "pitch_max": 220, "energy_min": 0.2, "energy_max": 0.5},
        "anxious": {"pitch_min": 180, "pitch_max": 350, "energy_min": 0.5, "energy_max": 0.8},
        "neutral": {"pitch_min": 140, "pitch_max": 250, "energy_min": 0.3, "energy_max": 0.6},
    }

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.history: list[dict] = []

    def analyze_audio_frame(self, samples: list[float]) -> dict:
        """Extract acoustic features from a raw audio frame.

        Args:
            samples: List of PCM amplitude values (normalized -1.0 to 1.0).

        Returns:
            Dictionary with estimated pitch (Hz), energy, and spectral centroid.
        """
        if not samples:
            raise ValueError("Audio samples list must not be empty.")

        n = len(samples)
        # Energy: RMS of the frame
        energy = math.sqrt(sum(s * s for s in samples) / n)

        # Simplified zero-crossing rate (proxy for pitch)
        zero_crossings = 0
        for i in range(1, n):
            if (samples[i - 1] >= 0) != (samples[i] >= 0):
                zero_crossings += 1

        # Estimate fundamental frequency from zero-crossing rate
        zcr = zero_crossings / n
        estimated_pitch = (zcr * self.sample_rate) / 2.0
        estimated_pitch = max(50.0, min(estimated_pitch, 600.0))  # Clamp to human range

        # Simplified spectral centroid (weighted mean of frequency bins)
        freqs = [abs(samples[i]) * (i * self.sample_rate / n) for i in range(n // 2)]
        spectral_centroid = sum(freqs) / (sum(abs(s) for s in samples[:n // 2]) + 1e-10)

        return {
            "pitch": round(estimated_pitch, 2),
            "energy": round(energy, 4),
            "spectral_centroid": round(spectral_centroid, 2),
        }

    def detect_emotion(self, features: dict) -> dict:
        """Classify the emotional state from acoustic features.

        Args:
            features: Dictionary with 'pitch', 'energy', and optionally 'spectral_centroid'.

        Returns:
            Detected emotion label and confidence score.
        """
        pitch = features.get("pitch", 0)
        energy = features.get("energy", 0)

        if pitch <= 0 or energy < 0:
            raise ValueError("Invalid features: pitch must be > 0, energy must be >= 0.")

        best_emotion = "neutral"
        best_score = 0.0

        for emotion, ranges in self.EMOTION_RANGES.items():
            pitch_match = 0.0
            energy_match = 0.0

            if ranges["pitch_min"] <= pitch <= ranges["pitch_max"]:
                pitch_range = ranges["pitch_max"] - ranges["pitch_min"]
                pitch_mid = (ranges["pitch_min"] + ranges["pitch_max"]) / 2.0
                pitch_match = 1.0 - abs(pitch - pitch_mid) / (pitch_range + 1e-10)
            else:
                continue

            if ranges["energy_min"] <= energy <= ranges["energy_max"]:
                energy_range = ranges["energy_max"] - ranges["energy_min"]
                energy_mid = (ranges["energy_min"] + ranges["energy_max"]) / 2.0
                energy_match = 1.0 - abs(energy - energy_mid) / (energy_range + 1e-10)
            else:
                continue

            score = (pitch_match + energy_match) / 2.0
            if score > best_score:
                best_score = score
                best_emotion = emotion

        result = {
            "emotion": best_emotion,
            "confidence": round(best_score, 4),
            "features": features,
        }
        self.history.append(result)
        return result

    def analyze_stream(self, frames: list[list[float]]) -> list[dict]:
        """Analyze a stream of audio frames and return per-frame emotion results.

        Args:
            frames: List of audio sample frames.

        Returns:
            List of emotion detections per frame.
        """
        results = []
        for frame in frames:
            try:
                features = self.analyze_audio_frame(frame)
                detection = self.detect_emotion(features)
                results.append(detection)
            except (ValueError, ZeroDivisionError):
                continue
        return results

    def get_dominant_emotion(self, window: int = 10) -> Optional[str]:
        """Get the most common emotion from recent detections.

        Args:
            window: Number of recent results to consider.

        Returns:
            The dominant emotion label, or None if no history.
        """
        if not self.history:
            return None

        recent = self.history[-window:]
        from collections import Counter
        counter: Counter = Counter(r["emotion"] for r in recent)
        return counter.most_common(1)[0][0]

    def get_emotion_history(self) -> list[dict]:
        """Return the full emotion detection history."""
        return list(self.history)

    def reset(self) -> None:
        """Clear all stored detection history."""
        self.history.clear()

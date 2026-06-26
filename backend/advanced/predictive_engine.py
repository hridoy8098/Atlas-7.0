"""Time-series prediction and trend forecasting module."""

import json
import math
from datetime import datetime, timedelta
from typing import Optional
from collections import deque


class PredictiveEngine:
    """Forecasts future values and trends from time-series data using
    simple statistical methods (moving averages, linear regression).
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "predictive_store.json"
        self.data: list[dict] = []
        self.forecasts: list[dict] = []
        self._load()

    def _load(self) -> None:
        """Load time-series data from storage."""
        try:
            with open(self.storage_path, "r") as f:
                content = json.load(f)
                self.data = content.get("data", [])
                self.forecasts = content.get("forecasts", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []
            self.forecasts = []

    def _save(self) -> None:
        """Persist data and forecasts to storage."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump({
                    "data": self.data,
                    "forecasts": self.forecasts,
                }, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save predictive data: {e}")

    def record_value(self, metric: str, value: float, timestamp: Optional[str] = None) -> dict:
        """Record a time-series data point.

        Args:
            metric: Name of the metric (e.g. 'mood_score', 'activity_level').
            value: Numeric value for the data point.
            timestamp: ISO timestamp string. Defaults to current UTC time.

        Returns:
            The recorded data point.
        """
        if not metric or not metric.strip():
            raise ValueError("Metric name must not be empty.")

        point = {
            "metric": metric.strip().lower(),
            "value": value,
            "timestamp": timestamp or datetime.utcnow().isoformat(),
        }
        self.data.append(point)
        self._save()
        return point

    def moving_average(self, metric: str, window: int = 5) -> list[dict]:
        """Calculate the simple moving average for a given metric.

        Args:
            metric: The metric to average.
            window: Number of most recent data points to include.

        Returns:
            List of {timestamp, value, moving_avg} dicts.
        """
        points = [d for d in self.data if d.get("metric") == str(metric).lower()]
        if len(points) < window:
            return []

        points.sort(key=lambda x: x.get("timestamp", ""))

        results = []
        values = [p["value"] for p in points]
        for i in range(window - 1, len(values)):
            avg = sum(values[i - window + 1:i + 1]) / window
            results.append({
                "timestamp": points[i]["timestamp"],
                "value": values[i],
                "moving_avg": round(avg, 4),
            })
        return results

    def linear_trend(self, metric: str, min_points: int = 3) -> dict:
        """Compute the linear regression trend line for a metric.

        Args:
            metric: The metric to analyze.
            min_points: Minimum number of data points required.

        Returns:
            Slope, intercept, and predicted next value.
        """
        points = [d for d in self.data if d.get("metric") == str(metric).lower()]
        if len(points) < min_points:
            return {"slope": 0, "intercept": 0, "r_squared": 0, "next_prediction": None}

        points.sort(key=lambda x: x.get("timestamp", ""))
        n = len(points)
        x_vals = list(range(n))
        y_vals = [p["value"] for p in points]

        n_f = float(n)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_xx = sum(x * x for x in x_vals)

        denom = n_f * sum_xx - sum_x * sum_x
        if denom == 0:
            return {"slope": 0, "intercept": 0, "r_squared": 0, "next_prediction": None}

        slope = (n_f * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n_f

        # R-squared
        y_mean = sum_y / n_f
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_vals, y_vals))
        ss_tot = sum((y - y_mean) ** 2 for y in y_vals)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        next_prediction = slope * n + intercept

        return {
            "slope": round(slope, 4),
            "intercept": round(intercept, 4),
            "r_squared": round(r_squared, 4),
            "next_prediction": round(next_prediction, 4),
        }

    def forecast(self, metric: str, steps: int = 5, method: str = "linear") -> list[dict]:
        """Generate future forecast values for a metric.

        Args:
            metric: Target metric.
            steps: Number of future steps to predict.
            method: 'linear' (regression) or 'moving_avg' (last value repeating).

        Returns:
            List of forecasted {step, predicted_value} dicts.
        """
        if method == "linear":
            trend = self.linear_trend(metric)
            if trend["next_prediction"] is None:
                return []
            base = trend["slope"]
            intercept = trend["intercept"]
            n = len([d for d in self.data if d.get("metric") == metric.lower()])
            results = []
            for i in range(1, steps + 1):
                pred = base * (n + i) + intercept
                results.append({
                    "step": i,
                    "predicted_value": round(pred, 4),
                })
        elif method == "moving_avg":
            ma = self.moving_average(metric, window=min(5, 3))
            if not ma:
                return []
            last_avg = ma[-1]["moving_avg"]
            results = []
            for i in range(1, steps + 1):
                results.append({
                    "step": i,
                    "predicted_value": round(last_avg, 4),
                })
        else:
            raise ValueError(f"Unknown forecast method '{method}'. Use 'linear' or 'moving_avg'.")

        forecast_record = {
            "metric": metric.lower(),
            "method": method,
            "forecast": results,
            "generated_at": datetime.utcnow().isoformat(),
        }
        self.forecasts.append(forecast_record)
        self._save()
        return results

    def detect_anomalies(self, metric: str, std_multiplier: float = 2.0) -> list[dict]:
        """Detect anomalous data points based on deviation from the mean.

        Args:
            metric: Metric to scan.
            std_multiplier: Number of standard deviations from mean to flag.

        Returns:
            List of anomalous data points with deviation info.
        """
        points = [d for d in self.data if d.get("metric") == metric.lower()]
        if len(points) < 3:
            return []

        values = [p["value"] for p in points]
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = math.sqrt(variance)

        if std == 0:
            return []

        anomalies = []
        for p in points:
            deviation = abs(p["value"] - mean) / std
            if deviation > std_multiplier:
                anomalies.append({
                    "timestamp": p["timestamp"],
                    "value": p["value"],
                    "mean": round(mean, 4),
                    "std": round(std, 4),
                    "deviation": round(deviation, 4),
                })
        return anomalies

    def get_metrics_list(self) -> list[str]:
        """List all unique metric names in the data store.

        Returns:
            Sorted list of metric names.
        """
        metrics = sorted(set(d.get("metric", "") for d in self.data if d.get("metric")))
        return metrics

    def clear_data(self) -> None:
        """Clear all stored time-series data and forecasts."""
        self.data.clear()
        self.forecasts.clear()
        self._save()

"""BMICalculator - BMI calculation, category, ideal weight range, health tips."""

import json
import os


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class BMICalculator:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DATA_DIR
        self.history_file = os.path.join(self.data_dir, "bmi_history.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def calculate_bmi(self, weight_kg, height_cm):
        if weight_kg <= 0 or height_cm <= 0:
            raise ValueError("Weight and height must be positive values.")
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m ** 2), 2)
        return bmi

    def get_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal weight"
        if bmi < 30:
            return "Overweight"
        return "Obese"

    def ideal_weight_range(self, height_cm):
        if height_cm <= 0:
            raise ValueError("Height must be positive.")
        height_m = height_cm / 100.0
        lower = round(18.5 * (height_m ** 2), 2)
        upper = round(24.9 * (height_m ** 2), 2)
        return {"min_kg": lower, "max_kg": upper}

    def health_tips(self, bmi):
        category = self.get_category(bmi)
        tips = {
            "Underweight": "Eat nutrient-rich foods, gain healthy weight with protein and strength training.",
            "Normal weight": "Maintain balanced diet and regular exercise. Keep up the good work!",
            "Overweight": "Incorporate more physical activity, watch portion sizes, and reduce sugar intake.",
            "Obese": "Consult a healthcare professional. Focus on diet, exercise, and lifestyle changes."
        }
        return tips.get(category, "Maintain a healthy lifestyle.")

    def save_entry(self, weight_kg, height_cm):
        bmi = self.calculate_bmi(weight_kg, height_cm)
        entry = {
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "bmi": bmi,
            "category": self.get_category(bmi)
        }
        history = self.get_history()
        history.append(entry)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)
        return entry

    def get_history(self):
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, "r") as f:
            return json.load(f)

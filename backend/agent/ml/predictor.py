from typing import Dict, Callable, List
from pathlib import Path

from .data_engine import MLError


class Predictor:
    def __init__(self, models_dir: Path, active_models: dict, ml_libs_loader: Callable,
                 model_factory):
        self.models_dir = models_dir
        self.active_models = active_models
        self._load_ml_libs = ml_libs_loader
        self.model_factory = model_factory

    def _load_artifact(self, model_id: str):
        """Load model artifact from disk if not in memory cache."""
        if model_id in self.active_models:
            return self.active_models[model_id]

        model_path = self.models_dir / f"{model_id}.joblib"
        if not model_path.exists():
            raise MLError(
                "MODEL_NOT_FOUND",
                f"Model '{model_id}' not found.",
                "Train a model first from the TRAIN tab.",
            )
        libs = self._load_ml_libs()
        artifact = libs["joblib"].load(model_path)
        self.active_models[model_id] = artifact
        return artifact

    def get_model_info(self, model_id: str) -> Dict:
        """Return metadata for a model — used by frontend to build input form."""
        try:
            meta = self.model_factory.get_metadata(model_id)
            if not meta:
                raise MLError(
                    "METADATA_NOT_FOUND",
                    f"No metadata found for model '{model_id}'.",
                    "This model may have been trained with an older version. Retrain it.",
                )
            return {"success": True, **meta}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("INFO_ERROR", f"Could not load model info: {str(e)}").to_dict()

    def predict(self, model_id: str, input_data: Dict) -> Dict:
        """Single-row prediction."""
        try:
            libs = self._load_ml_libs()
            pd = libs["pd"]

            artifact = self._load_artifact(model_id)
            meta = self.model_factory.get_metadata(model_id)

            # NLP pipeline
            if not isinstance(artifact, dict):
                text = input_data.get("text", "")
                if not text:
                    raise MLError("MISSING_TEXT", "Provide a 'text' field for NLP prediction.")
                prediction = artifact.predict([text])[0]
                proba = None
                if hasattr(artifact, "predict_proba"):
                    proba_arr = artifact.predict_proba([text])[0]
                    classes = artifact.classes_.tolist()
                    proba = {str(c): round(float(p), 4) for c, p in zip(classes, proba_arr)}
                return {
                    "success": True,
                    "prediction": str(prediction),
                    "probabilities": proba,
                    "model_id": model_id,
                }

            model = artifact["model"]
            scaler = artifact["scaler"]
            features = artifact["columns"]

            # Validate input
            missing_fields = [f for f in features if f not in input_data]
            if missing_fields:
                raise MLError(
                    "MISSING_FEATURES",
                    f"Missing input fields: {missing_fields}",
                    f"Provide values for all features: {features}",
                )

            input_df = pd.DataFrame([{f: input_data[f] for f in features}])

            # Type coercion using metadata
            if meta.get("feature_types"):
                for col, dtype_str in meta["feature_types"].items():
                    if col in input_df.columns:
                        try:
                            if "int" in dtype_str:
                                input_df[col] = input_df[col].astype(int)
                            elif "float" in dtype_str:
                                input_df[col] = input_df[col].astype(float)
                        except (ValueError, TypeError):
                            raise MLError(
                                "TYPE_ERROR",
                                f"Field '{col}' expects a numeric value ({dtype_str}).",
                                f"Enter a valid number for '{col}'.",
                            )

            input_scaled = scaler.transform(input_df)
            prediction = model.predict(input_scaled)[0]

            proba = None
            if hasattr(model, "predict_proba"):
                proba_arr = model.predict_proba(input_scaled)[0]
                classes = meta.get("classes", [str(c) for c in model.classes_])
                proba = {str(c): round(float(p), 4) for c, p in zip(classes, proba_arr)}

            return {
                "success": True,
                "prediction": str(prediction) if not hasattr(prediction, "item") else prediction.item(),
                "probabilities": proba,
                "confidence": round(float(max(proba.values())), 4) if proba else None,
                "model_id": model_id,
                "task": meta.get("task", "unknown"),
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("PREDICTION_ERROR", f"Prediction failed: {str(e)}").to_dict()

    def batch_predict(self, model_id: str, session_id: str, data_engine) -> Dict:
        """Predict on an entire session dataset."""
        try:
            libs = self._load_ml_libs()
            import json

            artifact = self._load_artifact(model_id)
            meta = self.model_factory.get_metadata(model_id)

            if not isinstance(artifact, dict):
                raise MLError("UNSUPPORTED", "Batch predict is not supported for NLP models yet.")

            df = data_engine.load_session_df(session_id)
            features = artifact["columns"]

            missing = [f for f in features if f not in df.columns]
            if missing:
                raise MLError(
                    "MISSING_COLUMNS",
                    f"Dataset is missing columns: {missing}",
                    "Make sure the dataset has the same columns the model was trained on.",
                )

            X = df[features]
            X_scaled = artifact["scaler"].transform(X)
            preds = artifact["model"].predict(X_scaled)

            df["prediction"] = preds
            records = json.loads(df.head(500).to_json(orient="records"))

            return {
                "success": True,
                "message": f"Batch prediction complete — {len(df):,} rows",
                "predictions": records,
                "total_rows": len(df),
                "model_id": model_id,
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("BATCH_ERROR", f"Batch prediction failed: {str(e)}").to_dict()
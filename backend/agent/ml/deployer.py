import json
import time
import pickle
from typing import Dict
from pathlib import Path

from .data_engine import MLError


class Deployer:
    def __init__(self, models_dir: Path, active_models: dict, model_factory):
        self.models_dir = models_dir
        self.active_models = active_models
        self.model_factory = model_factory

    def list_models(self) -> Dict:
        """List all saved models with rich metadata."""
        try:
            models = []
            for f in sorted(self.models_dir.glob("*.joblib"), key=lambda x: x.stat().st_ctime, reverse=True):
                stat = f.stat()
                meta = self.model_factory.get_metadata(f.stem)
                models.append({
                    "model_id": f.stem,
                    "name": f.stem,
                    "size": self._human_size(stat.st_size),
                    "created": time.ctime(stat.st_ctime),
                    # Rich info from metadata
                    "task": meta.get("task", "unknown"),
                    "algorithm": meta.get("algorithm", "unknown"),
                    "target": meta.get("target", "—"),
                    "features": meta.get("features", []),
                    "feature_types": meta.get("feature_types", {}),
                    "classes": meta.get("classes"),
                    "accuracy": meta.get("accuracy"),
                    "rmse": meta.get("rmse"),
                    "r2": meta.get("r2"),
                    "trained_at": meta.get("trained_at"),
                    "dataset_shape": meta.get("dataset_shape"),
                })

            return {"success": True, "models": models, "count": len(models)}
        except Exception as e:
            return MLError("LIST_ERROR", f"Could not list models: {str(e)}").to_dict()

    def delete_model(self, model_id: str) -> Dict:
        """Delete model file + metadata."""
        try:
            model_path = self.models_dir / f"{model_id}.joblib"
            meta_path = self.models_dir / f"{model_id}.json"

            if not model_path.exists():
                raise MLError("MODEL_NOT_FOUND", f"Model '{model_id}' not found.")

            model_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            if model_id in self.active_models:
                del self.active_models[model_id]

            return {"success": True, "message": f"Deleted model '{model_id}'"}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("DELETE_ERROR", str(e)).to_dict()

    def export_model(self, model_id: str, fmt: str = "joblib") -> Dict:
        """Export model as joblib or pickle."""
        try:
            exporters = {
                "joblib": self._export_joblib,
                "pickle": self._export_pickle,
            }
            if fmt not in exporters:
                raise MLError(
                    "UNSUPPORTED_FORMAT",
                    f"Export format '{fmt}' is not supported.",
                    "Use 'joblib' or 'pickle'.",
                )
            return exporters[fmt](model_id)
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("EXPORT_ERROR", str(e)).to_dict()

    def _export_joblib(self, model_id: str) -> Dict:
        path = self.models_dir / f"{model_id}.joblib"
        if not path.exists():
            raise MLError("MODEL_NOT_FOUND", f"Model '{model_id}' not found.")
        return {"success": True, "path": str(path), "format": "joblib"}

    def _export_pickle(self, model_id: str) -> Dict:
        src = self.models_dir / f"{model_id}.joblib"
        if not src.exists():
            raise MLError("MODEL_NOT_FOUND", f"Model '{model_id}' not found.")
        import joblib
        data = joblib.load(src)
        dst = self.models_dir / f"{model_id}.pkl"
        with open(dst, "wb") as f:
            pickle.dump(data, f)
        return {"success": True, "path": str(dst), "format": "pickle"}

    @staticmethod
    def _human_size(size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if abs(size_bytes) < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
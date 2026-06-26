import threading
import uuid
from typing import Dict, List
from pathlib import Path

from .ml.data_engine import DataEngine, MLError
from .ml.model_factory import ModelFactory
from .ml.predictor import Predictor
from .ml.visualizer import Visualizer
from .ml.deployer import Deployer

class MLAgent:
    """
    ML Agent — Zero-code machine learning
    Session-based data flow, background training jobs, structured errors.
    """

    def __init__(self):
        self.models_dir = Path.home() / "Atlas" / "ml_models"
        self.sessions_dir = Path.home() / "Atlas" / "ml_sessions"
        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"MLAgent: Could not create directories — {e}")

        self.active_models: dict = {}
        self.job_status: dict = {}  # job_id → {status, progress, step, result}
        self._ml_libs = None

        # Modular engines
        self.data_engine = DataEngine(self._load_ml_libs, self.sessions_dir)
        self.model_factory = ModelFactory(
            self.models_dir, self.sessions_dir,
            self._load_ml_libs, self.active_models, self.data_engine
        )
        self.predictor = Predictor(
            self.models_dir, self.active_models,
            self._load_ml_libs, self.model_factory
        )
        self.visualizer = Visualizer(self.models_dir, self._load_ml_libs)
        self.deployer = Deployer(self.models_dir, self.active_models, self.model_factory)

    # ──────────────────────────────────────────────
    # Lazy ML lib loader
    # ──────────────────────────────────────────────

    def _load_ml_libs(self):
        if self._ml_libs is None:
            import pandas as pd
            import numpy as np
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler, LabelEncoder
            from sklearn.metrics import accuracy_score, mean_squared_error
            import joblib

            self._ml_libs = {
                "pd": pd, "np": np,
                "train_test_split": train_test_split,
                "StandardScaler": StandardScaler,
                "LabelEncoder": LabelEncoder,
                "accuracy_score": accuracy_score,
                "mean_squared_error": mean_squared_error,
                "joblib": joblib,
            }
        return self._ml_libs

    # ──────────────────────────────────────────────
    # Background job management
    # ──────────────────────────────────────────────

    def _start_job(self, fn, *args, **kwargs) -> str:
        """Run fn in background, return job_id for polling."""
        job_id = str(uuid.uuid4())[:8]
        self.job_status[job_id] = {"status": "running", "progress": 0, "step": "Starting...", "result": None}

        def _run():
            try:
                result = fn(*args, job_status=self.job_status, job_id=job_id, **kwargs)
                self.job_status[job_id].update({"status": "done", "progress": 100, "result": result})
            except Exception as e:
                self.job_status[job_id].update({
                    "status": "error",
                    "result": MLError("JOB_ERROR", str(e)).to_dict()
                })

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return job_id

    def get_job_status(self, job_id: str) -> Dict:
        if job_id not in self.job_status:
            return MLError("JOB_NOT_FOUND", f"No job with id '{job_id}'.").to_dict()
        return {"success": True, "job_id": job_id, **self.job_status[job_id]}

    # ──────────────────────────────────────────────
    # Intent router
    # ──────────────────────────────────────────────

    def handle(self, intent: str, entities: Dict) -> Dict:
        intent_lower = intent.lower()
        e = entities  # alias

        # ── Data operations ──────────────────────
        if intent_lower in ("load_dataset", "ml_load"):
            session_id = e.get("session_id") or str(uuid.uuid4())[:12]
            return self.data_engine.load_dataset(
                e.get("filepath", e.get("path", "")),
                session_id,
                e.get("file_type", "auto"),
            )

        if intent_lower in ("clean_data", "ml_clean"):
            sid = e.get("session_id") or e.get("data", {}).get("session_id", "")
            return self.data_engine.clean_data(sid, e.get("operations"))

        if intent_lower in ("analyze_data", "ml_analyze"):
            sid = e.get("session_id") or e.get("data", {}).get("session_id", "")
            return self.data_engine.analyze_data(sid)

        # ── Training (background) ────────────────
        if intent_lower in ("train_classifier", "ml_classify"):
            job_id = self._start_job(
                self.model_factory.train_classifier,
                e.get("session_id", ""),
                e.get("target", ""),
                e.get("algorithm", "auto"),
            )
            return {"success": True, "job_id": job_id, "message": "Classifier training started."}

        if intent_lower in ("train_regressor", "ml_regress"):
            job_id = self._start_job(
                self.model_factory.train_regressor,
                e.get("session_id", ""),
                e.get("target", ""),
                e.get("algorithm", "auto"),
            )
            return {"success": True, "job_id": job_id, "message": "Regressor training started."}

        if intent_lower in ("train_nlp", "ml_nlp"):
            return self.model_factory.train_nlp_text(
                e.get("texts", []),
                e.get("labels", []),
                e.get("task", "classification"),
            )

        if intent_lower in ("auto_ml", "ml_auto"):
            sid = e.get("session_id") or e.get("data", {}).get("session_id", "")
            job_id = self._start_job(self.model_factory.auto_train, sid, e.get("target", ""), e.get("task_type", "auto"))
            return {"success": True, "job_id": job_id, "message": "AutoML started."}

        # ── Job polling ──────────────────────────
        if intent_lower in ("job_status", "ml_job"):
            return self.get_job_status(e.get("job_id", ""))

        # ── Prediction ───────────────────────────
        if intent_lower in ("predict", "ml_predict"):
            return self.predictor.predict(e.get("model_id", ""), e.get("input", {}))

        if intent_lower in ("batch_predict", "ml_batch"):
            return self.predictor.batch_predict(
                e.get("model_id", ""),
                e.get("session_id", ""),
                self.data_engine,
            )

        if intent_lower in ("model_info", "ml_info"):
            return self.predictor.get_model_info(e.get("model_id", ""))

        # ── Visualization ────────────────────────
        if intent_lower in ("chart_data", "ml_chart"):
            sid = e.get("session_id") or e.get("data", {}).get("session_id", "")
            return self.visualizer.get_chart_data(
                sid, self.data_engine, e.get("plot_type", "histogram"), e.get("columns"),
            )

        if intent_lower in ("feature_importance", "ml_importance"):
            return self.visualizer.feature_importance(
                e.get("model_id", ""),
                self.active_models,
                self.model_factory,
            )

        if intent_lower in ("export_plot", "ml_export_plot"):
            sid = e.get("session_id") or e.get("data", {}).get("session_id", "")
            return self.visualizer.export_plot_png(
                sid, self.data_engine, e.get("plot_type", "histogram"), e.get("columns"),
            )

        # ── Model management ─────────────────────
        if intent_lower in ("list_models", "ml_models"):
            return self.deployer.list_models()

        if intent_lower in ("delete_model", "ml_delete"):
            return self.deployer.delete_model(e.get("model_id", ""))

        if intent_lower in ("export_model", "ml_export"):
            return self.deployer.export_model(e.get("model_id", ""), e.get("format", "joblib"))

        # ── Clustering ────────────────────────────
        if intent_lower in ("train_cluster", "ml_cluster"):
            job_id = self._start_job(
                self.model_factory.train_cluster,
                e.get("session_id", ""),
                e.get("algorithm", "kmeans"),
                e.get("n_clusters", 3),
                e.get("eps", 0.5),
                e.get("min_samples", 5),
            )
            return {"success": True, "job_id": job_id, "message": "Clustering started."}

        # ── Dimensionality Reduction ───────────────
        if intent_lower in ("reduce_dim", "ml_dimreduce"):
            job_id = self._start_job(
                self.model_factory.reduce_dim,
                e.get("session_id", ""),
                e.get("algorithm", "pca"),
                e.get("n_components", 2),
            )
            return {"success": True, "job_id": job_id, "message": "Dimensionality reduction started."}

        # ── Neural Network (MLP) ───────────────────
        if intent_lower in ("train_mlp", "ml_mlp"):
            job_id = self._start_job(
                self.model_factory.train_mlp,
                e.get("session_id", ""),
                e.get("target", ""),
                e.get("task_type", "classification"),
                e.get("hidden_layers", "100,50"),
                e.get("max_iter", 500),
            )
            return {"success": True, "job_id": job_id, "message": "MLP training started."}

        # ── Hyperparameter Tuning ──────────────────
        if intent_lower in ("tune_hyperparams", "ml_tune"):
            job_id = self._start_job(
                self.model_factory.tune_hyperparams,
                e.get("session_id", ""),
                e.get("target", ""),
                e.get("task_type", "classification"),
                e.get("algorithm", "random_forest"),
                e.get("param_grid"),
                e.get("cv", 5),
                e.get("scoring", "accuracy"),
            )
            return {"success": True, "job_id": job_id, "message": "Hyperparameter tuning started."}

        # ── K-Fold Cross Validation ────────────────
        if intent_lower in ("train_kfold", "ml_kfold"):
            job_id = self._start_job(
                self.model_factory.train_kfold,
                e.get("session_id", ""),
                e.get("target", ""),
                e.get("task_type", "classification"),
                e.get("algorithm", "random_forest"),
                e.get("n_splits", 5),
            )
            return {"success": True, "job_id": job_id, "message": "K-Fold CV started."}

        # ── Feature Engineering ────────────────────
        if intent_lower in ("feature_engineer", "ml_feateng"):
            return self.model_factory.feature_engineering(
                e.get("session_id", ""),
                e.get("operations"),
            )

        # ── Confusion Matrix ───────────────────────
        if intent_lower in ("confusion_matrix", "ml_cm"):
            return self.visualizer.confusion_matrix_data(
                e.get("model_id", ""),
                e.get("session_id", ""),
                self.data_engine,
            )

        # ── ROC Curve ──────────────────────────────
        if intent_lower in ("roc_curve", "ml_roc"):
            return self.visualizer.roc_curve_data(
                e.get("model_id", ""),
                e.get("session_id", ""),
                self.data_engine,
            )

        # ── Elbow Plot ─────────────────────────────
        if intent_lower in ("elbow_plot", "ml_elbow"):
            return self.visualizer.elbow_plot_data(
                e.get("session_id", ""),
                self.data_engine,
                e.get("max_k", 10),
            )

        return MLError(
            "UNKNOWN_INTENT",
            f"MLAgent cannot handle intent: '{intent}'",
            f"Supported intents: {self.get_capabilities()}",
        ).to_dict()

    def get_capabilities(self) -> List[str]:
        return [
            "load_dataset", "clean_data", "analyze_data",
            "train_classifier", "train_regressor", "train_nlp", "auto_ml",
            "train_cluster", "reduce_dim", "train_mlp", "tune_hyperparams",
            "train_kfold", "feature_engineer",
            "confusion_matrix", "roc_curve", "elbow_plot",
            "job_status",
            "predict", "batch_predict", "model_info",
            "chart_data", "feature_importance", "export_plot",
            "list_models", "delete_model", "export_model",
        ]


# Singleton
ml_agent = MLAgent()
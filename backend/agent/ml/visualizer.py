import json
import time
from typing import Dict, List, Callable, Optional
from pathlib import Path

from .data_engine import MLError


class Visualizer:
    def __init__(self, models_dir: Path, ml_libs_loader: Callable):
        self.models_dir = models_dir
        self._load_ml_libs = ml_libs_loader

    # ──────────────────────────────────────────────
    # Primary: return data for frontend charts
    # ──────────────────────────────────────────────

    def get_chart_data(self, session_id: str, data_engine,
                       plot_type: str = "histogram",
                       columns: Optional[List[str]] = None) -> Dict:
        """
        Return raw chart data (not an image) so the frontend can render
        interactive charts with Recharts / Plotly.
        Supported types: histogram, scatter, correlation, boxplot, bar
        """
        try:
            libs = self._load_ml_libs()
            np = libs["np"]

            df = data_engine.load_session_df(session_id)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

            if plot_type == "histogram":
                cols = columns or numeric_cols[:4]
                if not cols:
                    raise MLError("NO_NUMERIC", "No numeric columns available for histogram.",
                                  "Encode categorical columns first.")
                result = {}
                for col in cols:
                    if col not in df.columns:
                        continue
                    s = df[col].dropna()
                    counts, edges = np.histogram(s, bins=20)
                    result[col] = {
                        "bins": [round(float(e), 4) for e in edges[:-1]],
                        "counts": counts.tolist(),
                    }
                return {"success": True, "plot_type": "histogram", "data": result}

            elif plot_type == "scatter":
                cols = columns or numeric_cols[:2]
                if len(cols) < 2:
                    raise MLError("NOT_ENOUGH_COLS", "Scatter plot needs at least 2 numeric columns.")
                x_col, y_col = cols[0], cols[1]
                sample = df[[x_col, y_col]].dropna().head(1000)
                return {
                    "success": True,
                    "plot_type": "scatter",
                    "x_label": x_col,
                    "y_label": y_col,
                    "data": [{"x": float(r[x_col]), "y": float(r[y_col])}
                             for _, r in sample.iterrows()],
                }

            elif plot_type == "correlation":
                cols = columns or numeric_cols[:15]
                if len(cols) < 2:
                    raise MLError("NOT_ENOUGH_COLS", "Correlation needs at least 2 numeric columns.")
                corr = df[cols].corr()
                matrix = []
                for row_col in cols:
                    for col_col in cols:
                        val = corr.loc[row_col, col_col]
                        matrix.append({
                            "row": row_col,
                            "col": col_col,
                            "value": round(float(val), 4) if not np.isnan(val) else 0,
                        })
                return {"success": True, "plot_type": "correlation",
                        "columns": cols, "data": matrix}

            elif plot_type == "boxplot":
                cols = columns or numeric_cols[:6]
                if not cols:
                    raise MLError("NO_NUMERIC", "No numeric columns for boxplot.")
                result = {}
                for col in cols:
                    s = df[col].dropna()
                    result[col] = {
                        "min": round(float(s.min()), 4),
                        "q1": round(float(s.quantile(0.25)), 4),
                        "median": round(float(s.median()), 4),
                        "q3": round(float(s.quantile(0.75)), 4),
                        "max": round(float(s.max()), 4),
                        "outliers": [round(float(v), 4) for v in
                                     s[(s < s.quantile(0.25) - 1.5 * (s.quantile(0.75) - s.quantile(0.25))) |
                                       (s > s.quantile(0.75) + 1.5 * (s.quantile(0.75) - s.quantile(0.25)))].head(50)],
                    }
                return {"success": True, "plot_type": "boxplot", "data": result}

            elif plot_type == "bar":
                cols = columns or categorical_cols[:1]
                if not cols:
                    raise MLError("NO_CATEGORICAL", "No categorical columns for bar chart.")
                col = cols[0]
                vc = df[col].value_counts().head(20)
                return {
                    "success": True,
                    "plot_type": "bar",
                    "label": col,
                    "data": [{"name": str(k), "count": int(v)} for k, v in vc.items()],
                }

            else:
                raise MLError("UNKNOWN_PLOT", f"Plot type '{plot_type}' not supported.",
                              "Use: histogram, scatter, correlation, boxplot, bar")

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("CHART_ERROR", f"Chart generation failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Feature importance (from trained model)
    # ──────────────────────────────────────────────

    def feature_importance(self, model_id: str, active_models: dict,
                           model_factory) -> Dict:
        try:
            artifact = active_models.get(model_id)
            if artifact is None:
                libs = self._load_ml_libs()
                model_path = self.models_dir / f"{model_id}.joblib"
                if not model_path.exists():
                    raise MLError("MODEL_NOT_FOUND", f"Model '{model_id}' not found.")
                artifact = libs["joblib"].load(model_path)

            if not isinstance(artifact, dict) or "model" not in artifact:
                raise MLError("UNSUPPORTED", "Feature importance is only available for tabular models.")

            model = artifact["model"]
            features = artifact["columns"]

            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_.tolist()
            elif hasattr(model, "coef_"):
                import numpy as np
                coef = model.coef_
                if coef.ndim > 1:
                    importances = np.abs(coef).mean(axis=0).tolist()
                else:
                    importances = [abs(c) for c in coef.tolist()]
            else:
                raise MLError(
                    "NO_IMPORTANCE",
                    f"Algorithm does not expose feature importances.",
                    "Use Random Forest or Gradient Boosting for feature importance.",
                )

            pairs = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
            return {
                "success": True,
                "model_id": model_id,
                "data": [{"feature": f, "importance": round(imp, 6)} for f, imp in pairs],
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("IMPORTANCE_ERROR", f"Failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Confusion Matrix Data
    # ──────────────────────────────────────────────

    def confusion_matrix_data(self, model_id: str, session_id: str, data_engine) -> Dict:
        """Generate confusion matrix JSON for frontend heatmap."""
        try:
            import json
            libs = self._load_ml_libs()
            from sklearn.metrics import confusion_matrix
            model_path = self.models_dir / f"{model_id}.joblib"
            if not model_path.exists():
                raise MLError("MODEL_NOT_FOUND", f"Model '{model_id}' not found.")
            artifact = libs["joblib"].load(model_path)
            if not isinstance(artifact, dict):
                raise MLError("UNSUPPORTED", "Confusion matrix requires a tabular model.")
            model = artifact["model"]
            scaler = artifact["scaler"]
            features = artifact["columns"]
            df = data_engine.load_session_df(session_id)
            missing = [f for f in features if f not in df.columns]
            if missing:
                raise MLError("MISSING_FEATURES", f"Missing columns: {missing}")
            meta_path = self.models_dir / f"{model_id}.json"
            meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
            target = meta.get("target", "")
            if target not in df.columns:
                raise MLError("TARGET_MISSING", f"Target column '{target}' not found in dataset.")
            X = df[features]
            y_true = df[target]
            X_s = scaler.transform(X)
            y_pred = model.predict(X_s)
            cm = confusion_matrix(y_true, y_pred).tolist()
            classes = meta.get("classes", sorted(set(str(c) for c in y_true.unique())))
            return {"success": True, "matrix": cm, "labels": classes,
                    "model_id": model_id, "target": target}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("CM_ERROR", f"Confusion matrix failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # ROC Curve Data
    # ──────────────────────────────────────────────

    def roc_curve_data(self, model_id: str, session_id: str, data_engine) -> Dict:
        """Generate ROC curve data for binary classification."""
        try:
            import json
            libs = self._load_ml_libs()
            from sklearn.metrics import roc_curve, auc
            model_path = self.models_dir / f"{model_id}.joblib"
            if not model_path.exists():
                raise MLError("MODEL_NOT_FOUND", f"Model '{model_id}' not found.")
            artifact = libs["joblib"].load(model_path)
            if not isinstance(artifact, dict):
                raise MLError("UNSUPPORTED", "ROC requires a tabular model with predict_proba.")
            model = artifact["model"]
            scaler = artifact["scaler"]
            features = artifact["columns"]
            if not hasattr(model, "predict_proba"):
                raise MLError("NO_PROBA", "This model does not support probability predictions.")
            meta_path = self.models_dir / f"{model_id}.json"
            meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
            target = meta.get("target", "")
            df = data_engine.load_session_df(session_id)
            if target not in df.columns:
                raise MLError("TARGET_MISSING", f"Target column '{target}' not found.")
            X = df[features]
            y_true = df[target]
            X_s = scaler.transform(X)
            y_score = model.predict_proba(X_s)[:, 1]
            fpr, tpr, thresholds = roc_curve(y_true, y_score, pos_label=meta.get("classes", [1])[1] if len(meta.get("classes", [])) > 1 else 1)
            roc_auc = float(auc(fpr, tpr))
            return {"success": True, "fpr": [round(float(x), 4) for x in fpr],
                    "tpr": [round(float(x), 4) for x in tpr],
                    "auc": round(roc_auc, 4), "model_id": model_id, "target": target}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("ROC_ERROR", f"ROC curve failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Elbow Plot Data (for K-Means)
    # ──────────────────────────────────────────────

    def elbow_plot_data(self, session_id: str, data_engine, max_k: int = 10) -> Dict:
        """Compute inertia for k=1..max_k for elbow method visualization."""
        try:
            libs = self._load_ml_libs()
            from sklearn.cluster import KMeans
            df = data_engine.load_session_df(session_id)
            feature_cols = df.select_dtypes(include=[libs["np"].number]).columns.tolist()
            if not feature_cols:
                raise MLError("NO_NUMERIC", "No numeric columns.")
            X = df[feature_cols].dropna()
            scaler = libs["StandardScaler"]()
            X_s = scaler.fit_transform(X)
            inertias = []
            ks = list(range(1, min(max_k + 1, len(X))))
            for k in ks:
                km = KMeans(n_clusters=k, random_state=42, n_init=10)
                km.fit(X_s)
                inertias.append(float(km.inertia_))
            return {"success": True, "plot_type": "elbow",
                    "data": [{"k": k, "inertia": inertias[i]} for i, k in enumerate(ks)]}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("ELBOW_ERROR", f"Elbow plot failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Fallback: generate PNG (for export/download)
    # ──────────────────────────────────────────────

    def export_plot_png(self, session_id: str, data_engine,
                        plot_type: str = "histogram",
                        columns: Optional[List[str]] = None) -> Dict:
        """Generate a matplotlib PNG and return base64 — use only for download."""
        try:
            libs = self._load_ml_libs()
            np = libs["np"]
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import seaborn as sns
            import base64
            import io

            df = data_engine.load_session_df(session_id)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cols = columns or numeric_cols[:4]

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.set_style("darkgrid")

            if plot_type == "histogram":
                df[cols].hist(ax=ax, bins=20, edgecolor="white")
            elif plot_type == "scatter" and len(cols) >= 2:
                ax.scatter(df[cols[0]], df[cols[1]], alpha=0.6)
                ax.set_xlabel(cols[0])
                ax.set_ylabel(cols[1])
            elif plot_type == "correlation":
                sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", ax=ax, cmap="coolwarm")
            elif plot_type == "boxplot":
                df[cols].boxplot(ax=ax)

            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            plt.close()
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode("utf-8")

            return {
                "success": True,
                "plot_type": plot_type,
                "plot_base64": b64,
                "format": "png",
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("EXPORT_ERROR", f"PNG export failed: {str(e)}").to_dict()
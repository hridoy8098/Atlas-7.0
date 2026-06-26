import json
import time
from datetime import datetime
from typing import Dict, List, Callable
from pathlib import Path

from .data_engine import MLError


class ModelFactory:
    def __init__(self, models_dir: Path, sessions_dir: Path, ml_libs_loader: Callable,
                 active_models: dict, data_engine):
        self.models_dir = models_dir
        self.sessions_dir = sessions_dir
        self._load_ml_libs = ml_libs_loader
        self.active_models = active_models
        self.data_engine = data_engine

    # ──────────────────────────────────────────────
    # Metadata helpers
    # ──────────────────────────────────────────────

    def _save_metadata(self, model_id: str, meta: dict):
        with open(self.models_dir / f"{model_id}.json", "w") as f:
            json.dump(meta, f, indent=2)

    def get_metadata(self, model_id: str) -> Dict:
        meta_path = self.models_dir / f"{model_id}.json"
        if meta_path.exists():
            with open(meta_path) as f:
                return json.load(f)
        return {}

    def _prepare_data(self, session_id: str, target: str):
        """Load session data and split into X / y. Returns (X, y, df, libs)."""
        libs = self._load_ml_libs()
        pd = libs["pd"]

        df = self.data_engine.load_session_df(session_id)

        if target not in df.columns:
            raise MLError(
                "TARGET_NOT_FOUND",
                f"Target column '{target}' not found in dataset.",
                f"Available columns: {list(df.columns)}",
            )

        # Check all features are numeric
        feature_cols = [c for c in df.columns if c != target]
        non_numeric = [c for c in feature_cols if df[c].dtype == "object"]
        if non_numeric:
            raise MLError(
                "NON_NUMERIC_FEATURES",
                f"Columns {non_numeric} contain text and cannot be used as features.",
                "Go to the DATA tab and encode these columns first.",
            )

        # Check for missing values
        missing_cols = [c for c in feature_cols if df[c].isna().any()]
        if missing_cols:
            raise MLError(
                "MISSING_VALUES",
                f"Columns {missing_cols} have missing values.",
                "Go to the DATA tab and fill or drop missing values first.",
            )

        X = df[feature_cols]
        y = df[target]
        return X, y, df, libs

    # ──────────────────────────────────────────────
    # Classification
    # ──────────────────────────────────────────────

    def train_classifier(self, session_id: str, target: str, algorithm: str = "auto",
                         job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})

        try:
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC
            from sklearn.naive_bayes import GaussianNB
            from sklearn.metrics import classification_report

            _progress(5, "Loading dataset...")
            X, y, df, libs = self._prepare_data(session_id, target)

            _progress(15, "Splitting data...")
            X_train, X_test, y_train, y_test = libs["train_test_split"](
                X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() < 20 else None
            )

            _progress(25, "Scaling features...")
            scaler = libs["StandardScaler"]()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            candidates = {
                "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "logistic": LogisticRegression(max_iter=1000, random_state=42),
                "gradient_boost": GradientBoostingClassifier(random_state=42),
                "svm": SVC(probability=True, random_state=42),
                "naive_bayes": GaussianNB(),
            }

            if algorithm != "auto":
                if algorithm not in candidates:
                    raise MLError(
                        "UNKNOWN_ALGORITHM",
                        f"Algorithm '{algorithm}' not recognized.",
                        f"Available: {list(candidates.keys())} or 'auto'.",
                    )
                _progress(50, f"Training {algorithm}...")
                model = candidates[algorithm]
                model.fit(X_train_s, y_train)
                chosen = algorithm
            else:
                best_score, best_model, chosen = -1, None, ""
                total = len(candidates)
                for i, (name, m) in enumerate(candidates.items()):
                    _progress(30 + int(40 * i / total), f"Trying {name}...")
                    m.fit(X_train_s, y_train)
                    score = m.score(X_test_s, y_test)
                    if score > best_score:
                        best_score, best_model, chosen = score, m, name
                if best_model is None:
                    raise MLError("TRAINING_FAILED", "All candidate models failed to train.")
                model = best_model

            _progress(80, "Evaluating model...")
            preds = model.predict(X_test_s)
            accuracy = float(libs["accuracy_score"](y_test, preds))
            report = classification_report(y_test, preds, output_dict=True, zero_division=0)

            model_id = f"classifier_{target}_{chosen}_{int(time.time())}"
            model_path = self.models_dir / f"{model_id}.joblib"

            _progress(90, "Saving model...")
            artifact = {"model": model, "scaler": scaler, "columns": list(X.columns)}
            libs["joblib"].dump(artifact, model_path)
            self.active_models[model_id] = artifact

            metadata = {
                "model_id": model_id,
                "task": "classification",
                "algorithm": chosen,
                "target": target,
                "features": list(X.columns),
                "feature_types": {c: str(df[c].dtype) for c in X.columns},
                "classes": sorted([str(c) for c in y.unique()]),
                "accuracy": round(accuracy, 4),
                "report": report,
                "trained_at": datetime.now().isoformat(),
                "dataset_shape": list(df.shape),
                "model_path": str(model_path),
            }
            self._save_metadata(model_id, metadata)
            _progress(100, "Done!")

            return {
                "success": True,
                "message": f"Classifier trained — {chosen}",
                **{k: metadata[k] for k in ["model_id", "task", "algorithm", "target",
                                             "features", "classes", "accuracy", "trained_at"]},
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("TRAINING_ERROR", f"Training failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Regression
    # ──────────────────────────────────────────────

    def train_regressor(self, session_id: str, target: str, algorithm: str = "auto",
                        job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})

        try:
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.linear_model import LinearRegression, Ridge
            from sklearn.svm import SVR

            _progress(5, "Loading dataset...")
            X, y, df, libs = self._prepare_data(session_id, target)

            _progress(15, "Splitting data...")
            X_train, X_test, y_train, y_test = libs["train_test_split"](
                X, y, test_size=0.2, random_state=42
            )

            _progress(25, "Scaling features...")
            scaler = libs["StandardScaler"]()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            candidates = {
                "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
                "linear": LinearRegression(),
                "ridge": Ridge(),
                "gradient_boost": GradientBoostingRegressor(random_state=42),
                "svr": SVR(),
            }

            if algorithm != "auto":
                if algorithm not in candidates:
                    raise MLError(
                        "UNKNOWN_ALGORITHM",
                        f"Algorithm '{algorithm}' not recognized.",
                        f"Available: {list(candidates.keys())} or 'auto'.",
                    )
                _progress(50, f"Training {algorithm}...")
                model = candidates[algorithm]
                model.fit(X_train_s, y_train)
                chosen = algorithm
            else:
                best_mse, best_model, chosen = float("inf"), None, ""
                total = len(candidates)
                for i, (name, m) in enumerate(candidates.items()):
                    _progress(30 + int(40 * i / total), f"Trying {name}...")
                    m.fit(X_train_s, y_train)
                    mse = float(libs["mean_squared_error"](y_test, m.predict(X_test_s)))
                    if mse < best_mse:
                        best_mse, best_model, chosen = mse, m, name
                if best_model is None:
                    raise MLError("TRAINING_FAILED", "All candidate models failed to train.")
                model = best_model

            _progress(80, "Evaluating model...")
            preds = model.predict(X_test_s)
            mse = float(libs["mean_squared_error"](y_test, preds))
            rmse = mse ** 0.5
            import numpy as np
            ss_res = np.sum((y_test.values - preds) ** 2)
            ss_tot = np.sum((y_test.values - y_test.mean()) ** 2)
            r2 = float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0

            model_id = f"regressor_{target}_{chosen}_{int(time.time())}"
            model_path = self.models_dir / f"{model_id}.joblib"

            _progress(90, "Saving model...")
            artifact = {"model": model, "scaler": scaler, "columns": list(X.columns)}
            libs["joblib"].dump(artifact, model_path)
            self.active_models[model_id] = artifact

            metadata = {
                "model_id": model_id,
                "task": "regression",
                "algorithm": chosen,
                "target": target,
                "features": list(X.columns),
                "feature_types": {c: str(df[c].dtype) for c in X.columns},
                "rmse": round(rmse, 4),
                "r2": round(r2, 4),
                "trained_at": datetime.now().isoformat(),
                "dataset_shape": list(df.shape),
                "model_path": str(model_path),
            }
            self._save_metadata(model_id, metadata)
            _progress(100, "Done!")

            return {
                "success": True,
                "message": f"Regressor trained — {chosen}",
                **{k: metadata[k] for k in ["model_id", "task", "algorithm", "target",
                                             "features", "rmse", "r2", "trained_at"]},
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("TRAINING_ERROR", f"Training failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # NLP
    # ──────────────────────────────────────────────

    def train_nlp_text(self, texts: List[str], labels: List[str], task: str = "classification") -> Dict:
        try:
            if not texts or not labels:
                raise MLError("EMPTY_INPUT", "No texts or labels provided.")
            if len(texts) != len(labels):
                raise MLError("LENGTH_MISMATCH", f"texts ({len(texts)}) and labels ({len(labels)}) must have the same length.")

            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.pipeline import Pipeline

            pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("classifier", MultinomialNB()),
            ])
            pipeline.fit(texts, labels)

            model_id = f"nlp_{task}_{int(time.time())}"
            model_path = self.models_dir / f"{model_id}.joblib"
            self._load_ml_libs()["joblib"].dump(pipeline, model_path)
            self.active_models[model_id] = pipeline

            metadata = {
                "model_id": model_id,
                "task": f"nlp_{task}",
                "algorithm": "tfidf_naive_bayes",
                "features": ["text"],
                "feature_types": {"text": "object"},
                "classes": sorted(list(set(labels))),
                "samples": len(texts),
                "trained_at": datetime.now().isoformat(),
                "model_path": str(model_path),
            }
            self._save_metadata(model_id, metadata)

            return {
                "success": True,
                "message": f"NLP model trained — {task}",
                "model_id": model_id,
                "classes": metadata["classes"],
                "samples": len(texts),
            }
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("NLP_ERROR", f"NLP training failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # AutoML
    # ──────────────────────────────────────────────

    def auto_ml(self, session_id: str, target: str, task_type: str = "auto",
                job_status: dict = None, job_id: str = None) -> Dict:
        try:
            def _progress(pct, msg):
                if job_status and job_id:
                    job_status[job_id].update({"progress": pct, "step": msg})

            _progress(5, "Detecting task type...")
            df = self.data_engine.load_session_df(session_id)

            if target not in df.columns:
                raise MLError("TARGET_NOT_FOUND", f"Target column '{target}' not found.",
                              f"Available: {list(df.columns)}")

            if task_type == "auto":
                y = df[target]
                if y.dtype == "object" or y.nunique() <= 20:
                    task_type = "classification"
                else:
                    task_type = "regression"

            _progress(10, f"Running AutoML — {task_type}...")

            if task_type == "classification":
                return self.train_classifier(session_id, target, "auto", job_status, job_id)
            else:
                return self.train_regressor(session_id, target, "auto", job_status, job_id)

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("AUTOML_ERROR", f"AutoML failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Clustering (K-Means, DBSCAN)
    # ──────────────────────────────────────────────

    def train_cluster(self, session_id: str, algorithm: str = "kmeans",
                      n_clusters: int = 3, eps: float = 0.5, min_samples: int = 5,
                      job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})
        try:
            libs = self._load_ml_libs()
            _progress(10, "Loading data...")
            df = self.data_engine.load_session_df(session_id)
            feature_cols = df.select_dtypes(include=[libs["np"].number]).columns.tolist()
            if not feature_cols:
                raise MLError("NO_NUMERIC", "No numeric columns for clustering.")
            X = df[feature_cols].dropna()
            scaler = libs["StandardScaler"]()
            X_s = scaler.fit_transform(X)
            _progress(40, f"Running {algorithm}...")
            if algorithm == "kmeans":
                from sklearn.cluster import KMeans
                model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = model.fit_predict(X_s)
                inertia = float(model.inertia_)
                result = {"labels": [int(l) for l in labels], "inertia": inertia,
                          "n_clusters": n_clusters, "algorithm": "kmeans"}
            elif algorithm == "dbscan":
                from sklearn.cluster import DBSCAN
                model = DBSCAN(eps=eps, min_samples=min_samples)
                labels = model.fit_predict(X_s)
                n_noise = int((labels == -1).sum())
                result = {"labels": [int(l) for l in labels], "n_clusters": len(set(labels) - {-1}),
                          "n_noise": n_noise, "algorithm": "dbscan"}
            elif algorithm == "meanshift":
                from sklearn.cluster import MeanShift
                model = MeanShift()
                labels = model.fit_predict(X_s)
                result = {"labels": [int(l) for l in labels], "n_clusters": len(set(labels)),
                          "algorithm": "meanshift"}
            elif algorithm == "agglomerative":
                from sklearn.cluster import AgglomerativeClustering
                model = AgglomerativeClustering(n_clusters=n_clusters)
                labels = model.fit_predict(X_s)
                result = {"labels": [int(l) for l in labels], "n_clusters": n_clusters,
                          "algorithm": "agglomerative"}
            else:
                raise MLError("UNKNOWN_ALGO", f"Unknown clustering algorithm: {algorithm}",
                              "Use: kmeans, dbscan, meanshift, agglomerative")
            _progress(80, "Computing cluster centers...")
            centers = []
            for cid in set(labels):
                if cid == -1:
                    continue
                mask = [l == cid for l in labels]
                center = X_s[mask].mean(axis=0).tolist()
                centers.append({"cluster": int(cid), "size": int(sum(mask)), "center": [round(v, 4) for v in center]})
            _progress(100, "Done!")
            return {"success": True, "message": f"Clustering complete — {result['n_clusters']} clusters",
                    **result, "cluster_centers": centers, "features": feature_cols}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("CLUSTER_ERROR", f"Clustering failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Dimensionality Reduction (PCA, t-SNE)
    # ──────────────────────────────────────────────

    def reduce_dim(self, session_id: str, algorithm: str = "pca",
                   n_components: int = 2, job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})
        try:
            libs = self._load_ml_libs()
            _progress(20, "Loading data...")
            df = self.data_engine.load_session_df(session_id)
            feature_cols = df.select_dtypes(include=[libs["np"].number]).columns.tolist()
            if not feature_cols:
                raise MLError("NO_NUMERIC", "No numeric columns for dimensionality reduction.")
            X = df[feature_cols].dropna()
            scaler = libs["StandardScaler"]()
            X_s = scaler.fit_transform(X)
            n_comp = min(n_components, min(X_s.shape) - 1)
            _progress(50, f"Running {algorithm}...")
            if algorithm == "pca":
                from sklearn.decomposition import PCA
                model = PCA(n_components=n_comp)
                X_r = model.fit_transform(X_s)
                var_ratio = model.explained_variance_ratio_.tolist()
                result = {"algorithm": "pca", "components": X_r.tolist(),
                          "explained_variance_ratio": [round(v, 4) for v in var_ratio],
                          "cumulative_variance": round(float(sum(var_ratio)), 4)}
            elif algorithm == "tsne":
                from sklearn.manifold import TSNE
                model = TSNE(n_components=n_comp, random_state=42, perplexity=min(30, len(X) - 1))
                X_r = model.fit_transform(X_s)
                result = {"algorithm": "tsne", "components": X_r.tolist()}
            else:
                raise MLError("UNKNOWN_ALGO", f"Unknown algorithm: {algorithm}", "Use: pca, tsne")
            _progress(100, "Done!")
            return {"success": True, "message": f"{algorithm.upper()} done — {n_comp} components",
                    **result, "features": feature_cols[:n_comp], "n_components": n_comp}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("DIMRED_ERROR", f"Dimensionality reduction failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Neural Network (MLP)
    # ──────────────────────────────────────────────

    def train_mlp(self, session_id: str, target: str, task_type: str = "classification",
                  hidden_layers: str = "100,50", max_iter: int = 500,
                  job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})
        try:
            from sklearn.neural_network import MLPClassifier, MLPRegressor
            _progress(10, "Loading data...")
            X, y, df, libs = self._prepare_data(session_id, target)
            _progress(25, "Splitting data...")
            X_train, X_test, y_train, y_test = libs["train_test_split"](X, y, test_size=0.2, random_state=42)
            _progress(35, "Scaling...")
            scaler = libs["StandardScaler"]()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)
            hidden = tuple(int(x.strip()) for x in hidden_layers.split(","))
            _progress(50, f"Training MLP (layers: {hidden_layers})...")
            ModelClass = MLPClassifier if task_type == "classification" else MLPRegressor
            model = ModelClass(hidden_layer_sizes=hidden, max_iter=max_iter, random_state=42, early_stopping=True)
            model.fit(X_train_s, y_train)
            _progress(80, "Evaluating...")
            preds = model.predict(X_test_s)
            score = float(libs["accuracy_score"](y_test, preds)) if task_type == "classification" else float(-libs["mean_squared_error"](y_test, preds))
            loss = float(model.loss_) if hasattr(model, "loss_") else 0
            model_id = f"mlp_{target}_{int(time.time())}"
            libs["joblib"].dump({"model": model, "scaler": scaler, "columns": list(X.columns)}, self.models_dir / f"{model_id}.joblib")
            self.active_models[model_id] = {"model": model, "scaler": scaler, "columns": list(X.columns)}
            meta = {"model_id": model_id, "task": task_type, "algorithm": "mlp", "target": target,
                    "features": list(X.columns), "hidden_layers": hidden_layers, "max_iter": max_iter,
                    "layers": list(model.hidden_layer_sizes), "score": round(score, 4), "loss": round(loss, 4),
                    "trained_at": datetime.now().isoformat(), "dataset_shape": list(df.shape)}
            self._save_metadata(model_id, meta)
            _progress(100, "Done!")
            return {"success": True, "message": f"MLP trained — loss: {loss:.4f}",
                    "model_id": model_id, "algorithm": "mlp", "task": task_type,
                    "score": round(score, 4), "loss": round(loss, 4), "target": target}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("MLP_ERROR", f"MLP training failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Hyperparameter Tuning (GridSearchCV)
    # ──────────────────────────────────────────────

    def tune_hyperparams(self, session_id: str, target: str, task_type: str = "classification",
                         algorithm: str = "random_forest", param_grid: dict = None,
                         cv: int = 5, scoring: str = "accuracy",
                         job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})
        try:
            from sklearn.model_selection import GridSearchCV
            _progress(10, "Loading data...")
            X, y, df, libs = self._prepare_data(session_id, target)
            _progress(20, "Scaling...")
            scaler = libs["StandardScaler"]()
            X_s = scaler.fit_transform(X)
            if param_grid is None:
                param_grid = {"n_estimators": [10, 50, 100], "max_depth": [None, 10, 20]}
            base_models = {
                "random_forest": __import__("sklearn.ensemble", fromlist=["RandomForestClassifier"]).RandomForestClassifier(random_state=42),
                "svm": __import__("sklearn.svm", fromlist=["SVC"]).SVC(random_state=42),
                "logistic": __import__("sklearn.linear_model", fromlist=["LogisticRegression"]).LogisticRegression(max_iter=1000, random_state=42),
                "gradient_boost": __import__("sklearn.ensemble", fromlist=["GradientBoostingClassifier"]).GradientBoostingClassifier(random_state=42),
            }
            base_model = base_models.get(algorithm)
            if base_model is None:
                raise MLError("UNKNOWN_ALGO", f"Unknown algorithm: {algorithm}",
                              "Use: random_forest, svm, logistic, gradient_boost")
            _progress(40, f"GridSearchCV with {cv}-fold...")
            gs = GridSearchCV(base_model, param_grid, cv=cv, scoring=scoring, n_jobs=-1, verbose=0)
            gs.fit(X_s, y)
            _progress(85, "Evaluating best model...")
            model_id = f"tuned_{algorithm}_{target}_{int(time.time())}"
            best_model = gs.best_estimator_
            artifact = {"model": best_model, "scaler": scaler, "columns": list(X.columns)}
            libs["joblib"].dump(artifact, self.models_dir / f"{model_id}.joblib")
            self.active_models[model_id] = artifact
            meta = {"model_id": model_id, "task": task_type, "algorithm": algorithm, "target": target,
                    "features": list(X.columns), "best_params": gs.best_params_, "best_score": round(float(gs.best_score_), 4),
                    "cv": cv, "scoring": scoring, "trained_at": datetime.now().isoformat(), "dataset_shape": list(df.shape)}
            self._save_metadata(model_id, meta)
            _progress(100, "Done!")
            return {"success": True, "message": f"Tuning complete — best: {gs.best_score_:.4f}",
                    "model_id": model_id, "best_params": gs.best_params_, "best_score": round(float(gs.best_score_), 4),
                    "cv": cv, "algorithm": algorithm, "target": target}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("TUNE_ERROR", f"Hyperparameter tuning failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # K-Fold Cross Validation
    # ──────────────────────────────────────────────

    def train_kfold(self, session_id: str, target: str, task_type: str = "classification",
                    algorithm: str = "random_forest", n_splits: int = 5,
                    job_status: dict = None, job_id: str = None) -> Dict:
        def _progress(pct, msg):
            if job_status and job_id:
                job_status[job_id].update({"progress": pct, "step": msg})
        try:
            from sklearn.model_selection import cross_val_score, KFold
            _progress(10, "Loading data...")
            X, y, df, libs = self._prepare_data(session_id, target)
            _progress(25, "Scaling...")
            scaler = libs["StandardScaler"]()
            X_s = scaler.fit_transform(X)
            algos = {
                "random_forest": __import__("sklearn.ensemble", fromlist=["RandomForestClassifier"]).RandomForestClassifier(n_estimators=50, random_state=42),
                "svm": __import__("sklearn.svm", fromlist=["SVC"]).SVC(random_state=42),
                "logistic": __import__("sklearn.linear_model", fromlist=["LogisticRegression"]).LogisticRegression(max_iter=1000, random_state=42),
                "gradient_boost": __import__("sklearn.ensemble", fromlist=["GradientBoostingClassifier"]).GradientBoostingClassifier(random_state=42),
            }
            if task_type == "regression":
                algos = {k: __import__("sklearn.ensemble", fromlist=["RandomForestRegressor"]).RandomForestRegressor(n_estimators=50, random_state=42) for k in algos}
            model = algos.get(algorithm)
            if model is None:
                raise MLError("UNKNOWN_ALGO", f"Unknown algorithm: {algorithm}")
            _progress(50, f"{n_splits}-fold CV...")
            kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
            scoring = "accuracy" if task_type == "classification" else "neg_mean_squared_error"
            scores = cross_val_score(model, X_s, y, cv=kf, scoring=scoring)
            scores = scores.tolist()
            _progress(100, "Done!")
            return {"success": True, "message": f"{n_splits}-fold CV complete",
                    "scores": [round(float(s), 4) for s in scores],
                    "mean_score": round(float(sum(scores) / len(scores)), 4),
                    "std_score": round(float(__import__("numpy").std(scores)), 4),
                    "n_splits": n_splits, "algorithm": algorithm, "task": task_type,
                    "target": target, "features": list(X.columns)}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("KFOLD_ERROR", f"K-Fold CV failed: {str(e)}").to_dict()

    # ──────────────────────────────────────────────
    # Feature Engineering
    # ──────────────────────────────────────────────

    def feature_engineering(self, session_id: str, operations: List[Dict] = None) -> Dict:
        """Apply feature engineering: polynomial features, interactions."""
        try:
            libs = self._load_ml_libs()
            df = self.data_engine.load_session_df(session_id)
            applied = []
            if operations:
                for op in operations:
                    op_type = op.get("type", "")
                    if op_type == "polynomial":
                        cols = op.get("columns", [])
                        degree = op.get("degree", 2)
                        if cols:
                            from sklearn.preprocessing import PolynomialFeatures
                            poly = PolynomialFeatures(degree=degree, include_bias=False)
                            poly_vals = poly.fit_transform(df[cols])
                            poly_names = poly.get_feature_names_out(cols)
                            poly_df = libs["pd"].DataFrame(poly_vals, columns=poly_names, index=df.index)
                            df = libs["pd"].concat([df.drop(columns=cols), poly_df], axis=1)
                            applied.append(f"Polynomial features ({degree}°) from {cols}")
                    elif op_type == "interaction":
                        from sklearn.preprocessing import PolynomialFeatures
                        cols = op.get("columns", [])
                        if len(cols) >= 2:
                            poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
                            int_vals = poly.fit_transform(df[cols])
                            int_names = [c for c in poly.get_feature_names_out(cols) if "__" in c]
                            int_df = libs["pd"].DataFrame(int_vals[:, len(cols):], columns=int_names[len(cols):], index=df.index) if len(int_names) > len(cols) else libs["pd"].DataFrame()
                            if not int_df.empty:
                                df = libs["pd"].concat([df, int_df], axis=1)
                                applied.append(f"Interaction features from {cols}")
                    elif op_type == "bin":
                        col = op.get("column", "")
                        bins = op.get("bins", 3)
                        if col in df.columns:
                            labels = [f"{col}_bin_{i}" for i in range(bins)]
                            df[f"{col}_binned"] = libs["pd"].cut(df[col], bins=bins, labels=labels)
                            applied.append(f"Binned '{col}' into {bins} bins")
            cleaned_path = self.sessions_dir / f"{session_id}_engineered.csv"
            df.to_csv(cleaned_path, index=False)
            self.save_session(f"{session_id}_engineered", str(cleaned_path))
            records = libs["json"].loads(df.head(200).to_json(orient="records"))
            return {"success": True, "message": f"Feature engineering complete — {len(df.columns)} columns (was {len(df.columns)})",
                    "engineered_session_id": f"{session_id}_engineered",
                    "preview": records, "columns": list(df.columns),
                    "shape": [len(df), len(df.columns)],
                    "operations_applied": applied}
        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("FEATENG_ERROR", f"Feature engineering failed: {str(e)}").to_dict()
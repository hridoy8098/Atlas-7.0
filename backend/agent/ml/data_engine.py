import json
import base64
import os
from typing import Dict, Callable, List, Optional
from pathlib import Path
from collections import OrderedDict


class MLError(Exception):
    """Structured ML error with user-friendly message and suggestion."""
    def __init__(self, code: str, message: str, suggestion: str = ""):
        self.code = code
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

    def to_dict(self):
        return {
            "success": False,
            "error_code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class DataEngine:
    def __init__(self, ml_libs_loader: Callable, sessions_dir: Path):
        self._load_ml_libs = ml_libs_loader
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        # LRU cache: session_id -> DataFrame (max 5 sessions in memory)
        self._df_cache = OrderedDict()
        self._cache_max = 5
        # Track estimated memory per session (bytes)
        self._cache_sizes = {}

    # ──────────────────────────────────────────────
    # Session helpers
    # ──────────────────────────────────────────────

    def get_session_path(self, session_id: str) -> Optional[Path]:
        """Return the file path stored for a session, or None."""
        meta_path = self.sessions_dir / f"{session_id}.json"
        if not meta_path.exists():
            return None
        with open(meta_path) as f:
            meta = json.load(f)
        return Path(meta["filepath"])

    def save_session(self, session_id: str, filepath: str, extra: dict = None):
        meta = {"filepath": filepath, **(extra or {})}
        with open(self.sessions_dir / f"{session_id}.json", "w") as f:
            json.dump(meta, f)

    def _cache_put(self, session_id: str, df):
        """Store DataFrame in LRU cache, evicting oldest if over limit."""
        if session_id in self._df_cache:
            self._df_cache.move_to_end(session_id)
            return
        # Rough memory estimate (rows × cols × 8 bytes per float)
        mem = df.memory_usage(deep=True).sum()
        self._cache_sizes[session_id] = mem
        # Evict if over 5 sessions or estimated total > 200MB
        total_mem = sum(self._cache_sizes.values())
        while len(self._df_cache) >= self._cache_max or total_mem > 200 * 1024 * 1024:
            oldest, _ = self._df_cache.popitem(last=False)
            self._cache_sizes.pop(oldest, None)
            total_mem = sum(self._cache_sizes.values())
        self._df_cache[session_id] = df
        self._df_cache.move_to_end(session_id)

    def _cache_get(self, session_id: str):
        """Return cached DataFrame or None. Moves to end on hit."""
        df = self._df_cache.get(session_id)
        if df is not None:
            self._df_cache.move_to_end(session_id)
        return df

    def load_session_df(self, session_id: str):
        """Load a DataFrame for an existing session. Raises MLError on failure.
        Uses an LRU cache to avoid re-reading large files from disk."""
        # Check cache first
        cached = self._cache_get(session_id)
        if cached is not None:
            return cached

        libs = self._load_ml_libs()
        pd = libs["pd"]

        meta_path = self.sessions_dir / f"{session_id}.json"
        if not meta_path.exists():
            raise MLError(
                "SESSION_NOT_FOUND",
                f"Session '{session_id}' not found.",
                "Upload your dataset again from the DATA tab.",
            )
        with open(meta_path) as f:
            meta = json.load(f)

        filepath = meta["filepath"]
        if not os.path.exists(filepath):
            raise MLError(
                "FILE_MISSING",
                "Dataset file no longer exists on disk.",
                "Upload your dataset again from the DATA tab.",
            )

        ext = filepath.lower().rsplit(".", 1)[-1]
        readers = {
            "csv": pd.read_csv,
            "json": pd.read_json,
            "xlsx": pd.read_excel,
            "xls": pd.read_excel,
            "parquet": pd.read_parquet,
            "feather": pd.read_feather,
        }
        reader = readers.get(ext)
        if not reader:
            raise MLError(
                "UNSUPPORTED_FORMAT",
                f"File format '.{ext}' is not supported.",
                "Use CSV, Excel (.xlsx), JSON, Parquet, or Feather.",
            )
        df = pd.read_csv(filepath) if ext == "csv" else reader(filepath)
        self._cache_put(session_id, df)
        return df

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def _load_image_dataset(self, filepath: str) -> "pd.DataFrame":
        """Load an image file and flatten pixels into a DataFrame row.
        Each pixel channel becomes a column (pixel_r, pixel_g, pixel_b).
        Returns a single-row DataFrame (or multi-row if folder of images)."""
        from PIL import Image
        libs = self._load_ml_libs()
        pd = libs["pd"]
        np = libs["np"]

        img = Image.open(filepath).convert("RGB").resize((64, 64))
        arr = np.array(img).reshape(1, -1)  # 1 row × 12288 cols
        cols = [f"pixel_{i}" for i in range(arr.shape[1])]
        df = pd.DataFrame(arr, columns=cols)
        df["filename"] = os.path.basename(filepath)
        return df

    def _load_image_folder(self, folder_path: str) -> "pd.DataFrame":
        """Load all images from a folder, one row per image, with label from subfolder name."""
        from PIL import Image
        libs = self._load_ml_libs()
        pd = libs["pd"]
        np = libs["np"]
        import glob as glob_mod

        rows = []
        exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp")
        for ext in exts:
            for img_path in glob_mod.glob(os.path.join(folder_path, "**", ext), recursive=True):
                try:
                    img = Image.open(img_path).convert("RGB").resize((64, 64))
                    arr = np.array(img).flatten()
                    label = os.path.basename(os.path.dirname(img_path))
                    rows.append([*arr, label, img_path])
                except Exception:
                    continue
        if not rows:
            raise MLError("NO_IMAGES", "No valid images found in folder.", "Supported: jpg, png, jpeg, bmp, webp")
        cols = [f"pixel_{i}" for i in range(len(rows[0]) - 2)] + ["label", "image_path"]
        df = pd.DataFrame(rows, columns=cols)
        return df

    def load_dataset(self, filepath: str, session_id: str, file_type: str = "auto") -> Dict:
        """Load a dataset from disk and register a session."""
        try:
            libs = self._load_ml_libs()
            pd = libs["pd"]
            np = libs["np"]

            if not os.path.exists(filepath):
                raise MLError(
                    "FILE_NOT_FOUND",
                    f"File not found: {os.path.basename(filepath)}",
                    "Make sure the file was uploaded successfully.",
                )

            ext = filepath.lower().rsplit(".", 1)[-1] if file_type == "auto" else file_type
            image_exts = {"jpg", "jpeg", "png", "bmp", "webp"}

            if ext in image_exts:
                df = self._load_image_dataset(filepath)
            elif ext == "folder":
                df = self._load_image_folder(filepath)
            else:
                readers = {
                    "csv": pd.read_csv,
                    "json": pd.read_json,
                    "xlsx": pd.read_excel,
                    "xls": pd.read_excel,
                    "parquet": pd.read_parquet,
                    "feather": pd.read_feather,
                }
                reader = readers.get(ext)
                if not reader:
                    raise MLError(
                        "UNSUPPORTED_FORMAT",
                        f"File format '.{ext}' is not supported.",
                        "Use CSV, Excel (.xlsx), JSON, Parquet, Feather, or image (jpg/png).",
                    )
                df = reader(filepath)

            if df.empty:
                raise MLError(
                    "EMPTY_DATASET",
                    "The uploaded file contains no data.",
                    "Check that the file has at least one row of data.",
                )

            # Save session
            self.save_session(session_id, filepath, {"is_image": ext in image_exts or ext == "folder"})

            # Build preview (first 200 rows max to keep response small)
            preview_df = df.head(200)
            records = json.loads(preview_df.to_json(orient="records"))

            missing = {c: int(df[c].isna().sum()) for c in df.columns}
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            is_image = ext in image_exts or ext == "folder"

            return {
                "success": True,
                "session_id": session_id,
                "message": f"Loaded {os.path.basename(filepath)} — {len(df):,} rows, {len(df.columns)} pixel columns" if is_image else f"Loaded {os.path.basename(filepath)} — {len(df):,} rows, {len(df.columns)} columns",
                "preview": records if not is_image else [],
                "columns": list(df.columns),
                "dtypes": {c: str(d) for c, d in df.dtypes.items()},
                "shape": [len(df), len(df.columns)],
                "filename": os.path.basename(filepath),
                "missing": missing,
                "numeric_columns": numeric_cols,
                "categorical_columns": categorical_cols,
                "is_image_dataset": is_image,
                "image_shape": [64, 64, 3] if is_image else None,
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("LOAD_ERROR", f"Failed to load file: {str(e)}", "Check the file is not corrupted.").to_dict()

    def clean_data(self, session_id: str, operations: List[Dict] = None) -> Dict:
        """Apply cleaning operations to a session dataset and save result."""
        try:
            df = self.load_session_df(session_id)
            original_shape = df.shape

            applied = []
            if operations:
                for op in operations:
                    op_type = op.get("type", "")

                    if op_type == "drop_na":
                        before = len(df)
                        df = df.dropna()
                        applied.append(f"Dropped {before - len(df)} rows with missing values")

                    elif op_type == "fill_na":
                        col = op.get("column")
                        value = op.get("value", 0)
                        if col and col in df.columns:
                            count = int(df[col].isna().sum())
                            df[col] = df[col].fillna(value)
                            applied.append(f"Filled {count} missing values in '{col}' with {value}")
                        else:
                            raise MLError("COLUMN_NOT_FOUND", f"Column '{col}' not found.", f"Available columns: {list(df.columns)}")

                    elif op_type == "drop_column":
                        col = op.get("column")
                        if col and col in df.columns:
                            df = df.drop(columns=[col])
                            applied.append(f"Dropped column '{col}'")
                        else:
                            raise MLError("COLUMN_NOT_FOUND", f"Column '{col}' not found.", f"Available columns: {list(df.columns)}")

                    elif op_type == "rename":
                        col, new_name = op.get("column"), op.get("new_name")
                        if col and new_name and col in df.columns:
                            df = df.rename(columns={col: new_name})
                            applied.append(f"Renamed '{col}' → '{new_name}'")

                    elif op_type == "encode":
                        col = op.get("column")
                        if col and col in df.columns:
                            if df[col].dtype != "object":
                                raise MLError(
                                    "NOT_CATEGORICAL",
                                    f"Column '{col}' is already numeric ({df[col].dtype}).",
                                    "Only text/categorical columns need encoding.",
                                )
                            import pandas as pd
                            df[col] = pd.Categorical(df[col]).codes
                            applied.append(f"Label-encoded column '{col}'")

            # Save cleaned file back into session folder
            cleaned_path = self.sessions_dir / f"{session_id}_cleaned.csv"
            df.to_csv(cleaned_path, index=False)
            self.save_session(f"{session_id}_cleaned", str(cleaned_path))

            records = json.loads(df.head(200).to_json(orient="records"))
            missing = {c: int(df[c].isna().sum()) for c in df.columns}

            return {
                "success": True,
                "message": f"Cleaning complete — {len(df):,} rows, {len(df.columns)} columns (was {original_shape[0]:,} × {original_shape[1]})",
                "cleaned_session_id": f"{session_id}_cleaned",
                "preview": records,
                "columns": list(df.columns),
                "dtypes": {c: str(d) for c, d in df.dtypes.items()},
                "shape": [len(df), len(df.columns)],
                "missing": missing,
                "operations_applied": applied,
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("CLEAN_ERROR", f"Cleaning failed: {str(e)}").to_dict()

    def analyze_data(self, session_id: str) -> Dict:
        """Full statistical analysis of a session dataset."""
        try:
            libs = self._load_ml_libs()
            np = libs["np"]

            df = self.load_session_df(session_id)

            numeric_df = df.select_dtypes(include=[np.number])
            categorical_df = df.select_dtypes(include=["object", "category"])

            basic_stats = {}
            outliers = {}
            skewness = {}
            correlations = {}
            histogram_data = {}

            if not numeric_df.empty:
                desc = numeric_df.describe()
                basic_stats = json.loads(desc.to_json(orient="columns"))

                for col in numeric_df.columns:
                    s = numeric_df[col].dropna()
                    if len(s) < 2:
                        continue

                    skewness[col] = round(float(s.skew()), 4)

                    Q1 = float(s.quantile(0.25))
                    Q3 = float(s.quantile(0.75))
                    IQR = Q3 - Q1
                    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
                    outlier_count = int(((s < lower) | (s > upper)).sum())
                    if outlier_count > 0:
                        outliers[col] = {"count": outlier_count, "lower_bound": round(lower, 4), "upper_bound": round(upper, 4)}

                    # Histogram buckets (20 bins, frontend renders these)
                    counts, bin_edges = np.histogram(s.dropna(), bins=20)
                    histogram_data[col] = {
                        "counts": counts.tolist(),
                        "bins": [round(float(e), 4) for e in bin_edges],
                    }

                # Correlation matrix (limit to 15 cols for readability)
                corr_cols = numeric_df.columns[:15]
                corr_matrix = numeric_df[corr_cols].corr()
                correlations = json.loads(corr_matrix.to_json(orient="index"))

            analysis = {
                "basic_stats": basic_stats,
                "outliers": outliers,
                "skewness": skewness,
                "correlations": correlations,
                "histogram_data": histogram_data,
            }

            if not categorical_df.empty:
                analysis["value_counts"] = {
                    c: {str(k): int(v) for k, v in df[c].value_counts().head(20).items()}
                    for c in categorical_df.columns
                }

            return {
                "success": True,
                "message": f"Analysis complete — {len(df):,} rows, {len(df.columns)} columns",
                "analysis": analysis,
            }

        except MLError as e:
            return e.to_dict()
        except Exception as e:
            return MLError("ANALYSIS_ERROR", f"Analysis failed: {str(e)}").to_dict()
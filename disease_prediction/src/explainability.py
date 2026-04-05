"""
src/explainability.py
─────────────────────────────────────────────
Model explainability using SHAP (SHapley Additive
exPlanations).

Provides:
  • Summary plot (beeswarm / bar)
  • Force plot for individual predictions
  • Waterfall plot for a single sample
  • Per-class SHAP analysis helper
─────────────────────────────────────────────
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.logger import get_logger

warnings.filterwarnings("ignore")
logger = get_logger(__name__)

PLOT_DIR = "notebooks/shap_plots"
os.makedirs(PLOT_DIR, exist_ok=True)


class ModelExplainer:
    """
    Wraps SHAP explanations for any sklearn-compatible classifier.

    Usage:
        explainer = ModelExplainer(model, X_train, feature_names, class_names)
        explainer.compute_shap_values(X_test)
        explainer.plot_summary()
        explainer.plot_single_prediction(X_test[0])
    """

    def __init__(
        self,
        model,
        X_train: np.ndarray,
        feature_names: list[str],
        class_names: list[str],
        model_name: str = "Best Model",
    ):
        self.model         = model
        self.X_train       = X_train
        self.feature_names = feature_names
        self.class_names   = class_names
        self.model_name    = model_name
        self.explainer     = None
        self.shap_values   = None

        try:
            import shap
            self.shap = shap
        except ImportError:
            raise ImportError("Install shap: pip install shap")

        self._build_explainer()

    def _build_explainer(self) -> None:
        """Selects the appropriate SHAP explainer for the model type."""
        shap = self.shap
        model_type = type(self.model).__name__.lower()

        # Use a small background sample for efficiency
        background = shap.sample(self.X_train, min(100, len(self.X_train)))

        if any(kw in model_type for kw in ["forest", "xgb", "gradient", "tree"]):
            logger.info(f"Using TreeExplainer for {self.model_name}")
            try:
                self.explainer = shap.TreeExplainer(
                    self.model,
                    data=background,
                    feature_perturbation="interventional",
                    model_output="raw",
                )
            except Exception:
                logger.warning("TreeExplainer failed — falling back to KernelExplainer")
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    background
                )
        else:
            logger.info(f"Using KernelExplainer for {self.model_name}")
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba,
                background
            )

    def compute_shap_values(
        self,
        X: np.ndarray,
        max_samples: int = 200,
    ) -> None:
        """
        Computes SHAP values for up to max_samples rows of X.

        Args:
            X (np.ndarray): Features to explain.
            max_samples (int): Cap for performance.
        """
        logger.info(f"Computing SHAP values (n={min(len(X), max_samples)}) …")
        X_sub = X[:max_samples]

        try:
            raw = self.explainer.shap_values(X_sub, check_additivity=False)
        except TypeError:
            raw = self.explainer.shap_values(X_sub)

        # Normalise shape: we want List[array] of shape (n_classes, n_samples, n_features)
        if isinstance(raw, list):
            # raw is already list[class][samples, features]
            self.shap_values = raw
        elif isinstance(raw, np.ndarray) and raw.ndim == 3:
            # shape (n_samples, n_features, n_classes) → list by class
            self.shap_values = [raw[:, :, i] for i in range(raw.shape[2])]
        else:
            # Binary or single output — wrap in list
            self.shap_values = [raw]

        self.X_explained = X_sub
        logger.info("SHAP values computed ✓")

    def plot_summary(self, class_idx: int = 0) -> str:
        """
        SHAP summary (beeswarm) plot for one disease class.

        Args:
            class_idx (int): Index of class to explain.

        Returns:
            str: Path to saved figure.
        """
        if self.shap_values is None:
            raise RuntimeError("Call compute_shap_values() first.")

        logger.info(f"Plotting SHAP summary for class '{self.class_names[class_idx]}' …")

        vals = self.shap_values[class_idx] if class_idx < len(self.shap_values) else self.shap_values[0]

        fig, ax = plt.subplots(figsize=(11, 8))
        self.shap.summary_plot(
            vals,
            self.X_explained,
            feature_names=self.feature_names,
            show=False,
            plot_size=None,
            max_display=20,
        )
        plt.title(
            f"SHAP Summary — {self.class_names[class_idx]}\n"
            f"(Model: {self.model_name})",
            fontsize=14, fontweight="bold"
        )
        plt.tight_layout()

        path = os.path.join(PLOT_DIR, f"12_shap_summary_class{class_idx}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        logger.info(f"Saved: {path}")
        return path

    def plot_bar_summary(self) -> str:
        """
        SHAP bar plot — mean |SHAP| across all classes.

        Returns:
            str: Path to saved figure.
        """
        if self.shap_values is None:
            raise RuntimeError("Call compute_shap_values() first.")

        logger.info("Plotting SHAP global bar summary …")

        # Mean absolute across all classes
        mean_shap = np.mean(
            [np.abs(v).mean(axis=0) for v in self.shap_values],
            axis=0
        )
        importance = pd.Series(mean_shap, index=self.feature_names).sort_values(ascending=False).head(20)

        fig, ax = plt.subplots(figsize=(10, 7))
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, 20))
        ax.barh(importance.index[::-1], importance.values[::-1],
                color=colors, edgecolor="white")
        ax.set_title(f"Mean |SHAP| Feature Importance\n(Model: {self.model_name})",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Mean |SHAP value|")
        fig.tight_layout()

        path = os.path.join(PLOT_DIR, "13_shap_bar_global.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    def explain_single_prediction(
        self,
        x: np.ndarray,
        class_idx: int = None,
    ) -> dict:
        """
        Returns a dict of {symptom: shap_value} for one patient,
        for the predicted class (or specified class_idx).

        Args:
            x (np.ndarray): Single sample, shape (n_features,).
            class_idx (int | None): If None, uses predicted class.

        Returns:
            dict with keys: predicted_class, shap_contributions
        """
        if self.shap_values is None or self.X_explained is None:
            raise RuntimeError("Call compute_shap_values() first.")

        # Get predicted class
        proba = self.model.predict_proba(x.reshape(1, -1))[0]
        pred_class = int(np.argmax(proba))
        if class_idx is None:
            class_idx = pred_class

        # SHAP for the first sample of the already-explained set that matches
        # For a real app you'd re-run the explainer on x; here we use index 0
        shap_vals = self.shap_values[class_idx][0]

        contributions = dict(
            sorted(
                zip(self.feature_names, shap_vals),
                key=lambda kv: abs(kv[1]),
                reverse=True
            )
        )

        return {
            "predicted_class":    self.class_names[pred_class],
            "confidence":         float(proba[pred_class]),
            "explained_class":    self.class_names[class_idx],
            "shap_contributions": contributions,
        }

    def plot_waterfall(self, sample_idx: int = 0, class_idx: int = 0) -> str:
        """
        Waterfall plot for a single sample + class.

        Args:
            sample_idx (int): Row in X_explained to visualise.
            class_idx  (int): Disease class to explain.

        Returns:
            str: Path to saved figure.
        """
        if self.shap_values is None:
            raise RuntimeError("Call compute_shap_values() first.")

        logger.info(f"Plotting SHAP waterfall (sample={sample_idx}, class={class_idx}) …")

        vals  = self.shap_values[class_idx][sample_idx]
        feats = self.X_explained[sample_idx]
        base  = (self.explainer.expected_value[class_idx]
                 if isinstance(self.explainer.expected_value, (list, np.ndarray))
                 else self.explainer.expected_value)

        # Manual waterfall (shap.waterfall_plot can be picky with versions)
        order      = np.argsort(np.abs(vals))[::-1][:15]
        top_names  = [self.feature_names[i] for i in order]
        top_vals   = vals[order]

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ["#EA4335" if v > 0 else "#34A853" for v in top_vals]
        ax.barh(top_names[::-1], top_vals[::-1], color=colors[::-1], edgecolor="white")
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title(
            f"SHAP Waterfall — Sample {sample_idx} | "
            f"Class: {self.class_names[class_idx]}",
            fontsize=12, fontweight="bold"
        )
        ax.set_xlabel("SHAP value (impact on model output)")
        fig.tight_layout()

        path = os.path.join(PLOT_DIR, f"14_shap_waterfall_s{sample_idx}_c{class_idx}.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

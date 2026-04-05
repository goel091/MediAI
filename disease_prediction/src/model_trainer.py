"""
src/model_trainer.py
─────────────────────────────────────────────
Trains, evaluates, and compares four classifiers:
  • K-Nearest Neighbours (KNN)
  • Logistic Regression
  • Random Forest
  • XGBoost

Also handles:
  • Cross-validation
  • ROC-AUC curves
  • Confusion matrices
  • Model comparison table
  • Hyperparameter tuning (GridSearchCV)
  • Saving the best model to disk
─────────────────────────────────────────────
"""

import os
import time
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.neighbors         import KNeighborsClassifier
from sklearn.linear_model      import LogisticRegression
from sklearn.ensemble          import RandomForestClassifier
from sklearn.model_selection   import (
    cross_val_score, GridSearchCV, StratifiedKFold
)
from sklearn.metrics           import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, auc
)
from sklearn.preprocessing     import label_binarize

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from src.logger import get_logger

warnings.filterwarnings("ignore")
logger = get_logger(__name__)

# ── Output directory for all plots ────────────────────────────────────────────
PLOT_DIR = "notebooks/model_plots"
os.makedirs(PLOT_DIR, exist_ok=True)

PALETTE = {
    "primary":   "#1A73E8",
    "secondary": "#34A853",
    "accent":    "#EA4335",
    "warn":      "#FBBC04",
}

MODEL_COLORS = {
    "KNN":                 "#FF6B6B",
    "Logistic Regression": "#4ECDC4",
    "Random Forest":       "#45B7D1",
    "XGBoost":             "#96CEB4",
}


# ═══════════════════════════════════════════════════════════════════════════════
class ModelTrainer:
    """
    Full model training and evaluation pipeline.

    Args:
        class_names (list[str]): Disease label names.
        n_jobs (int): CPU cores for parallel ops (-1 = all).
        random_state (int): Reproducibility seed.
        cv_folds (int): Cross-validation folds.
    """

    def __init__(
        self,
        class_names: list[str],
        n_jobs: int = -1,
        random_state: int = 42,
        cv_folds: int = 5,
    ):
        self.class_names  = class_names
        self.n_jobs       = n_jobs
        self.random_state = random_state
        self.cv_folds     = cv_folds
        self.models: dict  = {}
        self.results: dict = {}
        self._define_models()

    # ──────────────────────────────────────────────────────────────────────────
    # Model Definitions
    # ──────────────────────────────────────────────────────────────────────────

    def _define_models(self) -> None:
        """Instantiate all baseline classifiers."""
        self.models = {
            "KNN": KNeighborsClassifier(
                n_neighbors=7,
                weights="distance",
                n_jobs=self.n_jobs,
            ),
            "Logistic Regression": LogisticRegression(
                max_iter=1000,
                solver="lbfgs",
                n_jobs=self.n_jobs,
                random_state=self.random_state,
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=None,
                min_samples_split=2,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
            ),
        }
        if XGBOOST_AVAILABLE:
            self.models["XGBoost"] = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric="mlogloss",
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbosity=0,
            )
        else:
            logger.warning("XGBoost not found — skipping that model.")

    # ──────────────────────────────────────────────────────────────────────────
    # Training & Evaluation
    # ──────────────────────────────────────────────────────────────────────────

    def _evaluate_model(
        self, name: str, model,
        X_train: np.ndarray, X_test: np.ndarray,
        y_train: np.ndarray, y_test: np.ndarray,
    ) -> dict:
        """
        Fits one model, evaluates on test set, runs cross-val.

        Returns a results dict.
        """
        logger.info(f"  Training: {name} …")
        t0 = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - t0

        y_pred  = model.predict(X_test)
        y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

        acc   = accuracy_score(y_test, y_pred)
        prec  = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec   = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1    = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        # ROC-AUC (one-vs-rest, macro)
        if y_proba is not None:
            try:
                roc_auc = roc_auc_score(
                    y_test, y_proba,
                    multi_class="ovr", average="macro"
                )
            except Exception:
                roc_auc = None
        else:
            roc_auc = None

        # Cross-validation (F1 weighted)
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True,
                             random_state=self.random_state)
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=cv, scoring="f1_weighted", n_jobs=self.n_jobs
        )

        result = {
            "model":       model,
            "name":        name,
            "accuracy":    acc,
            "precision":   prec,
            "recall":      rec,
            "f1":          f1,
            "roc_auc":     roc_auc,
            "cv_mean":     cv_scores.mean(),
            "cv_std":      cv_scores.std(),
            "train_time":  train_time,
            "y_pred":      y_pred,
            "y_proba":     y_proba,
            "report":      classification_report(
                               y_test, y_pred,
                               target_names=self.class_names,
                               zero_division=0
                           ),
        }

        roc_str = f"{roc_auc:.4f}" if roc_auc is not None else "N/A"
        logger.info(
            f"    ✓ Acc={acc:.4f} | F1={f1:.4f} | "
            f"ROC-AUC={roc_str} | "
            f"CV={cv_scores.mean():.4f}±{cv_scores.std():.4f} | "
            f"Time={train_time:.1f}s"
        )
        return result

    def train_all(
        self,
        X_train: np.ndarray, X_test: np.ndarray,
        y_train: np.ndarray, y_test: np.ndarray,
    ) -> dict:
        """
        Trains all defined models and stores results.

        Returns:
            dict: {model_name: result_dict}
        """
        logger.info("═" * 55)
        logger.info("Training all models …")
        logger.info("═" * 55)

        for name, model in self.models.items():
            self.results[name] = self._evaluate_model(
                name, model, X_train, X_test, y_train, y_test
            )

        logger.info("✅ All models trained")
        return self.results

    # ──────────────────────────────────────────────────────────────────────────
    # Visualization
    # ──────────────────────────────────────────────────────────────────────────

    def plot_model_comparison(self) -> str:
        """Bar chart comparing Accuracy, F1, and ROC-AUC across models."""
        logger.info("Plotting model comparison …")

        metrics = ["accuracy", "f1", "roc_auc"]
        labels  = ["Accuracy", "F1 (weighted)", "ROC-AUC"]
        model_names = list(self.results.keys())

        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        for ax, metric, label in zip(axes, metrics, labels):
            values = [self.results[m][metric] or 0 for m in model_names]
            colors = [MODEL_COLORS.get(m, "#999999") for m in model_names]
            bars = ax.bar(model_names, values, color=colors, edgecolor="white", width=0.55)
            ax.set_ylim(0, 1.05)
            ax.set_title(label, fontweight="bold", fontsize=13)
            ax.set_ylabel("Score")
            ax.set_xticklabels(model_names, rotation=20, ha="right")

            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold"
                )

        fig.suptitle("Model Performance Comparison", fontsize=16, fontweight="bold", y=1.02)
        fig.tight_layout()
        path = os.path.join(PLOT_DIR, "07_model_comparison.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    def plot_confusion_matrices(self, y_test: np.ndarray) -> str:
        """Grid of confusion matrices for all trained models."""
        logger.info("Plotting confusion matrices …")

        n = len(self.results)
        ncols = 2
        nrows = (n + 1) // ncols

        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 9, nrows * 7))
        axes = axes.flatten()

        for idx, (name, res) in enumerate(self.results.items()):
            cm = confusion_matrix(y_test, res["y_pred"])
            # Truncate class names for readability
            short_names = [cn[:12] for cn in self.class_names]
            sns.heatmap(
                cm, ax=axes[idx],
                cmap="Blues", annot=(len(self.class_names) <= 15),
                fmt="d", linewidths=0.3,
                xticklabels=short_names if len(self.class_names) <= 20 else False,
                yticklabels=short_names if len(self.class_names) <= 20 else False,
                cbar_kws={"shrink": 0.7},
            )
            axes[idx].set_title(f"{name}  (Acc={res['accuracy']:.3f})",
                                fontweight="bold", fontsize=12)
            axes[idx].set_xlabel("Predicted", fontsize=10)
            axes[idx].set_ylabel("Actual", fontsize=10)

        # Hide extra axes
        for ax in axes[n:]:
            ax.set_visible(False)

        fig.suptitle("Confusion Matrices — All Models",
                     fontsize=16, fontweight="bold", y=1.01)
        fig.tight_layout()
        path = os.path.join(PLOT_DIR, "08_confusion_matrices.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    def plot_roc_curves(self, y_test: np.ndarray) -> str:
        """
        Macro-average ROC curves for all models (one-vs-rest).
        Only plotted for models that support predict_proba.
        """
        logger.info("Plotting ROC curves …")

        n_classes = len(self.class_names)
        y_bin = label_binarize(y_test, classes=list(range(n_classes)))

        fig, ax = plt.subplots(figsize=(9, 7))

        for name, res in self.results.items():
            if res["y_proba"] is None:
                continue
            try:
                # Macro-average
                fpr = dict(); tpr = dict()
                for i in range(n_classes):
                    fpr[i], tpr[i], _ = roc_curve(y_bin[:, i], res["y_proba"][:, i])

                all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))
                mean_tpr = np.zeros_like(all_fpr)
                for i in range(n_classes):
                    mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])
                mean_tpr /= n_classes
                macro_auc = auc(all_fpr, mean_tpr)

                ax.plot(
                    all_fpr, mean_tpr,
                    color=MODEL_COLORS.get(name, "#999999"),
                    lw=2,
                    label=f"{name} (AUC = {macro_auc:.3f})"
                )
            except Exception as e:
                logger.warning(f"Could not plot ROC for {name}: {e}")

        ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Random Classifier")
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel("False Positive Rate", fontsize=12)
        ax.set_ylabel("True Positive Rate", fontsize=12)
        ax.set_title("Macro-Average ROC Curves", fontsize=14, fontweight="bold")
        ax.legend(loc="lower right", fontsize=10)
        fig.tight_layout()

        path = os.path.join(PLOT_DIR, "09_roc_curves.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    def plot_cv_comparison(self) -> str:
        """Cross-validation score comparison with error bars."""
        logger.info("Plotting CV comparison …")

        names  = list(self.results.keys())
        means  = [self.results[n]["cv_mean"] for n in names]
        stds   = [self.results[n]["cv_std"]  for n in names]
        colors = [MODEL_COLORS.get(n, "#999999") for n in names]

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(names, means, yerr=stds, capsize=7,
                      color=colors, edgecolor="white", width=0.5, alpha=0.9)
        ax.set_ylim(0, 1.1)
        ax.set_ylabel("CV F1-Weighted Score", fontsize=12)
        ax.set_title(
            f"{self.cv_folds}-Fold Cross-Validation Comparison",
            fontsize=14, fontweight="bold"
        )
        ax.set_xticklabels(names, rotation=15, ha="right")

        for bar, m, s in zip(bars, means, stds):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + s + 0.01,
                f"{m:.3f}±{s:.3f}",
                ha="center", va="bottom", fontsize=10
            )

        fig.tight_layout()
        path = os.path.join(PLOT_DIR, "10_cv_comparison.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    def plot_feature_importance(self, feature_names: list[str], top_n: int = 25) -> str:
        """Feature importance from tree-based models (RF / XGBoost)."""
        logger.info("Plotting feature importances …")

        tree_models = {n: r for n, r in self.results.items()
                       if hasattr(r["model"], "feature_importances_")}
        if not tree_models:
            logger.warning("No tree-based models available for feature importance.")
            return ""

        n = len(tree_models)
        fig, axes = plt.subplots(1, n, figsize=(n * 10, 7))
        if n == 1:
            axes = [axes]

        for ax, (name, res) in zip(axes, tree_models.items()):
            imp = pd.Series(
                res["model"].feature_importances_,
                index=feature_names
            ).sort_values(ascending=False).head(top_n)

            colors = plt.cm.viridis(np.linspace(0.2, 0.9, top_n))
            ax.barh(imp.index[::-1], imp.values[::-1], color=colors, edgecolor="white")
            ax.set_title(f"{name} — Top {top_n} Features",
                         fontweight="bold", fontsize=12)
            ax.set_xlabel("Importance Score")

        fig.suptitle("Feature Importance Analysis", fontsize=15, fontweight="bold", y=1.01)
        fig.tight_layout()
        path = os.path.join(PLOT_DIR, "11_feature_importance.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    # ──────────────────────────────────────────────────────────────────────────
    # Comparison Table & Best Model
    # ──────────────────────────────────────────────────────────────────────────

    def get_comparison_table(self) -> pd.DataFrame:
        """Returns a formatted DataFrame comparing all models."""
        rows = []
        for name, res in self.results.items():
            rows.append({
                "Model":          name,
                "Accuracy":       round(res["accuracy"],  4),
                "Precision":      round(res["precision"], 4),
                "Recall":         round(res["recall"],    4),
                "F1 (weighted)":  round(res["f1"],        4),
                "ROC-AUC":        round(res["roc_auc"], 4) if res["roc_auc"] else None,
                "CV Mean F1":     round(res["cv_mean"],   4),
                "CV Std":         round(res["cv_std"],    4),
                "Train Time (s)": round(res["train_time"],2),
            })
        df = pd.DataFrame(rows).set_index("Model")
        return df

    def get_best_model_name(self, metric: str = "f1") -> str:
        """Returns the name of the best model by a given metric."""
        scores = {n: r[metric] or 0 for n, r in self.results.items()}
        best = max(scores, key=scores.get)
        logger.info(f"Best model by {metric}: {best}  ({scores[best]:.4f})")
        return best

    # ──────────────────────────────────────────────────────────────────────────
    # Hyperparameter Tuning
    # ──────────────────────────────────────────────────────────────────────────

    def tune_best_model(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
    ) -> object:
        """
        Runs GridSearchCV on the best model with a targeted parameter grid.

        Args:
            model_name (str): Name of model to tune.
            X_train: Scaled training features.
            y_train: Training labels.

        Returns:
            Fitted best estimator.
        """
        logger.info(f"═" * 55)
        logger.info(f"Tuning {model_name} with GridSearchCV …")

        param_grids = {
            "KNN": {
                "n_neighbors": [3, 5, 7, 9, 11],
                "weights":     ["uniform", "distance"],
                "metric":      ["euclidean", "manhattan"],
            },
            "Logistic Regression": {
                "C":       [0.01, 0.1, 1.0, 10.0],
                "solver":  ["lbfgs", "saga"],
                "max_iter":[500, 1000],
            },
            "Random Forest": {
                "n_estimators":     [100, 200, 300],
                "max_depth":        [None, 10, 20],
                "min_samples_split":[2, 5],
            },
            "XGBoost": {
                "n_estimators":  [100, 200],
                "max_depth":     [4, 6, 8],
                "learning_rate": [0.05, 0.1, 0.2],
                "subsample":     [0.8, 1.0],
            },
        }

        if model_name not in param_grids:
            logger.warning(f"No parameter grid defined for {model_name}.")
            return self.results[model_name]["model"]

        base_model  = self.results[model_name]["model"]
        param_grid  = param_grids[model_name]
        cv          = StratifiedKFold(n_splits=self.cv_folds, shuffle=True,
                                      random_state=self.random_state)

        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=cv,
            scoring="f1_weighted",
            n_jobs=self.n_jobs,
            verbose=1,
            refit=True,
        )
        grid_search.fit(X_train, y_train)

        logger.info(f"Best params : {grid_search.best_params_}")
        logger.info(f"Best CV F1  : {grid_search.best_score_:.4f}  "
                    f"(was {self.results[model_name]['cv_mean']:.4f})")

        return grid_search.best_estimator_

    # ──────────────────────────────────────────────────────────────────────────
    # Persist Model
    # ──────────────────────────────────────────────────────────────────────────

    def save_model(
        self,
        model,
        filename: str = "best_model.pkl",
        save_dir: str = "models",
    ) -> str:
        """
        Saves a model to disk using joblib.

        Returns:
            str: Full path to saved file.
        """
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)
        joblib.dump(model, path)
        logger.info(f"✅ Model saved → {path}")
        return path


# ── Standalone run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from src.data_generator    import generate_dataset
    from src.data_preprocessing import DataPreprocessor

    raw_path = "data/raw/disease_dataset.csv"
    if not os.path.exists(raw_path):
        generate_dataset(save_path=raw_path)

    pp = DataPreprocessor()
    data = pp.run_pipeline(raw_path)

    trainer = ModelTrainer(class_names=data["class_names"])
    results = trainer.train_all(
        data["X_train"], data["X_test"],
        data["y_train"].values, data["y_test"].values,
    )

    print("\n── Model Comparison ──")
    print(trainer.get_comparison_table().to_string())

    best_name = trainer.get_best_model_name("f1")
    print(f"\nBest model: {best_name}")

    # Tune
    tuned = trainer.tune_best_model(best_name, data["X_train"], data["y_train"].values)
    trainer.save_model(tuned, filename="best_model.pkl")

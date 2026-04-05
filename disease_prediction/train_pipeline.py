"""
train_pipeline.py
─────────────────────────────────────────────
Master script: runs the complete training pipeline.

Steps:
  1.  Generate / load dataset
  2.  Preprocess data
  3.  Run EDA
  4.  Train all models
  5.  Evaluate & compare
  6.  Hyperparameter tuning
  7.  SHAP explainability
  8.  Save best model + artefacts

Usage:
    python train_pipeline.py
─────────────────────────────────────────────
"""

import os
import sys
import joblib
import numpy as np

# ── Ensure project root is on PYTHONPATH ──────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.logger            import get_logger
from src.data_generator    import generate_dataset
from src.data_preprocessing import DataPreprocessor
from src.eda               import EDAAnalyzer
from src.model_trainer     import ModelTrainer
from src.explainability    import ModelExplainer

import pandas as pd

logger = get_logger("train_pipeline")


def main() -> None:
    logger.info("╔══════════════════════════════════════════════════╗")
    logger.info("║   AI Disease Prediction — Training Pipeline      ║")
    logger.info("╚══════════════════════════════════════════════════╝")

    # ── STEP 1: Dataset ──────────────────────────────────────────────────────
    raw_path = os.path.join(ROOT, "data", "raw", "disease_dataset.csv")
    if not os.path.exists(raw_path):
        logger.info("Raw dataset not found — generating synthetic data …")
        generate_dataset(save_path=raw_path)
    else:
        logger.info(f"Using existing dataset: {raw_path}")

    # ── STEP 2: Preprocessing ────────────────────────────────────────────────
    logger.info("\n── Step 2: Preprocessing ──")
    pp   = DataPreprocessor(test_size=0.20, random_state=42)
    data = pp.run_pipeline(raw_path)

    # ── STEP 3: EDA ──────────────────────────────────────────────────────────
    logger.info("\n── Step 3: Exploratory Data Analysis ──")
    import pandas as _pd
    df_raw = _pd.read_csv(raw_path)
    eda    = EDAAnalyzer(df_raw, output_dir=os.path.join(ROOT, "notebooks", "eda_plots"))
    eda_results = eda.run_all()

    logger.info("\nKey EDA Insights:")
    for insight in eda_results["insights"]:
        logger.info(f"  {insight}")

    # ── STEP 4: Train all models ─────────────────────────────────────────────
    logger.info("\n── Step 4: Model Training ──")
    trainer = ModelTrainer(class_names=data["class_names"])
    results = trainer.train_all(
        data["X_train"], data["X_test"],
        data["y_train"].values, data["y_test"].values,
    )

    # ── STEP 5: Evaluate & Compare ───────────────────────────────────────────
    logger.info("\n── Step 5: Evaluation ──")
    comparison = trainer.get_comparison_table()
    logger.info(f"\n{comparison.to_string()}")

    # Save comparison CSV
    comp_path = os.path.join(ROOT, "notebooks", "model_comparison.csv")
    comparison.to_csv(comp_path)
    logger.info(f"Comparison table saved → {comp_path}")

    # Generate all evaluation plots
    trainer.plot_model_comparison()
    trainer.plot_confusion_matrices(data["y_test"].values)
    trainer.plot_roc_curves(data["y_test"].values)
    trainer.plot_cv_comparison()
    trainer.plot_feature_importance(data["feature_names"])

    # ── STEP 6: Hyperparameter Tuning ────────────────────────────────────────
    logger.info("\n── Step 6: Hyperparameter Tuning ──")
    best_name  = trainer.get_best_model_name("f1")
    tuned_model = trainer.tune_best_model(
        best_name, data["X_train"], data["y_train"].values
    )

    # Re-evaluate tuned model on test set
    from sklearn.metrics import f1_score, accuracy_score
    y_pred_tuned = tuned_model.predict(data["X_test"])
    acc_tuned = accuracy_score(data["y_test"].values, y_pred_tuned)
    f1_tuned  = f1_score(data["y_test"].values, y_pred_tuned, average="weighted")
    logger.info(f"Tuned model  — Acc: {acc_tuned:.4f} | F1: {f1_tuned:.4f}")
    logger.info(f"Baseline     — Acc: {results[best_name]['accuracy']:.4f} | F1: {results[best_name]['f1']:.4f}")

    # ── STEP 7: SHAP Explainability ──────────────────────────────────────────
    logger.info("\n── Step 7: SHAP Explainability ──")
    try:
        explainer = ModelExplainer(
            model=tuned_model,
            X_train=data["X_train"],
            feature_names=data["feature_names"],
            class_names=data["class_names"],
            model_name=best_name,
        )
        explainer.compute_shap_values(data["X_test"], max_samples=100)
        explainer.plot_summary(class_idx=0)
        explainer.plot_bar_summary()
        explainer.plot_waterfall(sample_idx=0, class_idx=0)
        logger.info("SHAP plots saved to notebooks/shap_plots/")
    except Exception as exc:
        logger.warning(f"SHAP explainability skipped: {exc}")

    # ── STEP 8: Save artefacts ───────────────────────────────────────────────
    logger.info("\n── Step 8: Saving Artefacts ──")
    models_dir = os.path.join(ROOT, "models")
    trainer.save_model(tuned_model, filename="best_model.pkl", save_dir=models_dir)
    pp.save_artefacts(save_dir=models_dir)

    # Save metadata (feature names, class names)
    metadata = {
        "feature_names": data["feature_names"],
        "class_names":   data["class_names"],
        "best_model":    best_name,
        "n_classes":     len(data["class_names"]),
        "n_features":    len(data["feature_names"]),
    }
    meta_path = os.path.join(models_dir, "metadata.pkl")
    joblib.dump(metadata, meta_path)
    logger.info(f"Metadata saved → {meta_path}")

    # Save processed data
    proc_dir = os.path.join(ROOT, "data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    _pd.DataFrame(
        data["X_train"],
        columns=data["feature_names"]
    ).to_csv(os.path.join(proc_dir, "X_train.csv"), index=False)
    _pd.DataFrame(
        data["X_test"],
        columns=data["feature_names"]
    ).to_csv(os.path.join(proc_dir, "X_test.csv"), index=False)
    _pd.Series(data["y_train"].values, name="Disease").to_csv(
        os.path.join(proc_dir, "y_train.csv"), index=False)
    _pd.Series(data["y_test"].values,  name="Disease").to_csv(
        os.path.join(proc_dir, "y_test.csv"),  index=False)

    logger.info("╔══════════════════════════════════════════════════╗")
    logger.info("║   ✅  Training Pipeline Complete!                ║")
    logger.info("╠══════════════════════════════════════════════════╣")
    logger.info(f"║  Best model  : {best_name:<34}║")
    logger.info(f"║  Accuracy    : {acc_tuned:.4f}                            ║")
    logger.info(f"║  F1 Score    : {f1_tuned:.4f}                            ║")
    logger.info("╚══════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()

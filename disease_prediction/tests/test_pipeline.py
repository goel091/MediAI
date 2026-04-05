"""
tests/test_pipeline.py
─────────────────────────────────────────────
Unit tests for the Disease Prediction pipeline.

Run:
    pytest tests/ -v
─────────────────────────────────────────────
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

# Ensure project root is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.data_generator     import generate_dataset, DISEASES, SYMPTOM_NAMES, NUM_SYMPTOMS
from src.data_preprocessing  import DataPreprocessor


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def raw_df():
    """Generate a small synthetic dataset for testing."""
    return generate_dataset(
        n_samples_per_disease=20,
        noise_level=0.0,
        random_state=0,
        save_path=os.path.join(ROOT, "data", "raw", "test_dataset.csv")
    )

@pytest.fixture(scope="module")
def preprocessor():
    return DataPreprocessor(test_size=0.25, random_state=42)

@pytest.fixture(scope="module")
def pipeline_data(raw_df, preprocessor):
    path = os.path.join(ROOT, "data", "raw", "test_dataset.csv")
    return preprocessor.run_pipeline(path)


# ─── Data Generator Tests ─────────────────────────────────────────────────────

class TestDataGenerator:

    def test_output_shape(self, raw_df):
        """Dataset should have correct number of rows and columns."""
        expected_rows = 20 * len(DISEASES)
        assert len(raw_df) == expected_rows, f"Expected {expected_rows} rows"
        assert len(raw_df.columns) == NUM_SYMPTOMS + 1  # +1 for Disease

    def test_symptom_columns(self, raw_df):
        """All symptom columns should be binary (0 or 1)."""
        sym_cols = [c for c in raw_df.columns if c != "Disease"]
        unique_vals = set(raw_df[sym_cols].values.flatten())
        assert unique_vals.issubset({0, 1}), f"Non-binary values found: {unique_vals - {0,1}}"

    def test_disease_column_present(self, raw_df):
        assert "Disease" in raw_df.columns

    def test_all_diseases_present(self, raw_df):
        assert set(raw_df["Disease"].unique()) == set(DISEASES.keys())

    def test_no_null_values(self, raw_df):
        assert raw_df.isnull().sum().sum() == 0

    def test_symptom_name_count(self, raw_df):
        sym_cols = [c for c in raw_df.columns if c != "Disease"]
        assert len(sym_cols) == NUM_SYMPTOMS


# ─── Preprocessing Tests ──────────────────────────────────────────────────────

class TestDataPreprocessor:

    def test_pipeline_keys(self, pipeline_data):
        required = {"X_train", "X_test", "y_train", "y_test",
                    "feature_names", "class_names", "label_encoder", "scaler"}
        assert required.issubset(set(pipeline_data.keys()))

    def test_train_test_shapes_consistent(self, pipeline_data):
        assert pipeline_data["X_train"].shape[1] == pipeline_data["X_test"].shape[1]
        assert len(pipeline_data["y_train"]) == pipeline_data["X_train"].shape[0]
        assert len(pipeline_data["y_test"])  == pipeline_data["X_test"].shape[0]

    def test_no_data_leakage(self, pipeline_data, raw_df):
        """Train + test sizes should sum to the total dataset size."""
        total = len(pipeline_data["y_train"]) + len(pipeline_data["y_test"])
        assert total == len(raw_df)

    def test_label_encoding_complete(self, pipeline_data):
        """All class labels should be non-negative integers."""
        all_labels = np.concatenate([
            pipeline_data["y_train"].values,
            pipeline_data["y_test"].values,
        ])
        assert np.all(all_labels >= 0)
        assert len(pipeline_data["class_names"]) == len(DISEASES)

    def test_feature_names_length(self, pipeline_data):
        assert len(pipeline_data["feature_names"]) == NUM_SYMPTOMS

    def test_scaler_fitted(self, pipeline_data):
        """Scaler mean_ should be set after fitting."""
        assert hasattr(pipeline_data["scaler"], "mean_")

    def test_scaled_range(self, pipeline_data):
        """After StandardScaler the training data should be roughly zero-centred."""
        mean = pipeline_data["X_train"].mean()
        assert abs(mean) < 1.5, f"Training data mean too large: {mean}"


# ─── Model Trainer Tests (lightweight) ───────────────────────────────────────

class TestModelTrainer:

    def test_models_defined(self, pipeline_data):
        from src.model_trainer import ModelTrainer
        trainer = ModelTrainer(class_names=pipeline_data["class_names"])
        assert len(trainer.models) >= 3

    def test_train_returns_results(self, pipeline_data):
        from src.model_trainer import ModelTrainer
        trainer = ModelTrainer(class_names=pipeline_data["class_names"])
        results = trainer.train_all(
            pipeline_data["X_train"], pipeline_data["X_test"],
            pipeline_data["y_train"].values, pipeline_data["y_test"].values,
        )
        assert len(results) >= 3
        for name, res in results.items():
            assert 0.0 <= res["accuracy"] <= 1.0, f"Bad accuracy for {name}"
            assert 0.0 <= res["f1"]       <= 1.0, f"Bad F1 for {name}"

    def test_comparison_table_shape(self, pipeline_data):
        from src.model_trainer import ModelTrainer
        trainer = ModelTrainer(class_names=pipeline_data["class_names"])
        trainer.train_all(
            pipeline_data["X_train"], pipeline_data["X_test"],
            pipeline_data["y_train"].values, pipeline_data["y_test"].values,
        )
        table = trainer.get_comparison_table()
        assert table.shape[0] >= 3
        assert "Accuracy" in table.columns

    def test_best_model_selection(self, pipeline_data):
        from src.model_trainer import ModelTrainer
        trainer = ModelTrainer(class_names=pipeline_data["class_names"])
        trainer.train_all(
            pipeline_data["X_train"], pipeline_data["X_test"],
            pipeline_data["y_train"].values, pipeline_data["y_test"].values,
        )
        best = trainer.get_best_model_name("f1")
        assert best in trainer.results


# ─── Cleanup ──────────────────────────────────────────────────────────────────

def teardown_module(module):
    test_csv = os.path.join(ROOT, "data", "raw", "test_dataset.csv")
    if os.path.exists(test_csv):
        os.remove(test_csv)

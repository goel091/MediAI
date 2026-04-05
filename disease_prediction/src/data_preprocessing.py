"""
src/data_preprocessing.py
─────────────────────────────────────────────
End-to-end data cleaning, encoding, and scaling
pipeline for the Disease Prediction System.
─────────────────────────────────────────────
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils import resample

from src.logger import get_logger

logger = get_logger(__name__)


class DataPreprocessor:
    """
    Handles all preprocessing steps:
      1. Loading raw data
      2. Cleaning (missing values, duplicates, type fixes)
      3. Label encoding the target column
      4. Feature scaling
      5. Train / test splitting
      6. (Optional) Class balancing via oversampling
    """

    def __init__(
        self,
        target_col: str = "Disease",
        test_size: float = 0.20,
        random_state: int = 42,
        scaler_type: str = "standard",  # "standard" | "minmax"
    ):
        self.target_col = target_col
        self.test_size = test_size
        self.random_state = random_state
        self.scaler_type = scaler_type

        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler() if scaler_type == "standard" else None
        self.feature_names: list[str] = []
        self.class_names: list[str] = []

        # If minmax requested, import here
        if scaler_type == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            self.scaler = MinMaxScaler()

    # ──────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────────────────────────────────────

    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Loads CSV data from disk.

        Args:
            filepath (str): Path to the CSV file.

        Returns:
            pd.DataFrame: Raw dataframe.
        """
        logger.info(f"Loading data from: {filepath}")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset not found at: {filepath}")

        df = pd.read_csv(filepath)
        logger.info(f"Loaded dataset — Shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs data cleaning:
          - Strips whitespace from string columns
          - Drops exact duplicate rows
          - Fills missing values (0 for symptom binary columns)
          - Ensures binary symptom columns are int type

        Args:
            df (pd.DataFrame): Raw dataframe.

        Returns:
            pd.DataFrame: Cleaned dataframe.
        """
        logger.info("── Cleaning data ──")
        original_shape = df.shape

        # ── Strip whitespace from object columns ──
        str_cols = df.select_dtypes(include="object").columns
        for col in str_cols:
            df[col] = df[col].str.strip()

        # ── Log missing values ──
        missing = df.isnull().sum()
        if missing.any():
            logger.warning(f"Missing values detected:\n{missing[missing > 0]}")
            # Fill numeric columns with 0 (symptom not present)
            num_cols = df.select_dtypes(include=[np.number]).columns
            df[num_cols] = df[num_cols].fillna(0)
            # Fill categorical columns with mode
            cat_cols = df.select_dtypes(include="object").columns
            for col in cat_cols:
                df[col] = df[col].fillna(df[col].mode()[0])
        else:
            logger.info("No missing values found ✓")

        # ── Remove duplicates ──
        before_dedup = len(df)
        df = df.drop_duplicates()
        after_dedup = len(df)
        if before_dedup > after_dedup:
            logger.warning(f"Removed {before_dedup - after_dedup} duplicate rows")
        else:
            logger.info("No duplicate rows found ✓")

        # ── Ensure symptom columns are integer type ──
        symptom_cols = [c for c in df.columns if c != self.target_col]
        df[symptom_cols] = df[symptom_cols].astype(int)

        logger.info(f"Cleaned shape: {original_shape} → {df.shape}")
        return df.reset_index(drop=True)

    def encode_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Label-encodes the target column (disease names → integers).

        Args:
            df (pd.DataFrame): Cleaned dataframe.

        Returns:
            pd.DataFrame: Dataframe with encoded target.
        """
        logger.info("── Encoding target variable ──")
        df = df.copy()
        df[self.target_col] = self.label_encoder.fit_transform(df[self.target_col])
        self.class_names = list(self.label_encoder.classes_)
        logger.info(f"Number of disease classes: {len(self.class_names)}")
        logger.debug(f"Classes: {self.class_names}")
        return df

    def split_data(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Splits dataframe into train/test sets (stratified).

        Args:
            df (pd.DataFrame): Encoded dataframe.

        Returns:
            Tuple: (X_train, X_test, y_train, y_test)
        """
        logger.info(f"── Splitting data (test_size={self.test_size}) ──")

        X = df.drop(columns=[self.target_col])
        y = df[self.target_col]
        self.feature_names = list(X.columns)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y
        )

        logger.info(f"Train size: {X_train.shape[0]}  |  Test size: {X_test.shape[0]}")
        return X_train, X_test, y_train, y_test

    def scale_features(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Fits scaler on training data, transforms both train and test.

        Args:
            X_train (pd.DataFrame): Training features.
            X_test  (pd.DataFrame): Test features.

        Returns:
            Tuple: (X_train_scaled, X_test_scaled) as numpy arrays.
        """
        logger.info(f"── Scaling features ({self.scaler_type}) ──")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled  = self.scaler.transform(X_test)
        logger.info("Feature scaling complete ✓")
        return X_train_scaled, X_test_scaled

    def run_pipeline(
        self, filepath: str
    ) -> dict:
        """
        Convenience method: runs the full preprocessing pipeline
        and returns a dict with all artefacts.

        Args:
            filepath (str): Path to raw CSV.

        Returns:
            dict with keys:
              X_train, X_test, y_train, y_test (scaled arrays),
              X_train_raw, X_test_raw (unscaled DataFrames),
              df_clean, feature_names, class_names,
              label_encoder, scaler
        """
        df_raw   = self.load_data(filepath)
        df_clean = self.clean_data(df_raw)
        df_enc   = self.encode_target(df_clean)

        X_train_raw, X_test_raw, y_train, y_test = self.split_data(df_enc)
        X_train, X_test = self.scale_features(X_train_raw, X_test_raw)

        logger.info("✅ Preprocessing pipeline complete")

        return {
            "X_train": X_train,
            "X_test":  X_test,
            "y_train": y_train,
            "y_test":  y_test,
            "X_train_raw": X_train_raw,
            "X_test_raw":  X_test_raw,
            "df_clean":    df_clean,
            "feature_names": self.feature_names,
            "class_names":   self.class_names,
            "label_encoder": self.label_encoder,
            "scaler":        self.scaler,
        }

    def save_artefacts(self, save_dir: str = "models") -> None:
        """
        Saves the fitted label encoder and scaler to disk.

        Args:
            save_dir (str): Directory to save artefacts.
        """
        os.makedirs(save_dir, exist_ok=True)
        joblib.dump(self.label_encoder, os.path.join(save_dir, "label_encoder.pkl"))
        joblib.dump(self.scaler,        os.path.join(save_dir, "scaler.pkl"))
        logger.info(f"Saved label_encoder and scaler to '{save_dir}/'")


# ── Quick sanity check ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    from src.data_generator import generate_dataset

    # Generate dataset if needed
    raw_path = "data/raw/disease_dataset.csv"
    if not os.path.exists(raw_path):
        generate_dataset(save_path=raw_path)

    pp = DataPreprocessor()
    result = pp.run_pipeline(raw_path)

    print("\nPreprocessing Summary")
    print("─" * 40)
    print(f"X_train shape : {result['X_train'].shape}")
    print(f"X_test  shape : {result['X_test'].shape}")
    print(f"Classes       : {len(result['class_names'])}")
    print(f"Features      : {len(result['feature_names'])}")

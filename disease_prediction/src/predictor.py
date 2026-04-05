"""
src/predictor.py
─────────────────────────────────────────────
Production-ready inference module.

Loads saved model, scaler, and label encoder
and exposes a clean predict() API used by the
Streamlit app and any REST endpoint.
─────────────────────────────────────────────
"""

import os
import joblib
import numpy as np
import pandas as pd

from src.logger import get_logger

logger = get_logger(__name__)

# ── Default artefact paths ─────────────────────────────────────────────────────
DEFAULT_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


class DiseasePredictor:
    """
    Loads persisted ML artefacts and performs disease prediction.

    Args:
        models_dir (str): Directory containing saved artefacts.
        model_filename (str): Name of the model pickle file.
    """

    def __init__(
        self,
        models_dir: str = DEFAULT_MODELS_DIR,
        model_filename: str = "best_model.pkl",
    ):
        self.models_dir = models_dir
        self.model      = None
        self.scaler     = None
        self.label_enc  = None
        self.feature_names: list[str] = []
        self.class_names: list[str]   = []

        self._load_artefacts(model_filename)

    # ──────────────────────────────────────────────────────────────────────────

    def _load_artefacts(self, model_filename: str) -> None:
        """Loads model, scaler, label encoder, and feature/class names."""
        model_path = os.path.join(self.models_dir, model_filename)
        scaler_path = os.path.join(self.models_dir, "scaler.pkl")
        enc_path    = os.path.join(self.models_dir, "label_encoder.pkl")
        meta_path   = os.path.join(self.models_dir, "metadata.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please run the training pipeline first."
            )

        self.model     = joblib.load(model_path)
        self.scaler    = joblib.load(scaler_path)    if os.path.exists(scaler_path) else None
        self.label_enc = joblib.load(enc_path)       if os.path.exists(enc_path)    else None

        if os.path.exists(meta_path):
            meta = joblib.load(meta_path)
            self.feature_names = meta.get("feature_names", [])
            self.class_names   = meta.get("class_names",   [])

        if self.label_enc is not None and not self.class_names:
            self.class_names = list(self.label_enc.classes_)

        logger.info(
            f"Loaded model: {type(self.model).__name__} | "
            f"Classes: {len(self.class_names)} | "
            f"Features: {len(self.feature_names)}"
        )

    # ──────────────────────────────────────────────────────────────────────────

    def _build_feature_vector(
        self, symptoms_present: list[str]
    ) -> np.ndarray:
        """
        Converts a list of active symptom names into a binary feature vector.

        Args:
            symptoms_present (list[str]): Symptom names the patient has.

        Returns:
            np.ndarray: Shape (1, n_features).
        """
        if not self.feature_names:
            raise RuntimeError("Feature names not loaded from metadata.")

        vec = np.zeros(len(self.feature_names), dtype=float)
        not_found = []
        for sym in symptoms_present:
            sym_clean = sym.lower().replace(" ", "_").replace("-", "_")
            if sym_clean in self.feature_names:
                vec[self.feature_names.index(sym_clean)] = 1.0
            else:
                not_found.append(sym)

        if not_found:
            logger.warning(f"Symptoms not found in feature set: {not_found}")

        return vec.reshape(1, -1)

    def predict(
        self,
        symptoms_present: list[str],
        top_k: int = 5,
    ) -> dict:
        """
        Predicts the most likely disease(s) from a list of active symptoms.

        Args:
            symptoms_present (list[str]): Symptom names the patient reports.
            top_k (int): Number of top disease predictions to return.

        Returns:
            dict:
              - "primary_disease"  : str
              - "confidence"       : float (0–1)
              - "top_predictions"  : list of (disease, probability) tuples
              - "symptoms_used"    : list[str]
              - "risk_level"       : str  ("Low" / "Medium" / "High")
        """
        if not symptoms_present:
            raise ValueError("At least one symptom must be provided.")

        # ── Build feature vector ──
        X = self._build_feature_vector(symptoms_present)

        # ── Scale ──
        if self.scaler is not None:
            X = self.scaler.transform(X)

        # ── Predict probabilities ──
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X)[0]
        else:
            pred  = self.model.predict(X)[0]
            proba = np.zeros(len(self.class_names))
            proba[pred] = 1.0

        # ── Sort ──
        sorted_indices = np.argsort(proba)[::-1]
        top_indices    = sorted_indices[:top_k]

        primary_idx  = top_indices[0]
        primary_conf = float(proba[primary_idx])
        primary_dis  = self.class_names[primary_idx]

        top_preds = [
            (self.class_names[i], round(float(proba[i]) * 100, 2))
            for i in top_indices
        ]

        # ── Risk level heuristic ──
        risk_level = (
            "High"   if primary_conf >= 0.75 else
            "Medium" if primary_conf >= 0.45 else
            "Low"
        )

        return {
            "primary_disease":  primary_dis,
            "confidence":       round(primary_conf * 100, 2),
            "top_predictions":  top_preds,
            "symptoms_used":    symptoms_present,
            "risk_level":       risk_level,
        }

    def predict_from_dict(
        self,
        symptom_dict: dict[str, int],
        top_k: int = 5,
    ) -> dict:
        """
        Predicts from a dictionary of {symptom_name: 0_or_1}.

        Args:
            symptom_dict: All symptoms with binary values.
            top_k: Number of top results.

        Returns:
            Same dict as predict().
        """
        active = [k for k, v in symptom_dict.items() if v == 1]
        return self.predict(active, top_k=top_k)

    def get_all_symptoms(self) -> list[str]:
        """Returns the list of all known symptom feature names."""
        return self.feature_names

    def get_all_diseases(self) -> list[str]:
        """Returns the list of all disease class names."""
        return self.class_names

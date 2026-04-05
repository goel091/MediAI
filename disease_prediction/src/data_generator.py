"""
src/data_generator.py
─────────────────────────────────────────────
Generates a realistic synthetic disease-prediction
dataset when a real Kaggle download is unavailable.

The data mimics the UCI/Kaggle "Disease Symptom
Prediction" dataset structure with 132 binary symptom
columns and 1 multi-class disease label.
─────────────────────────────────────────────
"""

import os
import numpy as np
import pandas as pd
from src.logger import get_logger

logger = get_logger(__name__)

# ─── Disease definitions ───────────────────────────────────────────────────────
# Each disease has a list of "characteristic" symptom indices (out of 132).
# Patients with a disease will have those symptoms with high probability.

DISEASES = {
    "Fungal infection":        [0,  1,  2,  3,  4],
    "Allergy":                 [4,  5,  6,  7,  8],
    "GERD":                    [8,  9,  10, 11, 12],
    "Chronic cholestasis":     [12, 13, 14, 15, 16],
    "Drug Reaction":           [16, 17, 18, 19, 20],
    "Peptic ulcer disease":    [20, 21, 22, 23, 24],
    "AIDS":                    [24, 25, 26, 27, 28],
    "Diabetes":                [28, 29, 30, 31, 32],
    "Gastroenteritis":         [32, 33, 34, 35, 36],
    "Bronchial Asthma":        [36, 37, 38, 39, 40],
    "Hypertension":            [40, 41, 42, 43, 44],
    "Migraine":                [44, 45, 46, 47, 48],
    "Cervical spondylosis":    [48, 49, 50, 51, 52],
    "Paralysis (brain hemorrhage)": [52, 53, 54, 55, 56],
    "Jaundice":                [56, 57, 58, 59, 60],
    "Malaria":                 [60, 61, 62, 63, 64],
    "Chicken pox":             [64, 65, 66, 67, 68],
    "Dengue":                  [68, 69, 70, 71, 72],
    "Typhoid":                 [72, 73, 74, 75, 76],
    "Hepatitis A":             [76, 77, 78, 79, 80],
    "Hepatitis B":             [80, 81, 82, 83, 84],
    "Hepatitis C":             [84, 85, 86, 87, 88],
    "Hepatitis D":             [88, 89, 90, 91, 92],
    "Hepatitis E":             [92, 93, 94, 95, 96],
    "Alcoholic hepatitis":     [96, 97, 98, 99, 100],
    "Tuberculosis":            [100, 101, 102, 103, 104],
    "Common Cold":             [104, 105, 106, 107, 108],
    "Pneumonia":               [108, 109, 110, 111, 112],
    "Dimorphic hemorrhoids (piles)": [112, 113, 114, 115, 116],
    "Heart attack":            [116, 117, 118, 119, 120],
    "Varicose veins":          [120, 121, 122, 123, 124],
    "Hypothyroidism":          [124, 125, 126, 127, 128],
    "Hyperthyroidism":         [128, 129, 130, 131, 0],
    "Hypoglycemia":            [1,   30,  31,  40,  60],
    "Osteoarthritis":          [50,  51,  52,  53,  54],
    "Arthritis":               [50,  51,  52,  70,  71],
    "Vertigo (Paroxysmal Positional Vertigo)": [45, 46, 55, 56, 70],
    "Acne":                    [2,   3,   65,  66,  67],
    "Urinary tract infection": [9,   10,  33,  34,  35],
    "Psoriasis":               [0,   1,   2,   65,  66],
    "Impetigo":                [64,  65,  66,  67,  68],
}

NUM_SYMPTOMS = 132

SYMPTOM_NAMES = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing",
    "shivering", "chills", "joint_pain", "stomach_pain", "acidity",
    "ulcers_on_tongue", "muscle_wasting", "vomiting", "burning_micturition",
    "spotting_urination", "fatigue", "weight_gain", "anxiety",
    "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
    "lethargy", "patches_in_throat", "irregular_sugar_level", "cough",
    "high_fever", "sunken_eyes", "breathlessness", "sweating", "dehydration",
    "indigestion", "headache", "yellowish_skin", "dark_urine", "nausea",
    "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "constipation",
    "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
    "yellowing_of_eyes", "acute_liver_failure", "fluid_overload",
    "swelling_of_stomach", "swelled_lymph_nodes", "malaise",
    "blurred_and_distorted_vision", "phlegm", "throat_irritation",
    "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
    "chest_pain", "weakness_in_limbs", "fast_heart_rate",
    "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool",
    "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
    "obesity", "swollen_legs", "swollen_blood_vessels", "puffy_face_and_eyes",
    "enlarged_thyroid", "brittle_nails", "swollen_extremities",
    "excessive_hunger", "extra_marital_contacts", "drying_and_tingling_lips",
    "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness",
    "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements",
    "loss_of_balance", "unsteadiness", "weakness_of_one_body_side",
    "loss_of_smell", "bladder_discomfort", "foul_smell_of_urine",
    "continuous_feel_of_urine", "passage_of_gases", "internal_itching",
    "toxic_look_(typhos)", "depression", "irritability", "muscle_pain",
    "altered_sensorium", "red_spots_over_body", "belly_pain",
    "abnormal_menstruation", "dischromic_patches", "watering_from_eyes",
    "increased_appetite", "polyuria", "family_history", "mucoid_sputum",
    "rusty_sputum", "lack_of_concentration", "visual_disturbances",
    "receiving_blood_transfusion", "receiving_unsterile_injections", "coma",
    "stomach_bleeding", "distention_of_abdomen", "history_of_alcohol_consumption",
    "fluid_overload_1", "blood_in_sputum", "prominent_veins_on_calf",
    "palpitations", "painful_walking", "pus_filled_pimples", "blackheads",
    "scurring", "skin_peeling", "silver_like_dusting", "small_dents_in_nails",
    "inflammatory_nails", "blister", "red_sore_around_nose", "yellow_crust_ooze",
    "prognosis",
]
# Keep only first 132 as symptom names (last is the label placeholder)
SYMPTOM_NAMES = SYMPTOM_NAMES[:NUM_SYMPTOMS]


def generate_dataset(
    n_samples_per_disease: int = 120,
    noise_level: float = 0.05,
    random_state: int = 42,
    save_path: str = "data/raw/disease_dataset.csv"
) -> pd.DataFrame:
    """
    Generates a synthetic disease-symptom dataset.

    Args:
        n_samples_per_disease (int): Rows per disease class.
        noise_level (float): Probability of flipping a symptom bit (0–1).
        random_state (int): Seed for reproducibility.
        save_path (str): Where to persist the CSV.

    Returns:
        pd.DataFrame: Generated dataset.
    """
    np.random.seed(random_state)
    logger.info("Generating synthetic disease dataset …")

    rows = []
    labels = []

    for disease, char_symptoms in DISEASES.items():
        for _ in range(n_samples_per_disease):
            # ── Start with all-zero symptom vector ──
            symptom_vec = np.zeros(NUM_SYMPTOMS, dtype=int)

            # ── Activate characteristic symptoms with high probability ──
            for idx in char_symptoms:
                if idx < NUM_SYMPTOMS:
                    symptom_vec[idx] = 1 if np.random.rand() > 0.15 else 0

            # ── Add a few random co-occurring symptoms ──
            extra = np.random.choice(NUM_SYMPTOMS, size=np.random.randint(0, 4), replace=False)
            symptom_vec[extra] = 1

            # ── Apply noise (randomly flip bits) ──
            flip_mask = np.random.rand(NUM_SYMPTOMS) < noise_level
            symptom_vec[flip_mask] = 1 - symptom_vec[flip_mask]

            rows.append(symptom_vec)
            labels.append(disease)

    df = pd.DataFrame(rows, columns=SYMPTOM_NAMES)
    df["Disease"] = labels

    # ── Shuffle ──
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)

    # ── Persist ──
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    logger.info(f"Dataset saved → {save_path}  |  Shape: {df.shape}")

    return df


if __name__ == "__main__":
    df = generate_dataset()
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Diseases: {df['Disease'].nunique()}")

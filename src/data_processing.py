"""
src/data_processing.py
Data cleaning, preprocessing, feature engineering, and SMOTE balancing
for the AI4I 2020 Predictive Maintenance Dataset.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

try:
    from imblearn.over_sampling import SMOTE
    _HAS_SMOTE = True
except ImportError:
    _HAS_SMOTE = False
    print("[WARN] imbalanced-learn not installed — SMOTE will be skipped.")

try:
    import joblib
    _HAS_JOBLIB = True
except ImportError:
    import pickle as joblib  # type: ignore[no-redef]
    _HAS_JOBLIB = False
    print("[WARN] joblib not installed — falling back to pickle.")

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "Dataset", "ai4i2020.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
RANDOM_STATE = 42

FEATURE_COLS = [
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Temperature Difference",
    "Wear Rate",
    "Mechanical Load Index",
]

TARGET_COL = "Machine failure"


# ─────────────────────────────────────────────
# Load & clean
# ─────────────────────────────────────────────
def load_raw_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV and return a DataFrame."""
    df = pd.read_csv(path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Drop identifier columns
    - Remove duplicates
    - Drop rows with nulls
    - Encode Type column
    """
    df = df.copy()

    # Drop identifiers
    df.drop(columns=["UDI", "Product ID"], errors="ignore", inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Drop missing
    df.dropna(inplace=True)

    # Encode Type: L→0, M→1, H→2
    type_map = {"L": 0, "M": 1, "H": 2}
    df["Type"] = df["Type"].map(type_map).fillna(0).astype(int)

    return df


# ─────────────────────────────────────────────
# Feature engineering
# ─────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to the DataFrame."""
    df = df.copy()

    # Temperature Difference: how much hotter the process is vs ambient
    df["Temperature Difference"] = (
        df["Process temperature [K]"] - df["Air temperature [K]"]
    )

    # Wear Rate: tool wear accumulated per unit of rotational speed
    df["Wear Rate"] = df["Tool wear [min]"] / (df["Rotational speed [rpm]"] + 1e-6)

    # Mechanical Load Index: combined torque × wear proxy
    df["Mechanical Load Index"] = df["Torque [Nm]"] * df["Tool wear [min]"] / 1000.0

    return df


# ─────────────────────────────────────────────
# Train / Test split + SMOTE
# ─────────────────────────────────────────────
def prepare_datasets(df: pd.DataFrame, test_size: float = 0.2):
    """
    Split into train/test, apply StandardScaler, apply SMOTE to training set.

    Returns:
        X_train_res, X_test_scaled, y_train_res, y_test, scaler,
        class_counts_before, class_counts_after
    """
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # Counts before SMOTE
    unique, counts = np.unique(y, return_counts=True)
    class_counts_before = dict(zip(unique.tolist(), counts.tolist()))

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # SMOTE (or fallback to raw scaled training data)
    if _HAS_SMOTE:
        smote = SMOTE(random_state=RANDOM_STATE)
        X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
    else:
        print("[WARN] Skipping SMOTE — using raw scaled training data.")
        X_train_res, y_train_res = X_train_scaled, y_train

    unique_r, counts_r = np.unique(y_train_res, return_counts=True)
    class_counts_after = dict(zip(unique_r.tolist(), counts_r.tolist()))

    return (
        X_train_res,
        X_test_scaled,
        y_train_res,
        y_test,
        scaler,
        class_counts_before,
        class_counts_after,
    )


# ─────────────────────────────────────────────
# Full pipeline runner
# ─────────────────────────────────────────────
def run_pipeline(path: str = DATA_PATH):
    """End-to-end preprocessing. Returns all artefacts needed by model training."""
    df_raw = load_raw_data(path)
    df_clean = clean_data(df_raw)
    df_feat = engineer_features(df_clean)

    (
        X_train_res,
        X_test,
        y_train_res,
        y_test,
        scaler,
        counts_before,
        counts_after,
    ) = prepare_datasets(df_feat)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))

    return {
        "df_raw": df_raw,
        "df_clean": df_clean,
        "df_feat": df_feat,
        "X_train": X_train_res,
        "X_test": X_test,
        "y_train": y_train_res,
        "y_test": y_test,
        "scaler": scaler,
        "class_counts_before": counts_before,
        "class_counts_after": counts_after,
        "feature_cols": FEATURE_COLS,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print("Pipeline complete.")
    print("Class distribution before SMOTE:", result["class_counts_before"])
    print("Class distribution after  SMOTE:", result["class_counts_after"])
    print("Train shape:", result["X_train"].shape)
    print("Test  shape:", result["X_test"].shape)

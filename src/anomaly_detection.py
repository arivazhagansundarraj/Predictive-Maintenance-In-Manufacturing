"""
src/anomaly_detection.py
Isolation Forest-based anomaly detection for manufacturing sensor data.
"""

import os
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from src.data_processing import MODELS_DIR, FEATURE_COLS

RANDOM_STATE = 42
ISO_MODEL_PATH = os.path.join(MODELS_DIR, "isolation_forest.pkl")


# ─────────────────────────────────────────────
# Train
# ─────────────────────────────────────────────
def train_isolation_forest(X_train_normal: np.ndarray, contamination: float = 0.05):
    """
    Fit Isolation Forest on normal (no-failure) training samples.

    Parameters
    ----------
    X_train_normal : np.ndarray
        Scaled feature matrix — only rows where Machine failure == 0.
    contamination : float
        Expected proportion of outliers.

    Returns
    -------
    IsolationForest fitted model.
    """
    iso = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    iso.fit(X_train_normal)
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(iso, ISO_MODEL_PATH)
    return iso


# ─────────────────────────────────────────────
# Load & Predict
# ─────────────────────────────────────────────
def load_isolation_forest():
    return joblib.load(ISO_MODEL_PATH)


def predict_anomaly(iso_model, X: np.ndarray):
    """
    Return anomaly scores and binary labels for each sample.

    Returns
    -------
    scores : np.ndarray  – raw anomaly score (lower = more anomalous)
    labels : np.ndarray  – 1=normal, -1=anomaly (sklearn convention)
    normalized_scores : np.ndarray – [0,1] where 1 = most anomalous
    """
    labels = iso_model.predict(X)          # 1 = inlier, -1 = outlier
    scores = iso_model.score_samples(X)    # negative avg path length (more negative = more anomalous)

    # Normalize to [0, 1]: 0 = completely normal, 1 = maximally anomalous
    # Use fixed calibration bounds so single-sample calls work correctly.
    # Typical IF score_samples range: -0.7 (very anomalous) to -0.1 (very normal)
    SCORE_NORMAL = -0.10   # upper bound  → 0% anomaly
    SCORE_ANOMAL = -0.70   # lower bound  → 100% anomaly
    normalized = (SCORE_NORMAL - scores) / (SCORE_NORMAL - SCORE_ANOMAL)
    normalized = np.clip(normalized, 0.0, 1.0)

    return scores, labels, normalized


def iso_model_exists():
    return os.path.exists(ISO_MODEL_PATH)

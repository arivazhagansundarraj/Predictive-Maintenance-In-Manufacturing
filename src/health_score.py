"""
src/health_score.py
Compute a Machine Health Score [0–100].

Score composition:
  - Failure probability (inverted, weight 40 %)
  - Anomaly score      (inverted, weight 30 %)
  - Sensor deviation   (from healthy mean, weight 30 %)
"""

import numpy as np
import pandas as pd
from src.data_processing import FEATURE_COLS


# Healthy baseline ranges (approximate domain midpoints)
HEALTHY_MEANS = {
    "Air temperature [K]": 300.0,
    "Process temperature [K]": 310.0,
    "Rotational speed [rpm]": 1500.0,
    "Torque [Nm]": 40.0,
    "Tool wear [min]": 100.0,
    "Temperature Difference": 10.0,
    "Wear Rate": 0.07,
    "Mechanical Load Index": 4.0,
}

HEALTHY_STDS = {
    "Air temperature [K]": 2.0,
    "Process temperature [K]": 1.0,
    "Rotational speed [rpm]": 200.0,
    "Torque [Nm]": 10.0,
    "Tool wear [min]": 70.0,
    "Temperature Difference": 2.0,
    "Wear Rate": 0.05,
    "Mechanical Load Index": 3.0,
}


def compute_sensor_deviation_score(row_dict: dict) -> float:
    """
    Compute a [0, 1] sensor deviation penalty.
    0 = perfectly normal, 1 = extreme deviation.
    """
    z_scores = []
    for feat, mean in HEALTHY_MEANS.items():
        val = row_dict.get(feat)
        if val is None:
            continue
        std = HEALTHY_STDS.get(feat, 1.0)
        z = abs((val - mean) / (std + 1e-9))
        z_scores.append(z)

    if not z_scores:
        return 0.0

    avg_z = np.mean(z_scores)
    # Clip and normalize: z=0 → 0, z≥3 → 1
    deviation = float(np.clip(avg_z / 3.0, 0.0, 1.0))
    return deviation


def compute_health_score(
    failure_prob: float,
    anomaly_score_normalized: float,
    row_dict: dict | None = None,
) -> float:
    """
    Compute a Machine Health Score [0–100].

    Parameters
    ----------
    failure_prob : float [0, 1] – predicted failure probability
    anomaly_score_normalized : float [0, 1] – 0=normal, 1=anomaly
    row_dict : dict of feature values (optional, for sensor deviation)

    Returns
    -------
    health_score : float [0, 100]
    """
    sensor_dev = compute_sensor_deviation_score(row_dict) if row_dict else 0.0

    # Each component contributes a "health penalty" in [0, 1]
    failure_penalty = float(np.clip(failure_prob, 0.0, 1.0))
    anomaly_penalty = float(np.clip(anomaly_score_normalized, 0.0, 1.0))
    sensor_penalty = float(np.clip(sensor_dev, 0.0, 1.0))

    # Weighted combined health score
    composite_penalty = (
        0.40 * failure_penalty
        + 0.30 * anomaly_penalty
        + 0.30 * sensor_penalty
    )

    health_score = 100.0 * (1.0 - composite_penalty)
    return float(np.clip(health_score, 0.0, 100.0))


def batch_health_scores(
    failure_probs: np.ndarray,
    anomaly_scores: np.ndarray,
    df_features: pd.DataFrame | None = None,
) -> np.ndarray:
    """
    Compute health scores for an array of samples.

    Parameters
    ----------
    failure_probs : (N,) array
    anomaly_scores : (N,) normalized anomaly scores
    df_features : DataFrame with sensor columns (optional)
    """
    scores = []
    for i in range(len(failure_probs)):
        row_dict = (
            df_features.iloc[i].to_dict() if df_features is not None else None
        )
        s = compute_health_score(failure_probs[i], anomaly_scores[i], row_dict)
        scores.append(s)
    return np.array(scores)

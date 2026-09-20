"""
src/feature_importance.py
Extract and rank feature importances from a trained model.
"""

import pandas as pd
import numpy as np


def get_importance_df(model, feature_cols: list) -> pd.DataFrame:
    """
    Return a sorted DataFrame of feature importances.

    Parameters
    ----------
    model : trained classifier with feature_importances_ attribute
    feature_cols : list of feature names

    Returns
    -------
    pd.DataFrame with columns ['Feature', 'Importance']
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        importances = np.zeros(len(feature_cols))

    df = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": importances,
    }).sort_values("Importance", ascending=False).reset_index(drop=True)

    # Normalize to percentage
    total = df["Importance"].sum()
    if total > 0:
        df["Importance %"] = (df["Importance"] / total * 100).round(2)
    else:
        df["Importance %"] = 0.0

    return df

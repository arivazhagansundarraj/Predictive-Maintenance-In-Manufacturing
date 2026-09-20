"""
src/model_training.py
Train Random Forest, XGBoost, LightGBM, CatBoost.
Select best model by Recall + ROC-AUC and persist all artefacts.
"""

import os
import json
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)

# Optional boosting libraries — gracefully degrade if not installed
try:
    from xgboost import XGBClassifier
    _HAS_XGBOOST = True
except ImportError:
    _HAS_XGBOOST = False
    print("[WARN] xgboost not installed — skipping XGBoost model.")

try:
    from lightgbm import LGBMClassifier
    _HAS_LIGHTGBM = True
except ImportError:
    _HAS_LIGHTGBM = False
    print("[WARN] lightgbm not installed — skipping LightGBM model.")

try:
    from catboost import CatBoostClassifier
    _HAS_CATBOOST = True
except ImportError:
    _HAS_CATBOOST = False
    print("[WARN] catboost not installed — skipping CatBoost model.")

from src.data_processing import run_pipeline, FEATURE_COLS, MODELS_DIR

RANDOM_STATE = 42


# ─────────────────────────────────────────────
# Model definitions
# ─────────────────────────────────────────────
def get_models():
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }
    if _HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            scale_pos_weight=10,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            verbosity=0,
        )
    if _HAS_LIGHTGBM:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            verbose=-1,
        )
    if _HAS_CATBOOST:
        models["CatBoost"] = CatBoostClassifier(
            iterations=200,
            depth=6,
            learning_rate=0.05,
            auto_class_weights="Balanced",
            random_seed=RANDOM_STATE,
            verbose=0,
        )
    return models


# ─────────────────────────────────────────────
# Evaluation helpers
# ─────────────────────────────────────────────
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    fpr, tpr, roc_thresh = roc_curve(y_test, y_prob)
    prec_vals, rec_vals, pr_thresh = precision_recall_curve(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "confusion_matrix": cm.tolist(),
        "roc_fpr": fpr.tolist(),
        "roc_tpr": tpr.tolist(),
        "pr_precision": prec_vals.tolist(),
        "pr_recall": rec_vals.tolist(),
    }


# ─────────────────────────────────────────────
# Feature importance extraction
# ─────────────────────────────────────────────
def get_feature_importances(model, feature_cols):
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        importances = np.zeros(len(feature_cols))
    return dict(zip(feature_cols, importances.tolist()))


# ─────────────────────────────────────────────
# Main training routine
# ─────────────────────────────────────────────
def train_all_models(pipeline_data=None):
    if pipeline_data is None:
        pipeline_data = run_pipeline()

    X_train = pipeline_data["X_train"]
    X_test = pipeline_data["X_test"]
    y_train = pipeline_data["y_train"]
    y_test = pipeline_data["y_test"]
    feature_cols = pipeline_data["feature_cols"]

    models = get_models()
    all_metrics = {}
    best_model_name = None
    best_score = -1.0

    os.makedirs(MODELS_DIR, exist_ok=True)

    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        metrics["feature_importances"] = get_feature_importances(model, feature_cols)
        all_metrics[name] = metrics

        # Selection criterion: harmonic mean of Recall and ROC-AUC
        combined = 2 * metrics["recall"] * metrics["roc_auc"] / (
            metrics["recall"] + metrics["roc_auc"] + 1e-9
        )
        if combined > best_score:
            best_score = combined
            best_model_name = name

        # Persist individual model
        safe_name = name.lower().replace(" ", "_")
        joblib.dump(model, os.path.join(MODELS_DIR, f"{safe_name}.pkl"))

    # Persist best model reference
    best_model = models[best_model_name]
    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.pkl"))

    # Save metrics JSON
    summary = {
        "best_model": best_model_name,
        "models": all_metrics,
        "feature_cols": feature_cols,
        "class_counts_before": pipeline_data["class_counts_before"],
        "class_counts_after": pipeline_data["class_counts_after"],
    }
    with open(os.path.join(MODELS_DIR, "model_metrics.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Best model: {best_model_name} (score={best_score:.4f})")
    return summary


# ─────────────────────────────────────────────
# Loader helpers (used by Streamlit app)
# ─────────────────────────────────────────────
def load_best_model():
    path = os.path.join(MODELS_DIR, "best_model.pkl")
    return joblib.load(path)


def load_model_metrics():
    path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(path) as f:
        return json.load(f)


def load_scaler():
    path = os.path.join(MODELS_DIR, "scaler.pkl")
    return joblib.load(path)


def models_exist():
    return os.path.exists(os.path.join(MODELS_DIR, "best_model.pkl"))


if __name__ == "__main__":
    print("Starting model training pipeline...")
    summary = train_all_models()
    print("\nModel comparison:")
    for name, m in summary["models"].items():
        print(
            f"  {name:15s} | Recall={m['recall']:.4f} | ROC-AUC={m['roc_auc']:.4f} | F1={m['f1']:.4f}"
        )

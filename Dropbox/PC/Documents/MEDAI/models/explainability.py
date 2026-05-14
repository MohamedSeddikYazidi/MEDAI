"""
MedAI - SHAP Explainability Module
Generate SHAP explanations for model predictions.
"""

import sys
import json
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.config import settings

MODEL_DIR = Path(settings.MODEL_DIR)


def load_best_model():
    """Load the best trained model."""
    best_path = MODEL_DIR / "best_model.json"
    with open(best_path) as f:
        best_info = json.load(f)

    model_name = best_info["best_model"]
    model = joblib.load(MODEL_DIR / f"{model_name}_model.joblib")
    feature_names = json.load(open(MODEL_DIR / "feature_names.json"))
    scaler = joblib.load(MODEL_DIR / "scaler.joblib")

    return model, model_name, feature_names, scaler


def compute_shap_values(model, X_sample, feature_names, model_name="model"):
    """
    Compute SHAP values for a set of samples.
    Returns SHAP values and the explainer.
    """
    print(f"[*] Computing SHAP values for {model_name}...")

    if isinstance(X_sample, pd.DataFrame):
        X_array = X_sample.values
    else:
        X_array = np.array(X_sample)

    # Use TreeExplainer for tree-based models, KernelExplainer for others
    if model_name in ["xgboost", "random_forest", "lightgbm"]:
        explainer = shap.TreeExplainer(model)
    else:
        # For logistic regression, use a background sample
        background = X_array[:100]
        explainer = shap.LinearExplainer(model, background)

    shap_values = explainer.shap_values(X_array)

    # Handle multi-output SHAP values
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Class 1 (readmitted)

    return shap_values, explainer


def explain_single_prediction(
    model, features: dict, feature_names: list, scaler, model_name: str
) -> dict:
    """
    Generate SHAP explanation for a single patient prediction.
    Returns a dict with prediction, probability, and feature contributions.
    """
    # Prepare feature vector
    X = pd.DataFrame([features], columns=feature_names).fillna(0)
    X_scaled = pd.DataFrame(
        scaler.transform(X), columns=feature_names
    )

    # Predict
    prediction = int(model.predict(X_scaled)[0])
    probability = float(model.predict_proba(X_scaled)[0][1])

    # SHAP values
    shap_values, _ = compute_shap_values(model, X_scaled, feature_names, model_name)

    # Get top contributing features
    if shap_values.ndim == 1:
        sv = shap_values
    else:
        sv = shap_values[0]

    feature_contributions = []
    sorted_indices = np.argsort(np.abs(sv))[::-1]

    for idx in sorted_indices[:10]:  # Top 10 features
        feature_contributions.append({
            "feature": feature_names[idx],
            "value": float(X_scaled.iloc[0, idx]),
            "shap_value": float(sv[idx]),
            "impact": "increases risk" if sv[idx] > 0 else "decreases risk",
        })

    # Recalibrated risk thresholds based on clinical readmission risk
    # HIGH: >45% readmission probability (clinically significant)
    # MEDIUM: 25-45% readmission probability (moderate concern)
    # LOW: <25% readmission probability (baseline)
    if probability > 0.45:
        risk_level = "HIGH"
    elif probability > 0.25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Improved confidence calculation: distance from decision boundary (0.5)
    # Higher confidence when prediction is more certain
    confidence = abs(probability - 0.5) * 2  # Scales to 0-1 range
    
    return {
        "prediction": prediction,
        "probability": probability,
        "risk_level": risk_level,
        "confidence": float(confidence),
        "top_factors": feature_contributions,
        "model_used": model_name,
    }


def generate_shap_plots(model, X_sample, feature_names, model_name="model"):
    """Generate and save SHAP visualization plots."""
    plots_dir = MODEL_DIR / "plots"
    plots_dir.mkdir(exist_ok=True)

    shap_values, explainer = compute_shap_values(model, X_sample, feature_names, model_name)

    # Summary plot
    plt.figure(figsize=(12, 8))
    shap.summary_plot(
        shap_values,
        X_sample,
        feature_names=feature_names,
        show=False,
        max_display=20,
    )
    plt.title(f"SHAP Feature Importance - {model_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(plots_dir / f"shap_summary_{model_name}.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Bar plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_values,
        X_sample,
        feature_names=feature_names,
        plot_type="bar",
        show=False,
        max_display=20,
    )
    plt.title(f"SHAP Mean Impact - {model_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(plots_dir / f"shap_bar_{model_name}.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"[+] SHAP plots saved for {model_name}")


if __name__ == "__main__":
    from etl.loaders import load_diabetic_data
    from etl.transformers import prepare_ml_dataset

    model, model_name, feature_names, scaler = load_best_model()
    df = load_diabetic_data()
    X, y, _, _ = prepare_ml_dataset(df)

    # Use a sample for SHAP (SHAP on full dataset is slow)
    X_sample = X.sample(min(500, len(X)), random_state=42)
    generate_shap_plots(model, X_sample, feature_names, model_name)

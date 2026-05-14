"""
MedAI - ML Model Training Pipeline (Fast Version)
Trains multiple ML models for readmission prediction.
Optimized for speed: no GridSearch, sampled data, class weights instead of SMOTE.
"""

import sys
import os
import json
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from etl.loaders import load_diabetic_data
from etl.transformers import prepare_ml_dataset
from backend.config import settings


MODEL_DIR = Path(settings.MODEL_DIR)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Max rows to train on — keeps training fast (2-3 min)
SAMPLE_SIZE = int(os.getenv("TRAINING_SAMPLE_SIZE", 20000))


def get_models():
    """Define models with fixed good hyperparameters — no grid search."""
    return {
        "logistic_regression": LogisticRegression(
            max_iter=500, random_state=42, class_weight="balanced",
            C=0.1, solver="lbfgs",
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=15, min_samples_split=10,
            min_samples_leaf=5, random_state=42, class_weight="balanced",
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, scale_pos_weight=10,
            random_state=42, eval_metric="logloss", verbosity=0,
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=100, max_depth=8, learning_rate=0.1,
            num_leaves=31, subsample=0.8, random_state=42,
            is_unbalance=True, verbose=-1, n_jobs=-1,
        ),
    }


def train_and_evaluate(X_train, X_test, y_train, y_test, feature_names):
    """Train all models and evaluate — no hyperparameter tuning."""
    models = get_models()
    results = {}
    best_model_name = None
    best_auc = 0

    print("\n" + "=" * 60)
    print("[*] TRAINING ML MODELS (fast mode)")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n[*] Training: {name} ...")

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy":  float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall":    float(recall_score(y_test, y_pred, zero_division=0)),
            "f1":        float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc":   float(roc_auc_score(y_test, y_proba)),
        }

        results[name] = {"model": model, "metrics": metrics, "y_pred": y_pred, "y_proba": y_proba}

        print(f"   Accuracy:  {metrics['accuracy']:.4f}")
        print(f"   Precision: {metrics['precision']:.4f}")
        print(f"   Recall:    {metrics['recall']:.4f}")
        print(f"   F1:        {metrics['f1']:.4f}")
        print(f"   ROC AUC:   {metrics['roc_auc']:.4f}")

        if metrics["roc_auc"] > best_auc:
            best_auc = metrics["roc_auc"]
            best_model_name = name

    print(f"\n[+] Best model: {best_model_name} (ROC AUC: {best_auc:.4f})")
    return results, best_model_name


def save_models(results, scaler, feature_names, best_model_name):
    """Save trained models, scaler, and metadata."""
    print("\n[*] Saving models...")

    for name, data in results.items():
        joblib.dump(data["model"], MODEL_DIR / f"{name}_model.joblib")
        with open(MODEL_DIR / f"{name}_metrics.json", "w") as f:
            json.dump(data["metrics"], f, indent=2)
        print(f"   Saved: {name}")

    joblib.dump(scaler, MODEL_DIR / "scaler.joblib")

    with open(MODEL_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    with open(MODEL_DIR / "best_model.json", "w") as f:
        json.dump({
            "best_model": best_model_name,
            "metrics": results[best_model_name]["metrics"],
        }, f, indent=2)

    print(f"[+] All models saved to: {MODEL_DIR}")


def run_training():
    """Execute the full training pipeline."""
    print("=" * 60)
    print("[*] MedAI ML TRAINING PIPELINE (fast mode)")
    print(f"[*] Sample size: {SAMPLE_SIZE:,} rows")
    print("=" * 60)

    # Load data
    df = load_diabetic_data()

    # Sample for speed
    if len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=42)
        print(f"[*] Sampled {SAMPLE_SIZE:,} rows from {len(df):,} total")

    X, y, feature_names, scaler = prepare_ml_dataset(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[*] Train: {len(X_train):,} | Test: {len(X_test):,}")
    print(f"[*] Class balance — 0: {(y_train==0).sum():,} | 1: {(y_train==1).sum():,}")

    results, best_model = train_and_evaluate(X_train, X_test, y_train, y_test, feature_names)
    save_models(results, scaler, feature_names, best_model)

    print("\n" + "=" * 60)
    print("[+] TRAINING COMPLETE")
    print("=" * 60)

    return results, best_model


if __name__ == "__main__":
    run_training()
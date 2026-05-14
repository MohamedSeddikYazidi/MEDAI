"""
MedAI - Prediction Service
Loads trained models and provides prediction API for the agents.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import joblib

from backend.config import settings
from models.explainability import explain_single_prediction

MODEL_DIR = Path(settings.MODEL_DIR)


class PredictionService:
    """Service for loading models and making predictions."""

    def __init__(self):
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.best_model_name = None
        self._loaded = False

    def load(self):
        """Load all saved models and metadata."""
        if self._loaded:
            return

        try:
            # Load feature names
            with open(MODEL_DIR / "feature_names.json") as f:
                self.feature_names = json.load(f)

            # Load scaler
            self.scaler = joblib.load(MODEL_DIR / "scaler.joblib")

            # Load best model info
            with open(MODEL_DIR / "best_model.json") as f:
                best_info = json.load(f)
                self.best_model_name = best_info["best_model"]

            # Load all models
            for model_name in ["logistic_regression", "random_forest", "xgboost", "lightgbm"]:
                model_path = MODEL_DIR / f"{model_name}_model.joblib"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)

            self._loaded = True
            print(f"[+] Loaded {len(self.models)} models. Best: {self.best_model_name}")

        except Exception as e:
            print(f"[!] Warning: Could not load models: {e}")
            print("   Run 'python -m models.training' first to train models.")

    def predict(self, features: dict, model_name: str = None) -> dict:
        """
        Make a prediction for a single patient.
        
        Args:
            features: Dict of feature name → value
            model_name: Optional model to use. Defaults to best model.
        
        Returns:
            Dict with prediction, probability, risk_level, and explanations.
        """
        self.load()

        if not self.models:
            return {
                "error": "No trained models available. Run training first.",
                "prediction": None,
            }

        model_name = model_name or self.best_model_name
        model = self.models.get(model_name)

        if not model:
            return {"error": f"Model '{model_name}' not found."}

        return explain_single_prediction(
            model, features, self.feature_names, self.scaler, model_name
        )

    def predict_batch(self, features_list: list, model_name: str = None) -> list:
        """Make predictions for multiple patients."""
        return [self.predict(f, model_name) for f in features_list]

    def get_model_metrics(self, model_name: str = None) -> dict:
        """Get stored metrics for a model."""
        model_name = model_name or self.best_model_name
        metrics_path = MODEL_DIR / f"{model_name}_metrics.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                return json.load(f)
        return {"error": "Metrics not found"}

    def get_all_metrics(self) -> dict:
        """Get metrics for all trained models."""
        all_metrics = {}
        for name in self.models:
            all_metrics[name] = self.get_model_metrics(name)
        return all_metrics

    def get_available_models(self) -> list:
        """List available trained models."""
        self.load()
        return list(self.models.keys())


# Singleton instance
prediction_service = PredictionService()

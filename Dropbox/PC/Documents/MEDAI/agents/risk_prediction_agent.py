"""
MedAI - Risk Prediction Agent
Predicts medical risks using trained ML models with SHAP explanations.
"""

import json
from agents.base_agent import BaseAgent, AgentResponse
from agents.llm_provider import call_llm


class RiskPredictionAgent(BaseAgent):
    """Agent for predicting medical risks using ML models."""

    def __init__(self):
        super().__init__(
            name="Risk Prediction Agent",
            description="Predicts readmission risk and complications using trained ML models."
        )
        self._prediction_service = None

    def _get_predictor(self):
        """Lazy load prediction service."""
        if self._prediction_service is None:
            from models.predictor import prediction_service
            self._prediction_service = prediction_service
        return self._prediction_service

    def get_capabilities(self) -> list[str]:
        return [
            "readmission_prediction", "risk_scoring",
            "shap_explanation", "model_comparison",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Predict medical risks.
        Input: {"features": dict, "model_name": str (optional)}
        """
        try:
            features = input_data.get("features", {})
            model_name = input_data.get("model_name")

            if not features:
                # Generate sample features from patient info
                features = self._build_features_from_patient(input_data)

            predictor = self._get_predictor()
            result = predictor.predict(features, model_name)

            if "error" in result:
                # Fallback: Use rule-based risk assessment
                print(f"[!] Model prediction failed: {result['error']}")
                result = self._rule_based_risk_assessment(features)
                result["warning"] = "Using rule-based assessment (models not available)"

            # Generate human-readable explanation via LLM
            explanation_prompt = f"""Based on this medical risk prediction, provide a concise clinical summary:

Prediction: {"HIGH RISK of readmission" if result['prediction'] == 1 else "LOW RISK of readmission"}
Probability: {result['probability']:.1%}
Risk Level: {result['risk_level']}

Top Contributing Factors:
{json.dumps(result['top_factors'][:5], indent=2)}

Write a 2-3 sentence clinical summary explaining the risk assessment in plain medical language. Return ONLY the summary text."""

            clinical_summary = await call_llm(explanation_prompt)

            result["clinical_summary"] = clinical_summary
            if "model_used" in result:
                result["model_metrics"] = predictor.get_model_metrics(result.get("model_used"))

            return self._create_response(
                data=result,
                confidence=result.get("confidence", 0.5),
                reasoning=clinical_summary,
            )

        except Exception as e:
            return self._error_response(f"Prediction error: {str(e)}")

    def _build_features_from_patient(self, input_data: dict) -> dict:
        """Build ML feature dict from patient/encounter data with validation."""
        # Define feature defaults and track missing features
        feature_defaults = {
            "age_numeric": 55,
            "time_in_hospital": 4,
            "num_lab_procedures": 40,
            "num_procedures": 1,
            "num_medications": 12,
            "number_outpatient": 0,
            "number_emergency": 0,
            "number_inpatient": 0,
            "number_diagnoses": 7,
            "active_med_count": 2,
            "total_visits": 0,
            "med_change": 0,
            "has_diabetes_med": 1,
            "lab_intensity": 2,
            "emergency_admission": 0,
            "a1c_numeric": 0,
            "glu_numeric": 0,
            "diabetes_primary": 1,
            "race_encoded": 0,
            "gender_encoded": 0,
            "diag_1_category_encoded": 0,
            "diag_2_category_encoded": 0,
            "diag_3_category_encoded": 0,
            "admission_type_id": 1,
            "discharge_disposition_id": 1,
            "admission_source_id": 7,
        }
        
        missing_features = []
        features = {}
        
        for feature, default in feature_defaults.items():
            if feature not in input_data:
                missing_features.append(feature)
            features[feature] = input_data.get(feature, default)
        
        if missing_features:
            print(f"[WARNING] Missing {len(missing_features)} features: {missing_features[:5]}...")
            print(f"         Using defaults for missing features. Confidence may be reduced.")
        
        return features

    def _rule_based_risk_assessment(self, features: dict) -> dict:
        """
        Fallback rule-based risk assessment when ML models are unavailable.
        Uses clinical heuristics to estimate readmission risk.
        """
        risk_score = 0.0
        risk_factors = []
        
        # Age factor: older patients have higher risk
        age = features.get("age_numeric", 55)
        if age > 75:
            risk_score += 0.15
            risk_factors.append("Advanced age (>75 years)")
        elif age > 65:
            risk_score += 0.10
            risk_factors.append("Age >65 years")
        
        # Hospital stay duration: longer stays indicate severity
        time_in_hospital = features.get("time_in_hospital", 4)
        if time_in_hospital > 7:
            risk_score += 0.15
            risk_factors.append(f"Extended hospital stay ({time_in_hospital} days)")
        elif time_in_hospital > 5:
            risk_score += 0.08
            risk_factors.append(f"Moderate hospital stay ({time_in_hospital} days)")
        
        # Number of diagnoses: more diagnoses = more comorbidities
        num_diagnoses = features.get("number_diagnoses", 7)
        if num_diagnoses > 10:
            risk_score += 0.15
            risk_factors.append(f"High comorbidity burden ({num_diagnoses} diagnoses)")
        elif num_diagnoses > 7:
            risk_score += 0.08
            risk_factors.append(f"Moderate comorbidities ({num_diagnoses} diagnoses)")
        
        # Medication count: more medications = more complex management
        num_medications = features.get("num_medications", 12)
        if num_medications > 20:
            risk_score += 0.12
            risk_factors.append(f"Complex medication regimen ({num_medications} medications)")
        elif num_medications > 15:
            risk_score += 0.06
            risk_factors.append(f"Multiple medications ({num_medications})")
        
        # Emergency admission: emergency admissions have higher readmission risk
        emergency_admission = features.get("emergency_admission", 0)
        if emergency_admission == 1:
            risk_score += 0.15
            risk_factors.append("Emergency admission")
        
        # Prior visits: frequent visitors have higher risk
        total_visits = features.get("total_visits", 0)
        if total_visits > 10:
            risk_score += 0.12
            risk_factors.append(f"Frequent prior visits ({total_visits})")
        elif total_visits > 5:
            risk_score += 0.06
            risk_factors.append(f"Multiple prior visits ({total_visits})")
        
        # Lab procedures: high intensity indicates severity
        lab_intensity = features.get("lab_intensity", 2)
        if lab_intensity > 3:
            risk_score += 0.10
            risk_factors.append("High lab procedure intensity")
        
        # Diabetes medication: indicates diabetes management complexity
        has_diabetes_med = features.get("has_diabetes_med", 1)
        if has_diabetes_med == 1:
            risk_score += 0.08
            risk_factors.append("On diabetes medication")
        
        # Medication changes: recent changes indicate instability
        med_change = features.get("med_change", 0)
        if med_change == 1:
            risk_score += 0.10
            risk_factors.append("Recent medication changes")
        
        # Glucose and A1C levels (if available)
        a1c = features.get("a1c_numeric", 0)
        glu = features.get("glu_numeric", 0)
        if a1c > 8:  # Poor glycemic control
            risk_score += 0.12
            risk_factors.append(f"Poor glycemic control (A1C: {a1c})")
        if glu > 200:  # High glucose
            risk_score += 0.10
            risk_factors.append(f"Elevated glucose ({glu} mg/dL)")
        
        # Cap risk score at 0.95
        probability = min(risk_score, 0.95)
        
        # Determine risk level
        if probability > 0.45:
            risk_level = "HIGH"
        elif probability > 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "prediction": 1 if probability > 0.5 else 0,
            "probability": probability,
            "risk_level": risk_level,
            "confidence": abs(probability - 0.5) * 2,
            "top_factors": [
                {"feature": factor, "impact": "increases risk", "shap_value": 0.0}
                for factor in risk_factors
            ],
            "model_used": "rule_based_fallback",
        }

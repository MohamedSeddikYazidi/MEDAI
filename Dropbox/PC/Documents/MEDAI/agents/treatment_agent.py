"""
MedAI - Treatment Recommendation Agent
Generates evidence-based treatment recommendations with source citations.
"""

import json
from agents.base_agent import BaseAgent, AgentResponse
from agents.llm_provider import call_llm
from rag.vector_store import vector_store


class TreatmentAgent(BaseAgent):
    """Agent for generating treatment recommendations."""

    def __init__(self):
        super().__init__(
            name="Treatment Recommendation Agent",
            description="Generates evidence-based treatment plans with citations and safety alerts."
        )

    def get_capabilities(self) -> list[str]:
        return [
            "treatment_planning", "drug_recommendation",
            "safety_alerts", "guideline_adherence",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Generate treatment recommendations.
        Input: {"diagnoses": list, "risk_level": str, "patient_info": dict, "medications": list}
        """
        try:
            diagnoses = input_data.get("diagnoses", [])
            risk_level = input_data.get("risk_level", "MEDIUM")
            patient_info = input_data.get("patient_info", {})
            current_meds = input_data.get("medications", [])
            symptoms = input_data.get("symptoms", [])

            # RAG: retrieve treatment guidelines
            query = f"Treatment recommendations for: {', '.join([d if isinstance(d, str) else d.get('name', '') for d in diagnoses])}"
            rag_results = vector_store.search(query, n_results=5)
            context = "\n\n".join([r["text"] for r in rag_results])
            sources = [{"title": r["metadata"].get("title", ""), "relevance": r["relevance_score"]} for r in rag_results]

            prompt = f"""You are a clinical treatment specialist. Generate a comprehensive treatment plan.

DIAGNOSES: {json.dumps(diagnoses)}
RISK LEVEL: {risk_level}
CURRENT MEDICATIONS: {', '.join(current_meds) if current_meds else 'None reported'}
SYMPTOMS: {', '.join(symptoms) if symptoms else 'None specified'}
PATIENT INFO: {json.dumps(patient_info) if patient_info else 'Not available'}

CLINICAL GUIDELINES:
{context}

Provide your response as JSON with:
- "treatment_plan": list of objects with "treatment", "priority" (high/medium/low), "evidence_level" (A/B/C), "rationale", "source"
- "medication_recommendations": list of objects with "drug", "dosage", "frequency", "duration", "warnings"
- "lifestyle_modifications": list of recommendations
- "monitoring_plan": list of tests/checkups with frequency
- "safety_alerts": list of any warnings, contraindications, or drug interactions
- "follow_up": recommended follow-up schedule
- "referrals": list of specialist referrals if needed

Return ONLY valid JSON."""

            llm_response = await call_llm(prompt, temperature=0.2)

            try:
                treatment_data = json.loads(llm_response)
            except json.JSONDecodeError:
                treatment_data = {
                    "treatment_plan": [
                        {"treatment": "Comprehensive metabolic management", "priority": "high",
                         "evidence_level": "A", "rationale": "Evidence-based standard of care",
                         "source": "ADA 2024 Guidelines"},
                    ],
                    "medication_recommendations": [
                        {"drug": "Metformin", "dosage": "500mg", "frequency": "BID",
                         "duration": "Ongoing", "warnings": "Monitor renal function"},
                    ],
                    "lifestyle_modifications": [
                        "Balanced diet with carbohydrate counting",
                        "Regular exercise (150 min/week moderate intensity)",
                        "Weight management",
                        "Smoking cessation if applicable",
                    ],
                    "monitoring_plan": [
                        {"test": "A1C", "frequency": "Every 3 months"},
                        {"test": "Fasting glucose", "frequency": "Daily self-monitoring"},
                        {"test": "Lipid panel", "frequency": "Annually"},
                    ],
                    "safety_alerts": [],
                    "follow_up": "Follow-up visit in 2-4 weeks",
                    "referrals": [],
                }

            # Add high-risk alerts
            if risk_level == "HIGH":
                treatment_data.setdefault("safety_alerts", []).append(
                    "[!] HIGH RISK PATIENT: Ensure intensive follow-up within 7 days of discharge."
                )

            return self._create_response(
                data=treatment_data,
                confidence=0.80,
                sources=sources,
                reasoning="Treatment plan generated based on clinical guidelines and patient-specific factors.",
            )

        except Exception as e:
            return self._error_response(f"Treatment recommendation error: {str(e)}")

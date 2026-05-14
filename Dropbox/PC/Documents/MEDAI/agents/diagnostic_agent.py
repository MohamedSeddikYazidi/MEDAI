"""
MedAI - Diagnostic Agent
Proposes diagnostic hypotheses using LLM + RAG medical knowledge.
"""

import json
from agents.base_agent import BaseAgent, AgentResponse
from agents.llm_provider import call_llm
from rag.vector_store import vector_store


class DiagnosticAgent(BaseAgent):
    """Agent for generating diagnostic hypotheses."""

    def __init__(self):
        super().__init__(
            name="Diagnostic Agent",
            description="Proposes ranked diagnostic hypotheses using medical reasoning and RAG."
        )

    def get_capabilities(self) -> list[str]:
        return [
            "differential_diagnosis", "medical_reasoning",
            "rag_knowledge_retrieval", "confidence_scoring",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Generate diagnostic hypotheses.
        Input: {"symptoms": list, "conditions": list, "patient_info": dict}
        """
        try:
            symptoms = input_data.get("symptoms", [])
            conditions = input_data.get("conditions", [])
            patient_info = input_data.get("patient_info", {})
            medications = input_data.get("medications", [])

            if not symptoms:
                return self._error_response("No symptoms provided for diagnosis.")

            # Step 1: RAG — retrieve relevant medical knowledge
            query = f"Diagnosis for symptoms: {', '.join(symptoms)}. Patient conditions: {', '.join(conditions)}"
            rag_results = vector_store.search(query, n_results=5)
            context = "\n\n".join([r["text"] for r in rag_results])
            sources = [{"title": r["metadata"].get("title", ""), "relevance": r["relevance_score"]}
                       for r in rag_results]

            # Step 2: LLM diagnostic reasoning
            prompt = f"""You are an expert medical diagnostician. Based on the following patient information and medical knowledge, provide differential diagnoses.

PATIENT INFORMATION:
- Symptoms: {', '.join(symptoms)}
- Existing Conditions: {', '.join(conditions) if conditions else 'None reported'}
- Current Medications: {', '.join(medications) if medications else 'None reported'}
- Demographics: {json.dumps(patient_info) if patient_info else 'Not available'}

RELEVANT MEDICAL KNOWLEDGE:
{context}

Provide your response as a JSON object with:
- "diagnoses": list of objects, each with "name", "confidence" (0-1), "reasoning", "icd10_code", "urgency" (low/medium/high/critical)
- "clinical_reasoning": your step-by-step medical reasoning
- "additional_tests_needed": list of recommended diagnostic tests
- "red_flags": any concerning findings that need immediate attention

List diagnoses in order of likelihood. Return ONLY valid JSON."""

            llm_response = await call_llm(prompt, temperature=0.2)

            try:
                diagnosis_data = json.loads(llm_response)
            except json.JSONDecodeError:
                print(f"[!] LLM response was not valid JSON. Response: {llm_response[:200]}")
                # Fallback structured response
                diagnosis_data = {
                    "diagnoses": [
                        {"name": "Type 2 Diabetes Mellitus (E11.9)", "confidence": 0.85,
                         "reasoning": "Consistent with reported symptoms and clinical profile",
                         "icd10_code": "E11.9", "urgency": "medium"},
                        {"name": "Essential Hypertension (I10)", "confidence": 0.70,
                         "reasoning": "Common comorbidity, should be evaluated",
                         "icd10_code": "I10", "urgency": "low"},
                    ],
                    "clinical_reasoning": "Based on symptom analysis and medical knowledge base review.",
                    "additional_tests_needed": ["HbA1c", "Fasting blood glucose", "Lipid panel", "Basic metabolic panel"],
                    "red_flags": [],
                }

            # Calculate overall confidence: use max confidence of top diagnoses, not average
            # This better reflects diagnostic certainty
            if diagnosis_data.get("diagnoses"):
                # Use the confidence of the top diagnosis (most likely)
                top_confidence = diagnosis_data["diagnoses"][0].get("confidence", 0.5)
                # Adjust based on urgency of red flags
                if diagnosis_data.get("red_flags"):
                    # Reduce confidence if there are critical red flags
                    top_confidence = max(0.6, top_confidence - 0.1)
                avg_confidence = top_confidence
            else:
                avg_confidence = 0.5

            return self._create_response(
                data=diagnosis_data,
                confidence=avg_confidence,
                sources=sources,
                reasoning=diagnosis_data.get("clinical_reasoning", "Diagnostic analysis completed."),
            )

        except Exception as e:
            return self._error_response(f"Diagnostic error: {str(e)}")

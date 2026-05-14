"""
MedAI - Patient Intake Agent
Processes patient symptoms using NLP, extracts medical entities,
and structures patient data for downstream agents.
"""

import re
import json
from agents.base_agent import BaseAgent, AgentResponse
from agents.llm_provider import call_llm


# Medical entity patterns for rule-based NER
SYMPTOM_PATTERNS = [
    r'\b(headache|migraine|cephalgia)\b', r'\b(fever|pyrexia|high temperature)\b',
    r'\b(cough|tussis)\b', r'\b(nausea|vomiting|emesis)\b',
    r'\b(fatigue|tiredness|exhaustion|lethargy)\b',
    r'\b(chest pain|angina|thoracic pain)\b', r'\b(shortness of breath|dyspnea|breathlessness)\b',
    r'\b(dizziness|vertigo|lightheadedness)\b', r'\b(pain|ache|discomfort|soreness)\b',
    r'\b(swelling|edema|inflammation)\b', r'\b(numbness|tingling|paresthesia)\b',
    r'\b(blurred vision|visual disturbance)\b', r'\b(polyuria|frequent urination)\b',
    r'\b(polydipsia|excessive thirst)\b', r'\b(weight loss|weight gain)\b',
    r'\b(hyperglycemia|high blood sugar)\b', r'\b(hypoglycemia|low blood sugar)\b',
    r'\b(diabetic ketoacidosis|DKA)\b', r'\b(abdominal pain|stomach pain)\b',
    r'\b(diarrhea|constipation)\b', r'\b(insomnia|sleep disorder)\b',
]

MEDICATION_PATTERNS = [
    r'\b(metformin|glucophage)\b', r'\b(insulin|lantus|humalog|novolog)\b',
    r'\b(glipizide|glucotrol)\b', r'\b(glyburide|diabeta)\b',
    r'\b(pioglitazone|actos)\b', r'\b(sitagliptin|januvia)\b',
    r'\b(empagliflozin|jardiance)\b', r'\b(semaglutide|ozempic)\b',
    r'\b(lisinopril|enalapril)\b', r'\b(atorvastatin|lipitor)\b',
    r'\b(aspirin)\b', r'\b(amlodipine|norvasc)\b',
]

CONDITION_PATTERNS = [
    r'\b(diabetes|diabetic)\b', r'\b(hypertension|high blood pressure)\b',
    r'\b(heart failure|cardiac failure)\b', r'\b(kidney disease|renal disease|CKD)\b',
    r'\b(obesity|overweight)\b', r'\b(stroke|CVA|cerebrovascular)\b',
    r'\b(neuropathy)\b', r'\b(retinopathy)\b', r'\b(nephropathy)\b',
    r'\b(coronary artery disease|CAD)\b', r'\b(COPD|chronic obstructive)\b',
    r'\b(anemia)\b', r'\b(depression|anxiety)\b',
]


class PatientIntakeAgent(BaseAgent):
    """Agent for processing patient intake and extracting medical entities."""

    def __init__(self):
        super().__init__(
            name="Patient Intake Agent",
            description="Processes patient symptoms, extracts medical entities, and structures clinical data."
        )

    def get_capabilities(self) -> list[str]:
        return [
            "symptom_extraction", "medication_recognition",
            "condition_detection", "urgency_assessment",
            "patient_data_structuring",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Process patient intake data.
        Input: {"symptoms": str, "patient_info": dict (optional)}
        """
        try:
            symptoms_text = input_data.get("symptoms", "")
            patient_info = input_data.get("patient_info", {})

            if not symptoms_text:
                return self._error_response("No symptoms text provided.")

            # Step 1: Rule-based NER
            entities = self._extract_entities(symptoms_text)

            # Step 2: LLM-enhanced extraction
            llm_prompt = f"""Analyze the following patient description and extract structured medical information.
Return a JSON object with these fields:
- "symptoms": list of identified symptoms
- "medications": list of current medications mentioned
- "conditions": list of existing conditions mentioned
- "urgency": "low", "medium", "high", or "critical"
- "urgency_reasoning": brief explanation
- "key_findings": list of important clinical observations
- "recommended_tests": list of tests that should be considered

Patient description: {symptoms_text}

Additional patient info: {json.dumps(patient_info) if patient_info else 'None provided'}

Return ONLY valid JSON, no extra text."""

            llm_response = await call_llm(llm_prompt)

            # Parse LLM response
            try:
                llm_data = json.loads(llm_response)
            except json.JSONDecodeError:
                llm_data = {}

            # Merge rule-based and LLM results
            merged = {
                "symptoms": list(set(entities["symptoms"] + llm_data.get("symptoms", []))),
                "medications": list(set(entities["medications"] + llm_data.get("medications", []))),
                "conditions": list(set(entities["conditions"] + llm_data.get("conditions", []))),
                "urgency": llm_data.get("urgency", self._assess_urgency(entities)),
                "urgency_reasoning": llm_data.get("urgency_reasoning", ""),
                "key_findings": llm_data.get("key_findings", []),
                "recommended_tests": llm_data.get("recommended_tests", []),
                "raw_text": symptoms_text,
                "patient_info": patient_info,
            }

            confidence = min(0.95, 0.5 + 0.05 * len(merged["symptoms"]) + 0.1 * (1 if llm_data else 0))

            return self._create_response(
                data=merged,
                confidence=confidence,
                reasoning=f"Extracted {len(merged['symptoms'])} symptoms, {len(merged['medications'])} medications, "
                         f"{len(merged['conditions'])} conditions. Urgency: {merged['urgency']}.",
            )

        except Exception as e:
            return self._error_response(f"Intake processing error: {str(e)}")

    def _extract_entities(self, text: str) -> dict:
        """Extract medical entities using regex patterns."""
        text_lower = text.lower()
        entities = {"symptoms": [], "medications": [], "conditions": []}

        for pattern in SYMPTOM_PATTERNS:
            matches = re.findall(pattern, text_lower)
            entities["symptoms"].extend(matches)

        for pattern in MEDICATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            entities["medications"].extend(matches)

        for pattern in CONDITION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            entities["conditions"].extend(matches)

        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def _assess_urgency(self, entities: dict) -> str:
        """Rule-based urgency assessment."""
        critical_symptoms = {"chest pain", "shortness of breath", "diabetic ketoacidosis", "dka"}
        high_symptoms = {"hyperglycemia", "hypoglycemia", "blurred vision", "numbness"}

        symptoms_set = set(s.lower() for s in entities.get("symptoms", []))

        if symptoms_set & critical_symptoms:
            return "critical"
        elif symptoms_set & high_symptoms:
            return "high"
        elif len(entities.get("symptoms", [])) >= 4:
            return "medium"
        return "low"

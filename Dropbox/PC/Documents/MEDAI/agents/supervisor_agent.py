"""
MedAI - Supervisor / Orchestrator Agent
Coordinates all agents, manages workflows, and aggregates responses.
"""

import json
import time
from agents.base_agent import BaseAgent, AgentResponse
from agents.patient_intake_agent import PatientIntakeAgent
from agents.diagnostic_agent import DiagnosticAgent
from agents.risk_prediction_agent import RiskPredictionAgent
from agents.rag_agent import RAGAgent
from agents.treatment_agent import TreatmentAgent
from agents.bi_agent import BIAgent
from agents.llm_provider import call_llm


class SupervisorAgent(BaseAgent):
    """Orchestrator that coordinates all specialized agents."""

    def __init__(self):
        super().__init__(
            name="Supervisor Agent",
            description="Coordinates all medical AI agents and synthesizes results."
        )
        # Initialize all sub-agents
        self.agents = {
            "intake": PatientIntakeAgent(),
            "diagnostic": DiagnosticAgent(),
            "risk": RiskPredictionAgent(),
            "rag": RAGAgent(),
            "treatment": TreatmentAgent(),
            "bi": BIAgent(),
        }

    def get_capabilities(self) -> list[str]:
        return [
            "workflow_orchestration", "agent_coordination",
            "response_aggregation", "query_routing",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Route and orchestrate agent workflows.
        Input: {"query": str, "query_type": str, "data": dict}
        """
        try:
            query = input_data.get("query", "")
            query_type = input_data.get("query_type", "auto")

            # Auto-detect query type if not specified
            if query_type == "auto":
                query_type = self._classify_query(query)

            handlers = {
                "full_analysis": self._full_analysis,
                "diagnosis": self._diagnosis_only,
                "risk_prediction": self._risk_only,
                "knowledge_search": self._knowledge_search,
                "treatment": self._treatment_only,
                "analytics": self._analytics_only,
                "chat": self._chat_response,
            }

            handler = handlers.get(query_type, self._chat_response)
            return await handler(input_data)

        except Exception as e:
            return self._error_response(f"Orchestration error: {str(e)}")

    def _classify_query(self, query: str) -> str:
        """Classify the type of query based on keywords."""
        q = query.lower()
        if any(w in q for w in ["symptom", "patient", "complain", "feel"]):
            return "full_analysis"
        elif any(w in q for w in ["diagnos", "what is", "condition"]):
            return "diagnosis"
        elif any(w in q for w in ["risk", "predict", "readmission", "probability"]):
            return "risk_prediction"
        elif any(w in q for w in ["treat", "medication", "prescri", "recommend"]):
            return "treatment"
        elif any(w in q for w in ["dashboard", "analytics", "kpi", "statistic", "trend"]):
            return "analytics"
        elif any(w in q for w in ["what", "how", "why", "guide", "protocol"]):
            return "knowledge_search"
        return "chat"

    async def _full_analysis(self, input_data: dict) -> AgentResponse:
        """Run the complete multi-agent analysis pipeline."""
        start = time.time()
        results = {}
        query = input_data.get("query", "")
        patient_info = input_data.get("patient_info", {})

        # Step 1: Patient Intake
        intake_result = await self.agents["intake"].process({
            "symptoms": query,
            "patient_info": patient_info,
        })
        results["intake"] = intake_result.data

        # Step 2: Diagnosis (using intake output)
        symptoms = intake_result.data.get("symptoms", [])
        if not symptoms:
            symptoms = [query]  # fallback to raw query

        diag_result = await self.agents["diagnostic"].process({
            "symptoms": symptoms,
            "conditions": intake_result.data.get("conditions", []),
            "medications": intake_result.data.get("medications", []),
            "patient_info": patient_info,
        })
        results["diagnosis"] = diag_result.data

        # Step 3: Risk Prediction
        risk_result = await self.agents["risk"].process({
            **patient_info,
            "features": input_data.get("features", {}),
        })
        results["risk"] = risk_result.data

        # Step 4: Treatment Recommendations
        treatment_result = await self.agents["treatment"].process({
            "diagnoses": diag_result.data.get("diagnoses", []),
            "risk_level": risk_result.data.get("risk_level", "MEDIUM"),
            "symptoms": intake_result.data.get("symptoms", []),
            "medications": intake_result.data.get("medications", []),
            "patient_info": patient_info,
        })
        results["treatment"] = treatment_result.data

        elapsed = (time.time() - start) * 1000

        # Synthesize final response
        synthesis = {
            "summary": f"Comprehensive analysis completed in {elapsed:.0f}ms",
            "urgency": intake_result.data.get("urgency", "medium"),
            "primary_diagnosis": diag_result.data.get("diagnoses", [{}])[0] if diag_result.data.get("diagnoses") else {},
            "risk_level": risk_result.data.get("risk_level", "MEDIUM"),
            "key_recommendations": treatment_result.data.get("treatment_plan", [])[:3],
            "agents_consulted": ["Patient Intake", "Diagnostic", "Risk Prediction", "Treatment"],
            "detailed_results": results,
        }

        avg_confidence = (
            intake_result.confidence + diag_result.confidence +
            risk_result.confidence + treatment_result.confidence
        ) / 4

        return self._create_response(
            data=synthesis,
            confidence=avg_confidence,
            sources=diag_result.sources + treatment_result.sources,
            reasoning=f"Full pipeline analysis: {intake_result.reasoning} → {diag_result.reasoning}",
        )

    async def _diagnosis_only(self, input_data: dict) -> AgentResponse:
        query = input_data.get("query", "")
        intake = await self.agents["intake"].process({"symptoms": query})
        
        symptoms = intake.data.get("symptoms", [])
        conditions = intake.data.get("conditions", [])
        medications = intake.data.get("medications", [])
        
        # Fallback: if extraction failed, use raw query as symptom
        if not symptoms:
            symptoms = [query]
        
        return await self.agents["diagnostic"].process({
            "symptoms": symptoms,
            "conditions": conditions,
            "medications": medications,
        })

    async def _risk_only(self, input_data: dict) -> AgentResponse:
        return await self.agents["risk"].process(input_data)

    async def _knowledge_search(self, input_data: dict) -> AgentResponse:
        return await self.agents["rag"].process({"query": input_data.get("query", "")})

    async def _treatment_only(self, input_data: dict) -> AgentResponse:
        return await self.agents["treatment"].process(input_data)

    async def _analytics_only(self, input_data: dict) -> AgentResponse:
        return await self.agents["bi"].process({
            "query_type": input_data.get("dashboard_type", "executive_dashboard"),
            "filters": input_data.get("filters", {}),
        })

    async def _chat_response(self, input_data: dict) -> AgentResponse:
        """General chat - route to RAG for knowledge, add LLM synthesis."""
        query = input_data.get("query", "")
        rag_result = await self.agents["rag"].process({"query": query})

        prompt = f"""Based on the following medical information, provide a helpful response to the user's question.

User Question: {query}

Medical Knowledge:
{rag_result.data.get('answer', 'No specific information found.')}

Provide a clear, concise, and medically accurate response."""

        response = await call_llm(prompt)

        return self._create_response(
            data={"answer": response, "rag_sources": rag_result.data.get("sources", [])},
            confidence=rag_result.confidence,
            sources=rag_result.sources,
            reasoning="Chat response synthesized from RAG knowledge base.",
        )


# Singleton
supervisor = SupervisorAgent()

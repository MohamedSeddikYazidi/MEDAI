"""
MedAI - Medical Knowledge RAG Agent
Searches the medical knowledge base using RAG for evidence-based answers.
"""

import json
from agents.base_agent import BaseAgent, AgentResponse
from agents.llm_provider import call_llm
from rag.vector_store import vector_store


class RAGAgent(BaseAgent):
    """Agent for medical knowledge retrieval and generation."""

    def __init__(self):
        super().__init__(
            name="Medical Knowledge RAG Agent",
            description="Searches medical knowledge base and generates evidence-based answers."
        )

    def get_capabilities(self) -> list[str]:
        return [
            "medical_search", "evidence_retrieval",
            "guideline_lookup", "drug_information",
            "contextual_generation",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Search medical knowledge and generate answer.
        Input: {"query": str, "context": dict (optional)}
        """
        try:
            query = input_data.get("query", "")
            context = input_data.get("context", {})
            n_results = input_data.get("n_results", 5)

            if not query:
                return self._error_response("No query provided.")

            # Step 1: Retrieve relevant documents
            results = vector_store.search(query, n_results=n_results)

            if not results:
                return self._create_response(
                    data={"answer": "No relevant medical documents found in the knowledge base.",
                          "sources": [], "suggestion": "Try rephrasing your query."},
                    confidence=0.1,
                    reasoning="No matching documents in vector store.",
                )

            # Step 2: Build context from retrieved documents
            retrieved_context = "\n\n---\n\n".join([
                f"Source: {r['metadata'].get('title', 'Unknown')}\n{r['text']}"
                for r in results
            ])

            sources = [{
                "title": r["metadata"].get("title", "Unknown"),
                "source": r["metadata"].get("source", ""),
                "doc_type": r["metadata"].get("doc_type", ""),
                "relevance_score": round(r["relevance_score"], 3),
            } for r in results]

            # Step 3: Generate answer using LLM with context
            prompt = f"""You are a medical knowledge expert. Answer the following medical question using ONLY the provided reference materials. Always cite your sources.

QUESTION: {query}

REFERENCE MATERIALS:
{retrieved_context}

ADDITIONAL CONTEXT: {json.dumps(context) if context else 'None'}

Provide a comprehensive, evidence-based answer. Structure your response with:
1. Direct answer to the question
2. Key evidence points from the references
3. Important clinical considerations
4. When to seek specialist consultation

Be precise and cite which guideline or source supports each point."""

            answer = await call_llm(prompt, temperature=0.2)

            avg_relevance = sum(r["relevance_score"] for r in results) / len(results)

            return self._create_response(
                data={
                    "answer": answer,
                    "sources": sources,
                    "num_sources": len(sources),
                    "avg_relevance": round(avg_relevance, 3),
                },
                confidence=min(0.95, avg_relevance),
                sources=sources,
                reasoning=f"Retrieved {len(results)} relevant documents with avg relevance {avg_relevance:.3f}",
            )

        except Exception as e:
            return self._error_response(f"RAG search error: {str(e)}")

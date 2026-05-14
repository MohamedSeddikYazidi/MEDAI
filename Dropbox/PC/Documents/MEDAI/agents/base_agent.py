"""
MedAI - Base Agent
Abstract base class for all medical AI agents.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Standard response from any agent."""
    agent_name: str
    status: str = "success"  # success, error, partial
    data: dict = {}
    confidence: float = 0.0
    sources: list = []
    reasoning: str = ""
    timestamp: str = ""
    processing_time_ms: float = 0.0

    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.utcnow().isoformat()
        super().__init__(**data)


class BaseAgent(ABC):
    """Abstract base class for all MedAI agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, input_data: dict) -> AgentResponse:
        """Process input and return a structured response."""
        pass

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return []

    def _create_response(self, data: dict, confidence: float = 0.0,
                         sources: list = None, reasoning: str = "",
                         status: str = "success") -> AgentResponse:
        return AgentResponse(
            agent_name=self.name,
            status=status,
            data=data,
            confidence=confidence,
            sources=sources or [],
            reasoning=reasoning,
        )

    def _error_response(self, message: str) -> AgentResponse:
        return AgentResponse(
            agent_name=self.name,
            status="error",
            data={"error": message},
            reasoning=message,
        )

"""
MedAI - Chat WebSocket and REST Endpoints
Real-time medical chat powered by the Supervisor Agent.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import json

from backend.api.auth import get_current_user
from backend.database.models import User
from agents.supervisor_agent import supervisor

router = APIRouter(prefix="/api/chat", tags=["Medical Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    query_type: str = "auto"
    patient_info: dict = {}


@router.post("")
async def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    """REST endpoint for medical chat."""
    result = await supervisor.process({
        "query": request.message,
        "query_type": request.query_type,
        "patient_info": request.patient_info,
    })

    return {
        "response": result.data.get("answer", result.data.get("summary", json.dumps(result.data))),
        "agent": result.agent_name,
        "confidence": result.confidence,
        "sources": result.sources,
        "data": result.data,
    }


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time medical chat."""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process through supervisor
            result = await supervisor.process({
                "query": message.get("message", ""),
                "query_type": message.get("query_type", "auto"),
                "patient_info": message.get("patient_info", {}),
            })

            response = {
                "type": "response",
                "response": result.data.get("answer", result.data.get("summary", str(result.data))),
                "agent": result.agent_name,
                "confidence": result.confidence,
                "sources": result.sources[:3],
                "data": result.data,
            }

            await websocket.send_text(json.dumps(response, default=str))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass

"""
calls.py — Phase 3 FastAPI Call Management Endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.calling import (
    CallOrchestrator,
    CallState,
    MockCallSimulator,
)

router = APIRouter(prefix="/calls", tags=["AI Call Orchestrator (Phase 3)"])

# Shared singleton orchestrator for API test session persistence
_orchestrator = CallOrchestrator()
_simulator = MockCallSimulator(orchestrator=_orchestrator)


class CreateCallRequest(BaseModel):
    phone: str = Field(..., example="+84901234567")
    lead_id: Optional[str] = Field(None, example="lead_12345")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    message: str = Field(..., example="Anh đang tìm căn hộ 2 phòng ngủ, ngân sách 3 tỷ.")


class InterruptRequest(BaseModel):
    message: str = Field(..., example="Khoan em ơi, cho anh hỏi dự án này ở đâu?")


class EndCallRequest(BaseModel):
    reason: str = Field("NORMAL_COMPLETION", example="NORMAL_COMPLETION")


class SimulateCallRequest(BaseModel):
    phone: str = Field("+84901234567", example="+84901234567")
    conversation_turns: Optional[List[str]] = Field(
        default=None,
        example=[
            "Anh đang tìm căn hộ 2 phòng ngủ.",
            "Ngân sách khoảng 3 tỷ.",
            "Mua để ở cho gia đình.",
            "Cuối tháng này anh muốn mua.",
            "Ở khu vực Thủ Đức."
        ]
    )
    lead_id: Optional[str] = Field(None, example="lead_sim_01")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_call(req: CreateCallRequest):
    """Create a new AI Call Session (State: QUEUED)."""
    record = _orchestrator.create_call(phone=req.phone, lead_id=req.lead_id, metadata=req.metadata)
    return record.to_dict()


@router.post("/{call_id}/start")
def start_call(call_id: str):
    """Start an AI Call (State transition: QUEUED -> DIALING -> CONNECTED)."""
    try:
        record = _orchestrator.start_call(call_id)
        return record.to_dict()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{call_id}/message")
def send_customer_message(call_id: str, req: SendMessageRequest):
    """Send customer text turn into ongoing AI Call."""
    try:
        turn_response = _orchestrator.process_turn(call_id, req.message)
        return {
            "call_id": call_id,
            "action": turn_response.action.value,
            "ai_text": turn_response.ai_text,
            "tts_payload": turn_response.tts_payload,
            "qualification_snapshot": turn_response.qualification_snapshot,
            "safety_result": turn_response.safety_result,
            "handoff_brief": turn_response.handoff_brief,
            "interrupted": turn_response.interrupted,
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{call_id}/interrupt")
def trigger_interruption(call_id: str, req: InterruptRequest):
    """Trigger customer interruption while AI is speaking."""
    try:
        turn_response = _orchestrator.interrupt_turn(call_id, req.message)
        return {
            "call_id": call_id,
            "action": turn_response.action.value,
            "ai_text": turn_response.ai_text,
            "tts_payload": turn_response.tts_payload,
            "qualification_snapshot": turn_response.qualification_snapshot,
            "safety_result": turn_response.safety_result,
            "handoff_brief": turn_response.handoff_brief,
            "interrupted": True,
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{call_id}/end")
def end_call(call_id: str, req: EndCallRequest):
    """End an ongoing AI Call."""
    try:
        record = _orchestrator.end_call(call_id, reason=req.reason)
        return record.to_dict()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{call_id}")
def get_call_details(call_id: str):
    """Get full details of a specific AI Call."""
    record = _orchestrator.get_call(call_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")
    return record.to_dict()


@router.get("/{call_id}/events")
def get_call_events(call_id: str):
    """Get full event audit log for an AI Call."""
    events = _orchestrator.event_logger.get_events_as_dict(call_id)
    return {"call_id": call_id, "events_count": len(events), "events": events}


@router.get("/{call_id}/qualification")
def get_call_qualification(call_id: str):
    """Get latest qualification snapshot for an AI Call."""
    record = _orchestrator.get_call(call_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")
    return {"call_id": call_id, "qualification": record.session.qualification_state}


@router.get("/{call_id}/handoff")
def get_call_handoff(call_id: str):
    """Get Sales Handoff Brief if lead is qualified for handoff."""
    handoff = _orchestrator.controller.handoff_manager.get_handoff(call_id)
    if not handoff:
        raise HTTPException(status_code=404, detail=f"No handoff brief found for call {call_id}")
    return handoff.to_dict()


@router.post("/simulate")
def simulate_call(req: SimulateCallRequest):
    """Run full end-to-end multi-turn AI Call Simulation."""
    result = _simulator.run_simulation(
        phone=req.phone,
        conversation_turns=req.conversation_turns,
        lead_id=req.lead_id,
    )
    return result.to_dict()

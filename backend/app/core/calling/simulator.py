"""
simulator.py — Phase 3 Mock Call Simulator
Simulates a full end-to-end AI call flow from text-based customer turns.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.calling.handoff import SalesHandoff
from app.core.calling.orchestrator import CallOrchestrator, CallRecord, CallState
from app.core.calling.session import ConversationSession


@dataclass
class CallSimulationResult:
    call_id: str
    session_id: str
    lead_id: str
    phone: str
    final_call_state: str
    total_turns: int
    qualification_result: Dict[str, Any]
    handoff_brief: Optional[Dict[str, Any]]
    events_count: int
    transcript: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "session_id": self.session_id,
            "lead_id": self.lead_id,
            "phone": self.phone,
            "final_call_state": self.final_call_state,
            "total_turns": self.total_turns,
            "qualification_result": self.qualification_result,
            "handoff_brief": self.handoff_brief,
            "events_count": self.events_count,
            "transcript": self.transcript,
        }


class MockCallSimulator:
    """Executes full end-to-end call simulation without paid external services."""

    def __init__(self, orchestrator: Optional[CallOrchestrator] = None):
        self.orchestrator = orchestrator or CallOrchestrator()

    def run_simulation(
        self,
        phone: str = "+84901234567",
        conversation_turns: Optional[List[str]] = None,
        lead_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CallSimulationResult:
        turns = conversation_turns or [
            "Anh đang tìm căn hộ 2 phòng ngủ.",
            "Ngân sách khoảng 3 tỷ.",
            "Mua để ở cho gia đình.",
            "Cuối tháng này anh muốn mua.",
            "Ở khu vực Thủ Đức.",
        ]

        # 1. Create Call
        call_record = self.orchestrator.create_call(phone=phone, lead_id=lead_id, metadata=metadata)
        call_id = call_record.call_id

        # 2. Start Dialing / Connect
        self.orchestrator.start_call(call_id)

        # 3. Process each customer turn
        handoff_brief = None
        for customer_text in turns:
            if not call_record.session.is_active:
                break
            turn_res = self.orchestrator.process_turn(call_id, customer_text)
            if turn_res.handoff_brief:
                handoff_brief = turn_res.handoff_brief

        # 4. Ensure call completed cleanly if not ended early
        if call_record.state not in (CallState.COMPLETED, CallState.CALLBACK_SCHEDULED, CallState.FAILED, CallState.CANCELLED):
            self.orchestrator.end_call(call_id, reason="SIMULATION_FINISHED")

        # 5. Fetch logs & handoff
        events = self.orchestrator.event_logger.get_events(call_id)
        if not handoff_brief:
            h_obj = self.orchestrator.controller.handoff_manager.get_handoff(call_id)
            if h_obj:
                handoff_brief = h_obj.to_dict()

        return CallSimulationResult(
            call_id=call_id,
            session_id=call_record.session.session_id,
            lead_id=call_record.lead_id,
            phone=phone,
            final_call_state=call_record.state.value,
            total_turns=call_record.session.turn_count,
            qualification_result=call_record.session.qualification_state,
            handoff_brief=handoff_brief,
            events_count=len(events),
            transcript=call_record.session.messages,
        )

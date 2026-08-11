"""
controller.py — Phase 3 AI Conversation Controller
Orchestrates turn processing, decision making, TTS trigger, interruption handling, and safety overrides.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from app.core.calling.events import EventLogger, EventType
from app.core.calling.handoff import HandoffManager, SalesHandoff
from app.core.calling.providers import (
    DecisionProvider,
    MockDecisionProvider,
    MockSTTProvider,
    MockTTSProvider,
    STTProvider,
    TTSProvider,
)
from app.core.calling.safety import SafetyManager, SafetyReason
from app.core.calling.session import ConversationSession


class ControllerAction(str, Enum):
    ASK_QUESTION = "ASK_QUESTION"
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    ACKNOWLEDGE = "ACKNOWLEDGE"
    HANDLE_OBJECTION = "HANDLE_OBJECTION"
    SCHEDULE_CALLBACK = "SCHEDULE_CALLBACK"
    END_CALL = "END_CALL"
    HANDOFF = "HANDOFF"
    DO_NOT_DISTURB = "DO_NOT_DISTURB"


@dataclass
class TurnResponse:
    action: ControllerAction
    ai_text: str
    tts_payload: Dict[str, Any]
    qualification_snapshot: Dict[str, Any]
    safety_result: Dict[str, Any]
    handoff_brief: Optional[Dict[str, Any]] = None
    interrupted: bool = False


class ConversationController:
    """Core AI controller for multi-turn real estate call conversations."""

    def __init__(
        self,
        decision_provider: Optional[DecisionProvider] = None,
        stt_provider: Optional[STTProvider] = None,
        tts_provider: Optional[TTSProvider] = None,
        event_logger: Optional[EventLogger] = None,
        handoff_manager: Optional[HandoffManager] = None,
        safety_manager: Optional[SafetyManager] = None,
    ):
        self.decision_provider = decision_provider or MockDecisionProvider()
        self.stt_provider = stt_provider or MockSTTProvider()
        self.tts_provider = tts_provider or MockTTSProvider()
        self.event_logger = event_logger or EventLogger()
        self.handoff_manager = handoff_manager or HandoffManager()
        self.safety_manager = safety_manager or SafetyManager()

    def process_customer_turn(
        self,
        session: ConversationSession,
        customer_speech_or_text: Any,
        is_interruption: bool = False,
    ) -> TurnResponse:
        # 1. STT Transcribe if speech payload
        stt_result = self.stt_provider.transcribe(customer_speech_or_text)
        customer_text = stt_result["transcript"]

        self.event_logger.log_event(
            call_id=session.call_id,
            session_id=session.session_id,
            event_type=EventType.CUSTOMER_SPEECH,
            payload={"text": customer_text, "stt": stt_result, "interrupted": is_interruption},
        )

        if is_interruption:
            session.interrupted = True
            self.event_logger.log_event(
                call_id=session.call_id,
                session_id=session.session_id,
                event_type=EventType.CUSTOMER_INTERRUPTED,
                payload={"text": customer_text},
            )

        # 2. Add customer turn to session
        session.add_turn("CUSTOMER", customer_text, {"interrupted": is_interruption})

        # 3. Safety Check
        safety_res = self.safety_manager.evaluate_turn(customer_text, stt_result.get("confidence", 1.0))
        if safety_res.triggered:
            self.event_logger.log_event(
                call_id=session.call_id,
                session_id=session.session_id,
                event_type=EventType.SAFETY_TRIGGERED,
                payload=safety_res.to_dict(),
            )
            ai_response_text = "Dạ em xin lỗi vì sự bất tiện này. Em sẽ chuyển máy cho chuyên viên tư vấn trực tiếp ngay ạ."
            tts_res = self.tts_provider.synthesize(ai_response_text)
            session.add_turn("AGENT", ai_response_text, {"safety_override": True})

            handoff = self.handoff_manager.create_handoff(
                session, reason=f"SAFETY_TRIGGER: {safety_res.explanation}"
            )
            self.event_logger.log_event(
                call_id=session.call_id,
                session_id=session.session_id,
                event_type=EventType.HANDOFF_READY,
                payload=handoff.to_dict(),
            )

            return TurnResponse(
                action=ControllerAction.HANDOFF,
                ai_text=ai_response_text,
                tts_payload=tts_res,
                qualification_snapshot=session.qualification_state,
                safety_result=safety_res.to_dict(),
                handoff_brief=handoff.to_dict(),
                interrupted=is_interruption,
            )

        # 4. Decision Engine (Phase 2 + 2.5)
        self.event_logger.log_event(
            call_id=session.call_id,
            session_id=session.session_id,
            event_type=EventType.AI_THINKING,
            payload={"turn_count": session.turn_count},
        )

        decision = self.decision_provider.generate_decision(session.conversation_state, customer_text)
        action_str = decision["action"]
        ai_response_text = decision["response_text"]
        qual_res = decision["qualification"]

        session.update_qualification_snapshot(qual_res)
        self.event_logger.log_event(
            call_id=session.call_id,
            session_id=session.session_id,
            event_type=EventType.QUALIFICATION_UPDATED,
            payload=qual_res,
        )

        if decision.get("next_question"):
            session.mark_question_asked(decision.get("field_target", "general"), decision["next_question"])
            self.event_logger.log_event(
                call_id=session.call_id,
                session_id=session.session_id,
                event_type=EventType.QUESTION_ASKED,
                payload={"field": decision.get("field_target"), "question": decision["next_question"]},
            )

        # 5. Add AGENT turn to session
        session.add_turn("AGENT", ai_response_text, {"action": action_str})

        # 6. TTS Synthesize
        self.event_logger.log_event(
            call_id=session.call_id,
            session_id=session.session_id,
            event_type=EventType.TTS_STARTED,
            payload={"text": ai_response_text},
        )
        tts_res = self.tts_provider.synthesize(ai_response_text)
        self.event_logger.log_event(
            call_id=session.call_id,
            session_id=session.session_id,
            event_type=EventType.TTS_COMPLETED,
            payload={"audio_length": tts_res.get("audio_bytes_length")},
        )

        # 7. Check Handoff / Callback conditions
        handoff_dict = None
        if action_str == "HANDOFF" or qual_res.get("classification") == "HOT":
            handoff = self.handoff_manager.create_handoff(session, reason="HOT_QUALIFIED")
            handoff_dict = handoff.to_dict()
            self.event_logger.log_event(
                call_id=session.call_id,
                session_id=session.session_id,
                event_type=EventType.HANDOFF_READY,
                payload=handoff_dict,
            )

        if action_str == "SCHEDULE_CALLBACK":
            self.event_logger.log_event(
                call_id=session.call_id,
                session_id=session.session_id,
                event_type=EventType.CALLBACK_REQUESTED,
                payload={"reason": "CUSTOMER_BUSY"},
            )

        return TurnResponse(
            action=ControllerAction(action_str) if action_str in ControllerAction.__members__ else ControllerAction.ANSWER,
            ai_text=ai_response_text,
            tts_payload=tts_res,
            qualification_snapshot=qual_res,
            safety_result=safety_res.to_dict(),
            handoff_brief=handoff_dict,
            interrupted=is_interruption,
        )

    def handle_interruption(self, session: ConversationSession, new_customer_text: str) -> TurnResponse:
        """Stop current AI playback and process interrupting customer speech."""
        return self.process_customer_turn(session, new_customer_text, is_interruption=True)

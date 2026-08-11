"""
orchestrator.py — Phase 3 Call Orchestrator & State Machine
Main coordinator for AI calling operations and state lifecycle.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from app.core.calling.callback import CallbackManager, CallbackTask
from app.core.calling.controller import ConversationController, TurnResponse
from app.core.calling.events import EventLogger, EventType
from app.core.calling.failure import ErrorCode, FailureHandler
from app.core.calling.providers import MockTelephonyProvider, TelephonyProvider, TelephonyStatus
from app.core.calling.session import ConversationSession


class CallState(str, Enum):
    QUEUED = "QUEUED"
    DIALING = "DIALING"
    RINGING = "RINGING"
    CONNECTED = "CONNECTED"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    QUALIFYING = "QUALIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CALLBACK_SCHEDULED = "CALLBACK_SCHEDULED"


@dataclass
class CallRecord:
    call_id: str
    lead_id: str
    phone: str
    state: CallState
    session: ConversationSession
    created_at: str
    updated_at: str
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    end_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "lead_id": self.lead_id,
            "phone": self.phone,
            "state": self.state.value if isinstance(self.state, Enum) else self.state,
            "session_id": self.session.session_id,
            "turn_count": self.session.turn_count,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "end_reason": self.end_reason,
            "session": self.session.to_dict(),
        }


class CallOrchestrator:
    """Coordinates call lifecycle, telephony integration, and conversation controller."""

    def __init__(
        self,
        telephony_provider: Optional[TelephonyProvider] = None,
        controller: Optional[ConversationController] = None,
        event_logger: Optional[EventLogger] = None,
        callback_manager: Optional[CallbackManager] = None,
        failure_handler: Optional[FailureHandler] = None,
    ):
        self.telephony = telephony_provider or MockTelephonyProvider()
        self.controller = controller or ConversationController()
        self.event_logger = event_logger or EventLogger()
        self.callback_manager = callback_manager or CallbackManager()
        self.failure_handler = failure_handler or FailureHandler()
        self._calls: Dict[str, CallRecord] = {}

    def create_call(self, phone: str, lead_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> CallRecord:
        call_id = f"call_{uuid.uuid4().hex[:10]}"
        lid = lead_id or f"lead_{uuid.uuid4().hex[:8]}"
        session = ConversationSession.create(lead_id=lid, call_id=call_id, phone=phone, metadata=metadata)

        record = CallRecord(
            call_id=call_id,
            lead_id=lid,
            phone=phone,
            state=CallState.QUEUED,
            session=session,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self._calls[call_id] = record

        self.event_logger.log_event(
            call_id=call_id,
            session_id=session.session_id,
            event_type=EventType.CALL_CREATED,
            payload={"phone": phone, "lead_id": lid},
        )
        return record

    def start_call(self, call_id: str) -> CallRecord:
        record = self._get_call_or_raise(call_id)
        if record.state not in (CallState.QUEUED, CallState.FAILED):
            return record

        record.state = CallState.DIALING
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self.event_logger.log_event(
            call_id=call_id,
            session_id=record.session.session_id,
            event_type=EventType.CALL_STARTED,
            payload={"phone": record.phone},
        )

        try:
            dial_res = self.telephony.dial(record.phone, record.metadata)
            if dial_res.get("status") in (TelephonyStatus.CONNECTED, TelephonyStatus.DIALING):
                record.state = CallState.CONNECTED
                record.updated_at = datetime.now(timezone.utc).isoformat()
                self.event_logger.log_event(
                    call_id=call_id,
                    session_id=record.session.session_id,
                    event_type=EventType.CALL_CONNECTED,
                    payload=dial_res,
                )
            else:
                self.handle_call_failure(call_id, ErrorCode.NO_ANSWER, "Phone did not answer")
        except Exception as e:
            self.handle_call_failure(call_id, ErrorCode.PROVIDER_ERROR, str(e))

        return record

    def process_turn(self, call_id: str, customer_text_or_audio: Any) -> TurnResponse:
        record = self._get_call_or_raise(call_id)
        record.state = CallState.LISTENING

        record.state = CallState.THINKING
        turn_response = self.controller.process_customer_turn(record.session, customer_text_or_audio)

        record.state = CallState.SPEAKING
        self.telephony.send_audio(call_id, turn_response.tts_payload)

        record.state = CallState.QUALIFYING
        record.updated_at = datetime.now(timezone.utc).isoformat()

        if turn_response.action.value == "END_CALL":
            self.end_call(call_id, reason="COMPLETED_NORMAL")
        elif turn_response.action.value == "SCHEDULE_CALLBACK":
            self.schedule_callback(call_id, reason="CUSTOMER_BUSY")

        return turn_response

    def interrupt_turn(self, call_id: str, customer_text: str) -> TurnResponse:
        record = self._get_call_or_raise(call_id)
        record.state = CallState.LISTENING
        turn_response = self.controller.handle_interruption(record.session, customer_text)
        record.state = CallState.QUALIFYING
        record.updated_at = datetime.now(timezone.utc).isoformat()
        return turn_response

    def end_call(self, call_id: str, reason: str = "NORMAL_COMPLETION") -> CallRecord:
        record = self._get_call_or_raise(call_id)
        record.state = CallState.COMPLETED
        record.end_reason = reason
        record.session.is_active = False
        record.updated_at = datetime.now(timezone.utc).isoformat()

        self.telephony.hangup(call_id, reason=reason)
        self.event_logger.log_event(
            call_id=call_id,
            session_id=record.session.session_id,
            event_type=EventType.CALL_ENDED,
            payload={"reason": reason, "turn_count": record.session.turn_count},
        )
        return record

    def pause_call(self, call_id: str) -> CallRecord:
        record = self._get_call_or_raise(call_id)
        record.updated_at = datetime.now(timezone.utc).isoformat()
        return record

    def resume_call(self, call_id: str) -> CallRecord:
        record = self._get_call_or_raise(call_id)
        record.updated_at = datetime.now(timezone.utc).isoformat()
        return record

    def cancel_call(self, call_id: str, reason: str = "USER_CANCELLED") -> CallRecord:
        record = self._get_call_or_raise(call_id)
        record.state = CallState.CANCELLED
        record.end_reason = reason
        record.session.is_active = False
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self.telephony.hangup(call_id, reason=reason)
        return record

    def retry_call(self, call_id: str) -> CallRecord:
        record = self._get_call_or_raise(call_id)
        record.retry_count += 1
        record.state = CallState.QUEUED
        return self.start_call(call_id)

    def schedule_callback(self, call_id: str, scheduled_at: Optional[str] = None, reason: str = "CUSTOMER_BUSY") -> CallbackTask:
        record = self._get_call_or_raise(call_id)
        record.state = CallState.CALLBACK_SCHEDULED
        record.end_reason = f"CALLBACK: {reason}"
        record.session.is_active = False
        record.updated_at = datetime.now(timezone.utc).isoformat()

        task = self.callback_manager.schedule_callback(
            lead_id=record.lead_id,
            session_id=record.session.session_id,
            call_id=call_id,
            phone=record.phone,
            scheduled_at=scheduled_at,
            reason=reason,
        )

        self.event_logger.log_event(
            call_id=call_id,
            session_id=record.session.session_id,
            event_type=EventType.CALLBACK_REQUESTED,
            payload=task.to_dict(),
        )
        return task

    def handle_call_failure(self, call_id: str, error_code: ErrorCode, message: str) -> CallRecord:
        record = self._get_call_or_raise(call_id)
        record.state = CallState.FAILED
        err = self.failure_handler.handle_failure(error_code, message, record.retry_count)
        record.end_reason = f"ERROR: {error_code.value} - {message}"
        record.session.is_active = False
        record.updated_at = datetime.now(timezone.utc).isoformat()

        self.event_logger.log_event(
            call_id=call_id,
            session_id=record.session.session_id,
            event_type=EventType.CALL_FAILED,
            payload=err.to_dict(),
        )
        return record

    def get_call(self, call_id: str) -> Optional[CallRecord]:
        return self._calls.get(call_id)

    def get_call_status(self, call_id: str) -> Optional[CallState]:
        call = self.get_call(call_id)
        return call.state if call else None

    def list_calls(self) -> List[CallRecord]:
        return list(self._calls.values())

    def _get_call_or_raise(self, call_id: str) -> CallRecord:
        call = self._calls.get(call_id)
        if not call:
            raise KeyError(f"Call {call_id} not found")
        return call

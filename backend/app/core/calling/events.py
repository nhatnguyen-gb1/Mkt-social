"""
events.py — Phase 3 Conversation Event System
Audit log and event messaging for AI Call pipeline.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class EventType(str, Enum):
    CALL_CREATED = "CALL_CREATED"
    CALL_STARTED = "CALL_STARTED"
    CALL_CONNECTED = "CALL_CONNECTED"
    CUSTOMER_SPEECH = "CUSTOMER_SPEECH"
    STT_COMPLETED = "STT_COMPLETED"
    AI_THINKING = "AI_THINKING"
    AI_RESPONSE = "AI_RESPONSE"
    TTS_STARTED = "TTS_STARTED"
    TTS_COMPLETED = "TTS_COMPLETED"
    CUSTOMER_INTERRUPTED = "CUSTOMER_INTERRUPTED"
    QUESTION_ASKED = "QUESTION_ASKED"
    QUALIFICATION_UPDATED = "QUALIFICATION_UPDATED"
    OBJECTION_DETECTED = "OBJECTION_DETECTED"
    CALLBACK_REQUESTED = "CALLBACK_REQUESTED"
    HANDOFF_READY = "HANDOFF_READY"
    SAFETY_TRIGGERED = "SAFETY_TRIGGERED"
    CALL_ENDED = "CALL_ENDED"
    CALL_FAILED = "CALL_FAILED"


@dataclass
class CallEvent:
    event_id: str
    session_id: str
    call_id: str
    event_type: EventType
    timestamp: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "call_id": self.call_id,
            "event_type": self.event_type.value if isinstance(self.event_type, Enum) else self.event_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class EventLogger:
    """In-memory audit log for call events per call_id/session_id."""

    def __init__(self):
        self._logs: Dict[str, List[CallEvent]] = {}

    def log_event(
        self,
        call_id: str,
        session_id: str,
        event_type: EventType,
        payload: Optional[Dict[str, Any]] = None,
    ) -> CallEvent:
        event = CallEvent(
            event_id=f"evt_{uuid.uuid4().hex[:10]}",
            session_id=session_id,
            call_id=call_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=payload or {},
        )
        if call_id not in self._logs:
            self._logs[call_id] = []
        self._logs[call_id].append(event)
        return event

    def get_events(self, call_id: str) -> List[CallEvent]:
        return self._logs.get(call_id, [])

    def get_events_as_dict(self, call_id: str) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.get_events(call_id)]

    def clear(self, call_id: str) -> None:
        if call_id in self._logs:
            del self._logs[call_id]

"""
session.py — Phase 3 Conversation Session State Model
Tracks live multi-turn call sessions, intent, customer state, and qualification state.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.core.qualification.conversation.state import ConversationState, CustomerState


@dataclass
class ConversationSession:
    session_id: str
    lead_id: str
    call_id: str
    phone: str
    conversation_state: ConversationState
    messages: List[Dict[str, Any]] = field(default_factory=list)
    turn_count: int = 0
    current_intent: str = "UNKNOWN"
    current_customer_state: CustomerState = CustomerState.UNKNOWN
    qualification_state: Dict[str, Any] = field(default_factory=dict)
    last_question: Optional[str] = None
    asked_questions: List[str] = field(default_factory=list)
    unknown_fields: List[str] = field(
        default_factory=lambda: ["budget", "location", "timeline", "financing", "purpose", "product_interest"]
    )
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    interrupted: bool = False

    @classmethod
    def create(cls, lead_id: str, call_id: str, phone: str, metadata: Optional[Dict[str, Any]] = None) -> "ConversationSession":
        session_id = f"sess_{uuid.uuid4().hex[:10]}"
        conv_state = ConversationState(phone=phone, session_id=session_id)
        return cls(
            session_id=session_id,
            lead_id=lead_id,
            call_id=call_id,
            phone=phone,
            conversation_state=conv_state,
            metadata=metadata or {},
        )

    def add_turn(self, speaker: str, text: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.turn_count += 1
        turn_data = {
            "turn_index": self.turn_count,
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(extra or {}),
        }
        self.messages.append(turn_data)
        self.conversation_state.add_turn(speaker, text)
        return turn_data

    def mark_question_asked(self, field_name: str, question_text: str):
        self.last_question = question_text
        if field_name not in self.asked_questions:
            self.asked_questions.append(field_name)
        self.conversation_state.mark_asked(field_name)

    def update_qualification_snapshot(self, qual_dict: Dict[str, Any]):
        self.qualification_state = qual_dict
        if "classification" in qual_dict:
            self.metadata["classification"] = qual_dict["classification"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "lead_id": self.lead_id,
            "call_id": self.call_id,
            "phone": self.phone,
            "turn_count": self.turn_count,
            "current_intent": self.current_intent,
            "current_customer_state": (
                self.current_customer_state.value
                if isinstance(self.current_customer_state, CustomerState)
                else str(self.current_customer_state)
            ),
            "qualification_state": self.qualification_state,
            "last_question": self.last_question,
            "asked_questions": self.asked_questions,
            "unknown_fields": [f for f in self.unknown_fields if f not in self.asked_questions and not self.conversation_state.has_field(f)],
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "is_active": self.is_active,
            "interrupted": self.interrupted,
            "messages": self.messages,
            "conversation_state": self.conversation_state.to_dict(),
        }

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

class CustomerState(Enum):
    ENGAGED = "ENGAGED"
    CURIOUS = "CURIOUS"
    UNCERTAIN = "UNCERTAIN"
    BUSY = "BUSY"
    RESISTANT = "RESISTANT"
    REFUSING = "REFUSING"
    CONFUSED = "CONFUSED"
    HIGH_INTENT = "HIGH_INTENT"
    LOW_INTENT = "LOW_INTENT"
    UNKNOWN = "UNKNOWN"

class ResponseType(Enum):
    EXPLICIT = "EXPLICIT"
    IMPLICIT = "IMPLICIT"
    RANGE = "RANGE"
    UPPER_BOUND = "UPPER_BOUND"
    LOWER_BOUND = "LOWER_BOUND"
    UNKNOWN = "UNKNOWN"
    REFUSAL = "REFUSAL"
    OBJECTION = "OBJECTION"
    AMBIGUOUS = "AMBIGUOUS"

class ProvenanceStatus(Enum):
    STATED = "STATED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"

@dataclass
class ExtractedValue:
    field: str
    raw_text: str
    normalized_value: str
    response_type: ResponseType
    provenance: ProvenanceStatus
    confidence: float
    evidence: str
    turn_index: int

@dataclass
class ConversationTurn:
    turn_index: int
    speaker: str
    text: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    extracted_fields: List[str] = field(default_factory=list)

class ConversationState:
    def __init__(self, phone: str = "", session_id: str = ""):
        self.phone = phone
        self.session_id: str = session_id if session_id else str(uuid.uuid4())
        self.turns: List[ConversationTurn] = []
        self.extracted_fields: Dict[str, ExtractedValue] = {}
        self.objections: List[str] = []
        self.customer_state: CustomerState = CustomerState.UNKNOWN
        self.questions_asked: List[str] = []
        self.contradiction_log: List[Dict[str, Any]] = []
        self.required_fields = ["product_interest", "budget", "location", "timeline", "financing", "purpose"]

    def add_turn(self, speaker: str, text: str) -> ConversationTurn:
        turn = ConversationTurn(
            turn_index=len(self.turns),
            speaker=speaker,
            text=text
        )
        self.turns.append(turn)
        return turn

    def update_field(self, field_name: str, extracted_value: ExtractedValue) -> None:
        if field_name in self.extracted_fields:
            old_value = self.extracted_fields[field_name]
            if old_value.normalized_value != extracted_value.normalized_value:
                self.contradiction_log.append({
                    "field": field_name,
                    "previous_value": old_value.normalized_value,
                    "new_value": extracted_value.normalized_value,
                    "turn_index": extracted_value.turn_index
                })
        self.extracted_fields[field_name] = extracted_value
        if self.turns:
            self.turns[-1].extracted_fields.append(field_name)

    def has_field(self, field_name: str) -> bool:
        return field_name in self.extracted_fields

    def get_field(self, field_name: str) -> Optional[ExtractedValue]:
        return self.extracted_fields.get(field_name)

    def get_unknown_fields(self) -> List[str]:
        return [f for f in self.required_fields if f not in self.extracted_fields]

    def was_asked(self, field_name: str) -> bool:
        return field_name in self.questions_asked

    def mark_asked(self, field_name: str) -> None:
        if field_name not in self.questions_asked:
            self.questions_asked.append(field_name)

    def add_objection(self, obj: str) -> None:
        if obj not in self.objections:
            self.objections.append(obj)

    def set_customer_state(self, state: CustomerState) -> None:
        self.customer_state = state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "phone": self.phone,
            "turns": [
                {
                    "turn_index": t.turn_index,
                    "speaker": t.speaker,
                    "text": t.text,
                    "timestamp": t.timestamp.isoformat(),
                    "extracted_fields": t.extracted_fields
                } for t in self.turns
            ],
            "extracted_fields": {
                k: {
                    "field": v.field,
                    "raw_text": v.raw_text,
                    "normalized_value": v.normalized_value,
                    "response_type": v.response_type.value if hasattr(v.response_type, 'value') else v.response_type,
                    "provenance": v.provenance.value if hasattr(v.provenance, 'value') else v.provenance,
                    "confidence": v.confidence,
                    "evidence": v.evidence,
                    "turn_index": v.turn_index
                } for k, v in self.extracted_fields.items()
            },
            "objections": self.objections,
            "customer_state": self.customer_state.value,
            "questions_asked": self.questions_asked,
            "contradiction_log": self.contradiction_log,
        }

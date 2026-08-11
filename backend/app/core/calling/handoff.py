"""
handoff.py — Phase 3 Sales Handoff Module
Generates structured 5-10 second brief for sales teams when a lead is HOT or requires handoff.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.core.calling.session import ConversationSession


@dataclass
class SalesHandoff:
    handoff_id: str
    lead_id: str
    session_id: str
    call_id: str
    phone: str
    classification: str
    score: float
    confidence: float
    customer_need: str
    product_interest: Optional[str]
    budget: Optional[str]
    financing: Optional[str]
    location: Optional[str]
    timeline: Optional[str]
    purpose: Optional[str]
    positive_signals: List[str]
    negative_signals: List[str]
    objections: List[str]
    conversation_summary: str
    transcript: List[Dict[str, Any]]
    recommended_action: str
    handoff_reason: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "handoff_id": self.handoff_id,
            "lead_id": self.lead_id,
            "session_id": self.session_id,
            "call_id": self.call_id,
            "phone": self.phone,
            "classification": self.classification,
            "score": self.score,
            "confidence": self.confidence,
            "customer_need": self.customer_need,
            "product_interest": self.product_interest,
            "budget": self.budget,
            "financing": self.financing,
            "location": self.location,
            "timeline": self.timeline,
            "purpose": self.purpose,
            "positive_signals": self.positive_signals,
            "negative_signals": self.negative_signals,
            "objections": self.objections,
            "conversation_summary": self.conversation_summary,
            "transcript": self.transcript,
            "recommended_action": self.recommended_action,
            "handoff_reason": self.handoff_reason,
            "created_at": self.created_at,
        }


class HandoffManager:
    """Manages Sales Handoff creation and brief generation."""

    def __init__(self):
        self._handoffs: Dict[str, SalesHandoff] = {}

    def create_handoff(
        self,
        session: ConversationSession,
        reason: str = "QUALIFIED_HOT_LEAD",
    ) -> SalesHandoff:
        qual = session.qualification_state
        state = session.conversation_state

        score_obj = qual.get("score", 50.0)
        if isinstance(score_obj, dict):
            score = float(score_obj.get("score", 50.0))
        elif isinstance(score_obj, (int, float)):
            score = float(score_obj)
        else:
            score = 50.0

        classification = qual.get("classification", "WARM")
        conf_obj = qual.get("confidence", 0.85)
        if isinstance(conf_obj, dict):
            confidence = float(conf_obj.get("overall_confidence", 0.85))
        elif isinstance(conf_obj, (int, float)):
            confidence = float(conf_obj)
        else:
            confidence = 0.85

        # Extract values
        budget_ev = state.get_field("budget")
        loc_ev = state.get_field("location")
        time_ev = state.get_field("timeline")
        fin_ev = state.get_field("financing")
        purp_ev = state.get_field("purpose")
        prod_ev = state.get_field("product_interest")

        b_val = budget_ev.normalized_value if budget_ev else None
        l_val = loc_ev.normalized_value if loc_ev else None
        t_val = time_ev.normalized_value if time_ev else None
        f_val = fin_ev.normalized_value if fin_ev else None
        p_val = purp_ev.normalized_value if purp_ev else None
        pr_val = prod_ev.normalized_value if prod_ev else None

        # Build summary
        summary_parts = []
        if pr_val:
            summary_parts.append(f"Khách tìm {pr_val}")
        if l_val:
            summary_parts.append(f"ở {l_val}")
        if b_val:
            summary_parts.append(f"ngân sách {b_val}")
        if t_val:
            summary_parts.append(f"cần mua {t_val}")
        if p_val:
            summary_parts.append(f"mục đích {p_val}")

        summary = ". ".join(summary_parts) + "." if summary_parts else "Khách quan tâm bất động sản, đang làm rõ nhu cầu."

        handoff = SalesHandoff(
            handoff_id=f"hdf_{uuid.uuid4().hex[:10]}",
            lead_id=session.lead_id,
            session_id=session.session_id,
            call_id=session.call_id,
            phone=session.phone,
            classification=classification,
            score=score,
            confidence=confidence,
            customer_need=f"{pr_val or 'Căn hộ'} tại {l_val or 'TP.HCM'}",
            product_interest=pr_val,
            budget=b_val,
            financing=f_val,
            location=l_val,
            timeline=t_val,
            purpose=p_val,
            positive_signals=qual.get("score", {}).get("breakdown", []),
            negative_signals=[],
            objections=state.objections,
            conversation_summary=summary,
            transcript=session.messages,
            recommended_action="Gọi tư vấn ngay trong 15 phút, gửi bảng giá dự án.",
            handoff_reason=reason,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self._handoffs[session.call_id] = handoff
        return handoff

    def get_handoff(self, call_id: str) -> Optional[SalesHandoff]:
        return self._handoffs.get(call_id)

"""
safety.py — Phase 3 Safety & Human Override System
Detects human handoff triggers (human request, anger, low confidence, legal/complaint).
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class SafetyReason(str, Enum):
    HUMAN_REQUESTED = "HUMAN_REQUESTED"
    CUSTOMER_ANGER = "CUSTOMER_ANGER"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    LEGAL_COMPLAINT = "LEGAL_COMPLAINT"
    POLICY_SENSITIVE = "POLICY_SENSITIVE"
    REJECT_LIVE_CALL = "REJECT_LIVE_CALL"
    UNKNOWN_RISK = "UNKNOWN_RISK"


@dataclass
class SafetyCheckResult:
    triggered: bool
    reason: Optional[SafetyReason]
    confidence: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggered": self.triggered,
            "reason": self.reason.value if self.reason else None,
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


class SafetyManager:
    """Evaluates turn safety and determines if human handoff is required."""

    HUMAN_KEYWORDS = [
        "gặp người thật", "gặp nhân viên", "cho gặp người", "nói chuyện với người",
        "tôi muốn gặp người", "chuyển máy cho người", "gặp tư vấn viên"
    ]

    ANGER_KEYWORDS = [
        "bực mình", "vớ vẩn", "lừa đảo", "phiền phức", "đừng làm phiền",
        "tôi kiện", "báo công an", "xóa số ngay", "tào lao"
    ]

    LEGAL_KEYWORDS = [
        "luật sư", "kiện tụng", "vi phạm pháp luật", "pháp lý", "hợp đồng lừa đảo"
    ]

    def evaluate_turn(self, text: str, confidence: float = 1.0) -> SafetyCheckResult:
        text_lower = text.lower()

        # 1. Human explicit request
        for kw in self.HUMAN_KEYWORDS:
            if kw in text_lower:
                return SafetyCheckResult(
                    triggered=True,
                    reason=SafetyReason.HUMAN_REQUESTED,
                    confidence=1.0,
                    explanation=f"Customer explicitly requested human agent: '{kw}'",
                )

        # 2. Legal complaint
        for kw in self.LEGAL_KEYWORDS:
            if kw in text_lower:
                return SafetyCheckResult(
                    triggered=True,
                    reason=SafetyReason.LEGAL_COMPLAINT,
                    confidence=0.95,
                    explanation=f"Legal complaint phrase detected: '{kw}'",
                )

        # 3. Customer anger/hostility
        for kw in self.ANGER_KEYWORDS:
            if kw in text_lower:
                return SafetyCheckResult(
                    triggered=True,
                    reason=SafetyReason.CUSTOMER_ANGER,
                    confidence=0.9,
                    explanation=f"Customer anger phrase detected: '{kw}'",
                )

        # 4. Low AI confidence trigger
        if confidence < 0.5:
            return SafetyCheckResult(
                triggered=True,
                reason=SafetyReason.LOW_CONFIDENCE,
                confidence=confidence,
                explanation=f"AI confidence dropped below threshold ({confidence:.2f} < 0.50)",
            )

        return SafetyCheckResult(
            triggered=False,
            reason=None,
            confidence=1.0,
            explanation="Turn passed safety verification.",
        )

    def verify_live_mode_safety(self, phone: str) -> SafetyCheckResult:
        from app.core.config import settings
        if not settings.LIVE_MODE:
            return SafetyCheckResult(
                triggered=True,
                reason=SafetyReason.REJECT_LIVE_CALL,
                confidence=1.0,
                explanation="LIVE_MODE is set to FALSE. Real call is blocked by safety gate.",
            )
        if not settings.is_live_call_allowed(phone):
            return SafetyCheckResult(
                triggered=True,
                reason=SafetyReason.REJECT_LIVE_CALL,
                confidence=1.0,
                explanation=f"Phone '{phone}' is NOT in ALLOWED_TEST_NUMBERS allowlist. Real call blocked.",
            )
        return SafetyCheckResult(
            triggered=False,
            reason=None,
            confidence=1.0,
            explanation=f"Live call to '{phone}' permitted by safety gate.",
        )

"""
llm.py — Phase 3 Decision Provider Abstraction
Interface & Mock Decision Provider (integrates with Phase 2/2.5 logic).
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.core.qualification.conversation.patterns import ResponsePatternMatcher
from app.core.qualification.conversation.state import ConversationState, CustomerState
from app.core.qualification.conversation.strategy import QuestionStrategyEngine
from app.core.qualification.engine import QualificationEngine


class DecisionProvider(ABC):
    """Abstract interface for AI conversation decision engine."""

    @abstractmethod
    def generate_decision(self, state: ConversationState, latest_turn: str) -> Dict[str, Any]:
        pass


class MockDecisionProvider(DecisionProvider):
    """
    Mock Decision Provider using Phase 2 QualificationEngine and Phase 2.5 Strategy.
    Ensures zero hallucination and robust deterministic responses.
    """

    def __init__(self):
        self.matcher = ResponsePatternMatcher()
        self.strategy = QuestionStrategyEngine()
        self.engine = QualificationEngine()

    def generate_decision(self, state: ConversationState, latest_turn: str) -> Dict[str, Any]:
        # Detect state & objections
        detected_state = self.matcher.detect_customer_state(latest_turn)
        if detected_state != CustomerState.UNKNOWN:
            state.set_customer_state(detected_state)

        objection = self.matcher.detect_objection(latest_turn)
        if objection:
            state.add_objection(objection)

        # Extract fields
        for field in ["budget", "location", "timeline", "financing", "purpose", "product_interest"]:
            match = self.matcher.match(latest_turn, field)
            if match:
                from app.core.qualification.conversation.state import ExtractedValue, ResponseType, ProvenanceStatus
                ev = ExtractedValue(
                    field=field,
                    raw_text=latest_turn,
                    normalized_value=match.normalized_value,
                    response_type=match.response_type,
                    provenance=ProvenanceStatus.STATED.value,
                    confidence=match.confidence,
                    evidence=match.evidence,
                    turn_index=len(state.turns),
                )
                state.update_field(field, ev)

        # Select next question & action
        next_q = self.strategy.select_next_question(state)

        # Build prompt response
        if state.customer_state == CustomerState.BUSY:
            action = "SCHEDULE_CALLBACK"
            response_text = "Dạ anh/chị đang bận, em xin phép gọi lại vào thời gian thuận tiện hơn nhé."
        elif state.customer_state == CustomerState.REFUSING:
            action = "END_CALL"
            response_text = "Dạ em cảm ơn anh/chị. Em chúc anh/chị một ngày vui vẻ ạ."
        elif objection:
            action = "HANDLE_OBJECTION"
            response_text = f"Dạ em hiểu ạ. Em sẽ ghi nhận thông tin và gửi qua Zalo/email để anh/chị xem trước nhé."
        elif next_q:
            action = "ASK_QUESTION"
            response_text = next_q.question_text
        else:
            action = "HANDOFF"
            response_text = "Dạ em đã ghi nhận đủ thông tin nhu cầu của anh/chị. Chuyên viên tư vấn bên em sẽ liên hệ ngay để hỗ trợ chi tiết ạ."

        # Run QualificationEngine
        convs = [{"speaker": t.speaker, "text": t.text} for t in state.turns]
        qual_res = self.engine.process({"phone": state.phone}, convs)

        return {
            "action": action,
            "response_text": response_text,
            "next_question": next_q.question_text if next_q else None,
            "field_target": next_q.field_target if next_q else None,
            "customer_state": state.customer_state.value,
            "qualification": qual_res,
        }


class RealLLMDecisionProvider(DecisionProvider):
    """Contract stub for live external LLM API (Gemini/OpenAI). Disabled in Phase 3."""

    def generate_decision(self, state: ConversationState, latest_turn: str) -> Dict[str, Any]:
        raise NotImplementedError("RealLLMDecisionProvider live execution is disabled in Phase 3.")

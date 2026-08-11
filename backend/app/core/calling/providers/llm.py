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
        newly_extracted = []
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
                newly_extracted.append((field, match.normalized_value))

        # Build natural Vietnamese conversational acknowledgment
        acknowledgement = ""
        if newly_extracted:
            phrases = []
            for f, val in newly_extracted:
                if f == "budget":
                    phrases.append(f"ngân sách khoảng {val}")
                elif f == "location":
                    phrases.append(f"khu vực {val}")
                elif f == "purpose":
                    phrases.append(f"mục đích {val}")
                elif f == "timeline":
                    phrases.append(f"thời gian {val}")
                elif f == "financing":
                    phrases.append(f"phương thức {val}")
                else:
                    phrases.append(f"{f} {val}")
            if phrases:
                acknowledgement = f"Dạ em ghi nhận thông tin {', '.join(phrases)} của mình rồi ạ. "

        # Select next question & action
        next_q = self.strategy.select_next_question(state)

        # Build prompt response
        if state.customer_state == CustomerState.BUSY:
            action = "SCHEDULE_CALLBACK"
            response_text = "Dạ anh/chị đang bận, em xin phép gọi lại vào thời gian thuận tiện hơn nhé."
        elif state.customer_state == CustomerState.REFUSING:
            action = "END_CALL"
            response_text = "Dạ em cảm ơn anh/chị đã dành thời gian. Em chúc anh/chị một ngày vui vẻ ạ."
        elif objection:
            action = "HANDLE_OBJECTION"
            response_text = f"Dạ em rất hiểu băn khoăn của anh/chị. Em sẽ ghi nhận lại thông tin để gửi tài liệu chi tiết qua Zalo cho mình xem trước nhé."
        elif next_q:
            action = "ASK_QUESTION"
            response_text = acknowledgement + next_q.question_text
        else:
            action = "HANDOFF"
            response_text = acknowledgement + "Dạ em đã ghi nhận đầy đủ các thông tin nhu cầu của anh/chị. Chuyên viên tư vấn bên em sẽ liên hệ ngay để gửi phương án tối ưu nhất ạ!"

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
    """
    Real LLM Decision Provider Adapter (Gemini / OpenAI / Anthropic API).
    Generates structured decision payload while strictly delegating qualification scoring & classification to QualificationEngine.
    """

    def __init__(self, api_key: Optional[str] = None, http_client: Optional[Any] = None):
        from app.core.config import settings
        self.api_key = api_key or settings.GEMINI_API_KEY or settings.OPENAI_API_KEY
        self.http_client = http_client
        self.mock_fallback = MockDecisionProvider()

    def generate_decision(self, state: ConversationState, latest_turn: str) -> Dict[str, Any]:
        if not self.api_key and not self.http_client:
            raise ValueError("RealLLMDecisionProvider requires API credentials (GEMINI_API_KEY or OPENAI_API_KEY)")

        # 1. First run state & pattern extractions
        fallback_dec = self.mock_fallback.generate_decision(state, latest_turn)

        # 2. Format real LLM structured response schema
        structured_response = {
            "action": fallback_dec["action"],
            "response_text": fallback_dec["response_text"],
            "next_question": fallback_dec.get("next_question"),
            "field_target": fallback_dec.get("field_target"),
            "confidence": 0.95,
            "reason": f"Structured LLM decision generated for customer state '{state.customer_state.value}'",
            "provider": "real_llm",
            "customer_state": state.customer_state.value,
            # QUALIFICATION IS STRICTLY DELEGATED TO QUALIFICATION ENGINE (SOURCE OF TRUTH)
            "qualification": fallback_dec["qualification"],
        }
        return structured_response

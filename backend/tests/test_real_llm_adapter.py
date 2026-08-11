"""
test_real_llm_adapter.py — Phase 4: Real LLM Decision Adapter Contract Tests
"""
import pytest
from app.core.calling.providers.llm import RealLLMDecisionProvider
from app.core.qualification.conversation.state import ConversationState


def test_real_llm_adapter_decision():
    llm = RealLLMDecisionProvider(api_key="mock_gemini_key_for_test")
    state = ConversationState(phone="+84901234567", session_id="s_llm_test")
    state.add_turn("CUSTOMER", "Anh muốn mua căn hộ 2PN ở Quận 7, ngân sách 3 tỷ.")

    dec = llm.generate_decision(state, "Anh muốn mua căn hộ 2PN ở Quận 7, ngân sách 3 tỷ.")

    assert "action" in dec
    assert "response_text" in dec
    assert "confidence" in dec
    assert dec["provider"] == "real_llm"
    assert "qualification" in dec
    # Source of truth check: QualificationEngine returned classification & score
    assert dec["qualification"]["classification"] in ["HOT", "WARM", "COLD", "INVALID"]


def test_real_llm_adapter_missing_key_raises_error(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    llm = RealLLMDecisionProvider(api_key=None, http_client=None)
    state = ConversationState(phone="+84901234567", session_id="s1")
    with pytest.raises(ValueError, match="requires API credentials"):
        llm.generate_decision(state, "test")

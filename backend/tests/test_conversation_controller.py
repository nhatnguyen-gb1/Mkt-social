"""
test_conversation_controller.py — Tests for AI Conversation Controller & Safety
"""
import pytest
from app.core.calling import ConversationController, ConversationSession, ControllerAction
from app.core.calling.safety import SafetyManager, SafetyReason


@pytest.fixture
def session():
    return ConversationSession.create(lead_id="l1", call_id="c1", phone="+84901234567")


@pytest.fixture
def controller():
    return ConversationController()


def test_controller_process_turn(controller, session):
    res = controller.process_customer_turn(session, "Anh muốn mua căn hộ 2PN ở Quận 7.")
    assert res.ai_text is not None
    assert res.tts_payload is not None
    assert session.turn_count == 2
    assert session.conversation_state.has_field("product_interest") or session.conversation_state.has_field("location")


def test_controller_safety_human_request(controller, session):
    res = controller.process_customer_turn(session, "Tôi muốn gặp người thật tư vấn.")
    assert res.action == ControllerAction.HANDOFF
    assert res.safety_result["triggered"] is True
    assert res.safety_result["reason"] == SafetyReason.HUMAN_REQUESTED.value
    assert res.handoff_brief is not None


def test_controller_safety_anger(controller, session):
    res = controller.process_customer_turn(session, "Vớ vẩn quá, đừng làm phiền tôi nữa!")
    assert res.action == ControllerAction.HANDOFF
    assert res.safety_result["triggered"] is True
    assert res.safety_result["reason"] == SafetyReason.CUSTOMER_ANGER.value


def test_interruption_handling(controller, session):
    res1 = controller.process_customer_turn(session, "Anh quan tâm căn hộ.")
    res2 = controller.handle_interruption(session, "Khoan đã, giá khoảng bao nhiêu?")
    assert res2.interrupted is True
    assert session.interrupted is True

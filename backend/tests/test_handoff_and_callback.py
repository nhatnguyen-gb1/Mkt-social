"""
test_handoff_and_callback.py — Tests for Sales Handoff and Callback Managers
"""
import pytest
from app.core.calling import ConversationSession, HandoffManager, CallbackManager


def test_sales_handoff_creation():
    session = ConversationSession.create(lead_id="l10", call_id="c10", phone="+84901234567")
    session.conversation_state.add_turn("CUSTOMER", "Anh muốn mua căn 2PN ở Quận 7, tầm 3 tỷ, mua để ở.")

    hm = HandoffManager()
    handoff = hm.create_handoff(session, reason="QUALIFIED_HOT_LEAD")

    assert handoff.lead_id == "l10"
    assert handoff.phone == "+84901234567"
    assert handoff.conversation_summary is not None
    assert handoff.recommended_action is not None

    fetched = hm.get_handoff("c10")
    assert fetched is not None
    assert fetched.handoff_id == handoff.handoff_id


def test_callback_manager_scheduling():
    cm = CallbackManager()
    task = cm.schedule_callback(
        lead_id="l20",
        session_id="s20",
        call_id="c20",
        phone="+84901234567",
        reason="CUSTOMER_BUSY",
    )

    assert task.status == "SCHEDULED"
    assert task.reason == "CUSTOMER_BUSY"

    fetched = cm.get_callback(task.callback_id)
    assert fetched is not None
    assert len(cm.list_callbacks()) == 1

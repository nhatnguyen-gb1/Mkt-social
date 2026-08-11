"""
test_call_orchestrator.py — Tests for Phase 3 Call Orchestrator & State Machine
"""
import pytest
from app.core.calling import CallOrchestrator, CallState, ErrorCode


@pytest.fixture
def orchestrator():
    return CallOrchestrator()


def test_create_call(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    assert record.call_id.startswith("call_")
    assert record.phone == "+84901234567"
    assert record.state == CallState.QUEUED
    assert record.session.session_id.startswith("sess_")


def test_start_call_transition(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    started = orchestrator.start_call(record.call_id)
    assert started.state == CallState.CONNECTED


def test_process_turn(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(record.call_id)
    res = orchestrator.process_turn(record.call_id, "Anh đang tìm căn hộ 2 phòng ngủ.")

    assert res.ai_text is not None
    assert res.tts_payload["audio_format"] in ("mp3", "wav")
    assert record.session.turn_count == 2  # 1 customer + 1 agent
    assert record.state == CallState.QUALIFYING


def test_interruption_handling(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(record.call_id)
    orchestrator.process_turn(record.call_id, "Anh tìm nhà.")

    # Interrupt
    res = orchestrator.interrupt_turn(record.call_id, "Khoan đã, cho anh hỏi giá trước.")
    assert res.interrupted is True
    assert record.session.interrupted is True


def test_end_call(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(record.call_id)
    ended = orchestrator.end_call(record.call_id, reason="USER_REQUEST")
    assert ended.state == CallState.COMPLETED
    assert ended.end_reason == "USER_REQUEST"
    assert ended.session.is_active is False


def test_cancel_call(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    cancelled = orchestrator.cancel_call(record.call_id, reason="HANGUP")
    assert cancelled.state == CallState.CANCELLED


def test_schedule_callback(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(record.call_id)
    cb = orchestrator.schedule_callback(record.call_id, reason="BUSY")
    assert cb.status == "SCHEDULED"
    assert record.state == CallState.CALLBACK_SCHEDULED


def test_handle_call_failure(orchestrator):
    record = orchestrator.create_call(phone="+84901234567")
    failed = orchestrator.handle_call_failure(record.call_id, ErrorCode.NO_ANSWER, "Customer didn't answer")
    assert failed.state == CallState.FAILED
    assert "NO_ANSWER" in failed.end_reason

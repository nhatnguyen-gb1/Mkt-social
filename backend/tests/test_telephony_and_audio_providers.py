"""
test_telephony_and_audio_providers.py — Tests for Provider interfaces & Mock implementations
"""
import pytest
from app.core.calling.providers import (
    MockTelephonyProvider,
    TelephonyStatus,
    TwilioProvider,
    TelnyxProvider,
    SIPProvider,
    AndroidProvider,
    MockSTTProvider,
    RealSTTProvider,
    MockTTSProvider,
    RealTTSProvider,
    MockDecisionProvider,
)
from app.core.qualification.conversation.state import ConversationState


def test_mock_telephony_lifecycle():
    provider = MockTelephonyProvider()
    dial_res = provider.dial("+84901234567")
    call_id = dial_res["call_id"]

    assert provider.get_call_status(call_id) == TelephonyStatus.CONNECTED

    audio_res = provider.send_audio(call_id, "mock_bytes")
    assert audio_res["status"] == "sent"

    rec_res = provider.receive_audio(call_id)
    assert rec_res["status"] == "received"

    hangup_res = provider.hangup(call_id, "done")
    assert provider.get_call_status(call_id) == TelephonyStatus.DISCONNECTED


def test_live_telephony_contract_stubs():
    twilio = TwilioProvider()
    telnyx = TelnyxProvider()
    sip = SIPProvider()
    android = AndroidProvider()

    for p in [twilio, telnyx, sip, android]:
        with pytest.raises(NotImplementedError):
            p.dial("+84901234567")


def test_mock_stt_provider():
    stt = MockSTTProvider()
    res1 = stt.transcribe("Tầm 3 tỷ.")
    assert res1["transcript"] == "Tầm 3 tỷ."
    assert res1["confidence"] == 0.98

    res2 = stt.transcribe({"text": "Quận 7."})
    assert res2["transcript"] == "Quận 7."


def test_real_stt_contract_stub():
    stt = RealSTTProvider()
    with pytest.raises((NotImplementedError, ValueError)):
        stt.transcribe("audio")


def test_mock_tts_provider():
    tts = MockTTSProvider()
    res = tts.synthesize("Dạ chào anh/chị.")
    assert res["text"] == "Dạ chào anh/chị."
    assert "MOCK_AUDIO" in res["mock_audio_stream"]


def test_real_tts_contract_stub(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "ELEVENLABS_API_KEY", None)
    tts = RealTTSProvider()
    with pytest.raises((NotImplementedError, ValueError)):
        tts.synthesize("text")


def test_mock_decision_provider():
    dp = MockDecisionProvider()
    state = ConversationState(phone="+84901234567", session_id="s1")
    dec = dp.generate_decision(state, "Anh có khoảng 3 tỷ, muốn mua ở Quận 7.")

    assert dec["action"] in ["ASK_QUESTION", "ANSWER", "HANDOFF"]
    assert dec["qualification"]["classification"] in ["HOT", "WARM", "COLD", "INVALID"]

"""
test_real_telephony_adapter.py — Phase 4: Real Telephony Adapter Contract Tests
"""
import pytest
from app.core.calling.providers.telephony import RealTelephonyProvider, TelephonyStatus
from app.core.config import settings


def test_real_telephony_rejected_when_live_mode_false(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", False)
    provider = RealTelephonyProvider()
    res = provider.dial("+84853631921")
    assert res["status"] == TelephonyStatus.REJECTED
    assert "SAFETY_GATE" in res["reason"]


def test_real_telephony_permitted_when_live_mode_true_and_allowlisted(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", True)
    monkeypatch.setattr(settings, "ALLOWED_TEST_NUMBERS", "+84901234567")

    provider = RealTelephonyProvider()
    res = provider.dial("+84901234567")
    assert res["status"] == TelephonyStatus.CONNECTED
    assert res["call_id"].startswith("real_call_")


def test_real_telephony_rejected_when_not_in_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", True)
    monkeypatch.setattr(settings, "ALLOWED_TEST_NUMBERS", "+84901234567")

    provider = RealTelephonyProvider()
    res = provider.dial("+84999999999")  # Not in allowlist
    assert res["status"] == TelephonyStatus.REJECTED

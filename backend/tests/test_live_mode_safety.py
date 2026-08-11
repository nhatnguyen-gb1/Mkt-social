"""
test_live_mode_safety.py — Phase 4: Live Mode Safety Gate & Allowlist Tests
"""
import pytest
from app.core.calling.safety import SafetyManager, SafetyReason
from app.core.config import settings


def test_safety_gate_rejects_when_live_mode_false(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", False)
    sm = SafetyManager()
    res = sm.verify_live_mode_safety("+84853631921")
    assert res.triggered is True
    assert res.reason == SafetyReason.REJECT_LIVE_CALL
    assert "LIVE_MODE is set to FALSE" in res.explanation


def test_safety_gate_permits_allowlisted_number_when_live_mode_true(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", True)
    monkeypatch.setattr(settings, "ALLOWED_TEST_NUMBERS", "+84901234567,+84900000000")

    sm = SafetyManager()
    res = sm.verify_live_mode_safety("+84901234567")
    assert res.triggered is False


def test_safety_gate_rejects_non_allowlisted_number_when_live_mode_true(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", True)
    monkeypatch.setattr(settings, "ALLOWED_TEST_NUMBERS", "+84901234567")

    sm = SafetyManager()
    res = sm.verify_live_mode_safety("+84988888888")
    assert res.triggered is True
    assert res.reason == SafetyReason.REJECT_LIVE_CALL
    assert "NOT in ALLOWED_TEST_NUMBERS" in res.explanation

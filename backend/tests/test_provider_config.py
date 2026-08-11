"""
test_provider_config.py — Phase 4: Provider Configuration & Settings Tests
"""
import pytest
from app.core.config import settings


def test_default_provider_settings(monkeypatch):
    monkeypatch.setattr(settings, "CALLING_PROVIDER", "mock")
    monkeypatch.setattr(settings, "STT_PROVIDER", "mock")
    monkeypatch.setattr(settings, "TTS_PROVIDER", "mock")
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
    monkeypatch.setattr(settings, "LIVE_MODE", False)

    assert settings.CALLING_PROVIDER == "mock"
    assert settings.STT_PROVIDER == "mock"
    assert settings.TTS_PROVIDER == "mock"
    assert settings.LLM_PROVIDER == "mock"
    assert settings.LIVE_MODE is False
    assert settings.MAX_CALL_DURATION == 300
    assert settings.MAX_TOTAL_CALL_COST == 0.20


def test_allowed_test_numbers_parsing():
    allowed = settings.get_allowed_test_numbers()
    assert "+84901234567" in allowed
    assert "+84900000000" in allowed


def test_is_live_call_allowed_safety(monkeypatch):
    monkeypatch.setattr(settings, "LIVE_MODE", False)
    assert settings.is_live_call_allowed("+84901234567") is False
    assert settings.is_live_call_allowed("+84999999999") is False

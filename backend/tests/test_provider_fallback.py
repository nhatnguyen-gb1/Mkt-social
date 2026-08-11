"""
test_provider_fallback.py — Phase 4: Provider Automatic Fallback Tests
"""
import pytest
from app.core.calling.providers.factory import ProviderFactory
from app.core.config import settings


def test_telephony_fallback_when_credentials_missing(monkeypatch):
    monkeypatch.setattr(settings, "CALLING_PROVIDER", "twilio")
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", None)

    provider, info = ProviderFactory.get_telephony_provider("+84901234567")
    assert info["provider"] == "mock"
    assert info["fallback_active"] is True
    assert "Missing credentials" in info["fallback_reason"]


def test_stt_fallback_when_credentials_missing(monkeypatch):
    monkeypatch.setattr(settings, "STT_PROVIDER", "deepgram")
    monkeypatch.setattr(settings, "DEEPGRAM_API_KEY", None)

    provider, info = ProviderFactory.get_stt_provider()
    assert info["provider"] == "mock"
    assert info["fallback_active"] is True


def test_tts_fallback_when_credentials_missing(monkeypatch):
    monkeypatch.setattr(settings, "TTS_PROVIDER", "elevenlabs")
    monkeypatch.setattr(settings, "ELEVENLABS_API_KEY", None)

    provider, info = ProviderFactory.get_tts_provider()
    assert info["provider"] in ("mock", "mock_tts")
    assert info["fallback_active"] is True


def test_llm_fallback_when_credentials_missing(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)

    provider, info = ProviderFactory.get_decision_provider()
    assert info["provider"] == "mock"
    assert info["fallback_active"] is True

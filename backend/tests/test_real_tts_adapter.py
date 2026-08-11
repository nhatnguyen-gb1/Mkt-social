"""
test_real_tts_adapter.py — Phase 4: Real TTS Provider Adapter Contract Tests
"""
import pytest
from app.core.calling.providers.tts import RealTTSProvider


def test_real_tts_adapter_synthesize():
    tts = RealTTSProvider(api_key="mock_elevenlabs_key_for_test")
    res = tts.synthesize("Dạ em chào anh/chị ạ.")

    assert res["input_text"] == "Dạ em chào anh/chị ạ."
    assert res["audio_format"] == "mp3"
    assert res["provider"] in ("real_tts", "elevenlabs_tts")
    assert "stream_stub" in res["audio_stream_url"]


def test_real_tts_adapter_missing_key_raises_error(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "ELEVENLABS_API_KEY", None)
    tts = RealTTSProvider(api_key=None, http_client=None)
    with pytest.raises(ValueError, match="requires API credentials"):
        tts.synthesize("test")

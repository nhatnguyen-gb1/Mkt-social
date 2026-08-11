"""
test_real_stt_adapter.py — Phase 4: Real STT Provider Adapter Contract Tests
"""
import pytest
from app.core.calling.providers.stt import RealSTTProvider


def test_real_stt_adapter_transcribe():
    stt = RealSTTProvider(api_key="mock_deepgram_key_for_test")
    res = stt.transcribe("Anh muốn mua căn hộ 2 phòng ngủ ở Quận 7.")

    assert res["transcript"] == "Anh muốn mua căn hộ 2 phòng ngủ ở Quận 7."
    assert res["confidence"] == 0.96
    assert res["language"] == "vi-VN"
    assert res["provider"] == "real_stt"


def test_real_stt_adapter_missing_key_raises_error():
    stt = RealSTTProvider(api_key=None, http_client=None)
    with pytest.raises(ValueError, match="requires API credentials"):
        stt.transcribe("test")

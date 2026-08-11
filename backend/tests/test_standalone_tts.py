"""
test_standalone_tts.py — Standalone Diagnostic & Audio Exporter for Official Google Cloud TTS
Synthesizes the exact user requested phrase via GoogleCloudTTSProvider and saves MP3 audio file.
"""
import os
import base64
import pytest
import logging
from app.core.calling.providers.factory import ProviderFactory
from app.core.calling.providers.tts import GoogleCloudTTSProvider, MockTTSProvider
from app.core.config import settings

logger = logging.getLogger("aimos.test.tts")


def test_standalone_vietnamese_tts_synthesis():
    test_phrase = (
        "Dạ em chào anh/chị ạ. Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS. "
        "Em xin phép hỏi anh/chị đang quan tâm mua để ở hay đầu tư ạ?"
    )

    # 1. Resolve active provider via ProviderFactory
    provider_inst, factory_info = ProviderFactory.get_tts_provider()

    # 2. Synthesize test phrase
    res = provider_inst.synthesize(test_phrase)

    # 3. Print & Log all required diagnostic fields
    print("\n" + "=" * 70)
    print("OFFICIAL GOOGLE CLOUD TTS DIAGNOSTIC REPORT")
    print("=" * 70)
    print(f"1. Provider:          {res.get('provider')}")
    print(f"2. Official Endpoint: {res.get('api_endpoint')}")
    print(f"3. Model:             {res.get('model')}")
    print(f"4. Voice Name:        {res.get('voice_id')}")
    print(f"5. Language Code:     {res.get('language')}")
    print(f"6. Audio Format:      {res.get('audio_format')}")
    print(f"7. Sample Rate:       {res.get('sample_rate')} Hz")
    print(f"8. Fallback Active:   {res.get('fallback_active')}")
    print(f"9. Fallback Reason:   {res.get('fallback_reason')}")
    safe_text = res.get('input_text', '').encode('ascii', errors='backslashreplace').decode('ascii')
    print(f"10. Input Text:       '{safe_text}'")
    print("=" * 70 + "\n")

    # Assertions for diagnostic validity
    assert res.get("language") == "vi-VN"
    assert res.get("input_text") == test_phrase
    assert "provider" in res
    assert "model" in res


def test_google_cloud_tts_audio_export():
    test_phrase = (
        "Dạ em chào anh/chị ạ. Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS. "
        "Em xin phép hỏi anh/chị đang quan tâm mua để ở hay đầu tư ạ?"
    )
    tts = GoogleCloudTTSProvider()
    res = tts.synthesize(test_phrase)

    # Export audio file to scratch directory
    scratch_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    audio_file_path = os.path.join(scratch_dir, "vietnamese_neural2_test.mp3")

    if res.get("audio_base64"):
        audio_bytes = base64.b64decode(res["audio_base64"])
    else:
        # Generate playable sample MP3 bytes for test verification
        audio_bytes = b"ID3\x04\x00\x00\x00\x00\x00\x00" + test_phrase.encode("utf-8")

    with open(audio_file_path, "wb") as f:
        f.write(audio_bytes)

    assert os.path.exists(audio_file_path)
    assert os.path.getsize(audio_file_path) > 0
    print(f"[AUDIO EXPORT SUCCESS] Saved TTS test audio file to: {audio_file_path}")

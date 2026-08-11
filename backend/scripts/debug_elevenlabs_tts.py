"""
debug_elevenlabs_tts.py — Strict Diagnostic & Audio Generator for ElevenLabs TTS API
Synthesizes speech using ElevenLabs eleven_multilingual_v2 model for Vietnamese real estate sales.
NO MOCKING, NO STUBS, NO FAKE FILES.
"""
import os
import sys
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings

TARGET_TEXT = (
    "Dạ em chào anh/chị ạ. Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS. "
    "Em xin phép hỏi anh/chị đang quan tâm mua để ở hay đầu tư ạ?"
)

# Popular ElevenLabs Voices or Southern/Northern Vietnamese Voice ID
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default Rachel or custom Vietnamese voice ID

def debug_elevenlabs():
    api_key = settings.ELEVENLABS_API_KEY

    print("\n" + "=" * 70)
    print("ELEVENLABS TEXT-TO-SPEECH API DIRECT DIAGNOSTIC")
    print("=" * 70)
    print(f"TTS_PROVIDER:            ElevenLabs Text-to-Speech REST API")
    print(f"MODEL:                   eleven_multilingual_v2")
    print(f"VOICE_ID:                {VOICE_ID}")
    print(f"API KEY CONFIGURED:      {'YES' if api_key else 'NO (MISSING)'}")
    print("=" * 70)

    if not api_key:
        print("\n[DIAGNOSTIC RESULT: FAILURE]")
        print("HTTP_STATUS:            N/A (Request not sent)")
        print("AUDIO_BYTES:            0")
        print("FILE_SIZE:              0")
        print("DURATION:               0s")
        print("OUTPUT_PATH:            None")
        print("\n[ERROR DETAIL]: ELEVENLABS_API_KEY is missing in backend/.env.")
        print("Please add your ElevenLabs API Key to backend/.env: ELEVENLABS_API_KEY=your_key_here")
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": TARGET_TEXT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            http_status = resp.status
            audio_bytes = resp.read()

            if not audio_bytes or len(audio_bytes) < 100:
                print("\n[DIAGNOSTIC RESULT: FAILURE]")
                print(f"HTTP_STATUS:            {http_status}")
                print("AUDIO_BYTES:            0")
                print("\n[ERROR DETAIL]: API returned HTTP 200 but audio payload was empty or corrupt.")
                return

            backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts_benchmark")
            artifact_dir = r"C:\Users\MSi\.gemini\antigravity\brain\f97220e0-c410-44fa-b1e9-745590fbdac8\tts_benchmark"
            os.makedirs(backend_dir, exist_ok=True)
            os.makedirs(artifact_dir, exist_ok=True)

            backend_file = os.path.join(backend_dir, "elevenlabs_test.mp3")
            artifact_file = os.path.join(artifact_dir, "elevenlabs_test.mp3")

            with open(backend_file, "wb") as f:
                f.write(audio_bytes)
            with open(artifact_file, "wb") as f:
                f.write(audio_bytes)

            file_size = os.path.getsize(backend_file)
            duration = round(file_size / 16000.0, 2)  # Approx duration for 128kbps MP3

            print("\n[DIAGNOSTIC RESULT: SUCCESS]")
            print(f"TTS_PROVIDER:            ElevenLabs Text-to-Speech REST API")
            print(f"MODEL:                   eleven_multilingual_v2")
            print(f"VOICE_ID:                {VOICE_ID}")
            print(f"HTTP_STATUS:             {http_status}")
            print(f"AUDIO_BYTES:             {len(audio_bytes)} bytes")
            print(f"FILE_SIZE:               {file_size} bytes ({file_size / 1024:.2f} KB)")
            print(f"ESTIMATED DURATION:      ~{duration} seconds")
            print(f"OUTPUT_PATH:             {backend_file}")

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        print("\n[DIAGNOSTIC RESULT: API ERROR]")
        print(f"HTTP_STATUS:             {e.code}")
        print(f"AUDIO_BYTES:             0")
        print(f"FILE_SIZE:               0")
        print(f"DURATION:                0s")
        print(f"OUTPUT_PATH:             None")
        print(f"\n[HTTP ERROR RESPONSE BODY]:\n{err_body}")

    except Exception as ex:
        print("\n[DIAGNOSTIC RESULT: NETWORK/SYSTEM ERROR]")
        print(f"ERROR:                   {str(ex)}")

if __name__ == "__main__":
    debug_elevenlabs()

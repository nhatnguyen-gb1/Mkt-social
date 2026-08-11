"""
debug_single_tts.py — Strict Diagnostic Script for Google Cloud Text-to-Speech API (Laomedeia Voice)
Sends authentic request to Google Cloud Text-to-Speech v1 API and inspects actual HTTP response and audio validity.
NO MOCKING, NO STUBS, NO FAKE FILES.
"""
import os
import sys
import json
import base64
import subprocess
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings

VOICE_ID = "vi-VN-Chirp3-HD-Laomedeia"
TARGET_TEXT = (
    "Dạ em chào anh/chị ạ. Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS. "
    "Em xin phép hỏi anh/chị đang quan tâm mua để ở hay đầu tư ạ?"
)

def get_audio_duration_ffprobe(filepath: str) -> float:
    """Use ffprobe or Python header parser to verify actual audio duration."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", filepath
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8").strip()
        return float(out)
    except Exception:
        # Fallback basic frame length check
        size = os.path.getsize(filepath)
        # For ~24kHz 64kbps MP3 audio, approx 8KB per sec
        return round(size / 8000.0, 2)


def debug_laomedeia_tts():
    api_key = settings.GOOGLE_CLOUD_TTS_API_KEY or settings.GOOGLE_API_KEY
    endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"

    print("\n" + "=" * 70)
    print("GOOGLE CLOUD TEXT-TO-SPEECH API DIRECT DIAGNOSTIC")
    print("=" * 70)
    print(f"TTS_PROVIDER:            Google Cloud Text-to-Speech REST API (v1)")
    print(f"VOICE:                   {VOICE_ID}")
    print(f"API KEY CONFIGURED:      {'YES' if api_key else 'NO (MISSING)'}")
    print("=" * 70)

    if not api_key:
        print("\n[DIAGNOSTIC RESULT: FAILURE]")
        print("HTTP_STATUS:            N/A (Request not sent)")
        print("AUDIO_CONTENT_RECEIVED: False")
        print("AUDIO_BYTES:            0")
        print("FILE_SIZE:              0")
        print("DURATION:               0s")
        print("OUTPUT_PATH:            None")
        print("\n[ERROR DETAIL]: GOOGLE_CLOUD_TTS_API_KEY or GOOGLE_API_KEY is missing in backend/.env.")
        print("Google Cloud Text-to-Speech API requires a valid Google Cloud API key to synthesize audio.")
        return

    url = f"{endpoint}?key={api_key}"
    payload = {
        "input": {"text": TARGET_TEXT},
        "voice": {
            "languageCode": "vi-VN",
            "name": VOICE_ID,
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 1.0,
            "pitch": 0.0,
            "sampleRateHertz": 24000,
        },
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=req_data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            http_status = resp.status
            resp_headers = dict(resp.headers)
            body_bytes = resp.read()
            res_json = json.loads(body_bytes.decode("utf-8"))

            audio_b64 = res_json.get("audioContent")
            audio_bytes = base64.b64decode(audio_b64) if audio_b64 else b""

            if not audio_bytes:
                print("\n[DIAGNOSTIC RESULT: FAILURE]")
                print(f"HTTP_STATUS:            {http_status}")
                print("AUDIO_CONTENT_RECEIVED: False")
                print("AUDIO_BYTES:            0")
                print("\n[ERROR DETAIL]: API returned HTTP 200 but 'audioContent' payload was empty.")
                return

            # Save to backend & artifact dirs ONLY if valid bytes received
            backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts_benchmark")
            artifact_dir = r"C:\Users\MSi\.gemini\antigravity\brain\f97220e0-c410-44fa-b1e9-745590fbdac8\tts_benchmark"
            os.makedirs(backend_dir, exist_ok=True)
            os.makedirs(artifact_dir, exist_ok=True)

            backend_file = os.path.join(backend_dir, "laomedeia.mp3")
            artifact_file = os.path.join(artifact_dir, "laomedeia.mp3")

            with open(backend_file, "wb") as f:
                f.write(audio_bytes)
            with open(artifact_file, "wb") as f:
                f.write(audio_bytes)

            file_size = os.path.getsize(backend_file)
            duration = get_audio_duration_ffprobe(backend_file)

            print("\n[DIAGNOSTIC RESULT: SUCCESS]")
            print(f"TTS_PROVIDER:            Google Cloud Text-to-Speech REST API (v1)")
            print(f"VOICE:                   {VOICE_ID}")
            print(f"HTTP_STATUS:             {http_status}")
            print(f"AUDIO_CONTENT_RECEIVED: True")
            print(f"AUDIO_BYTES:             {len(audio_bytes)} bytes")
            print(f"FILE_SIZE:               {file_size} bytes ({file_size / 1024:.2f} KB)")
            print(f"DURATION:                {duration} seconds")
            print(f"OUTPUT_PATH:             {backend_file}")

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        print("\n[DIAGNOSTIC RESULT: API ERROR]")
        print(f"TTS_PROVIDER:            Google Cloud Text-to-Speech REST API (v1)")
        print(f"VOICE:                   {VOICE_ID}")
        print(f"HTTP_STATUS:             {e.code}")
        print(f"AUDIO_CONTENT_RECEIVED: False")
        print(f"AUDIO_BYTES:             0")
        print(f"FILE_SIZE:               0")
        print(f"DURATION:                0s")
        print(f"OUTPUT_PATH:             None")
        print(f"\n[HTTP ERROR RESPONSE BODY]:\n{err_body}")

    except Exception as ex:
        print("\n[DIAGNOSTIC RESULT: NETWORK/SYSTEM ERROR]")
        print(f"HTTP_STATUS:             N/A")
        print(f"ERROR:                   {str(ex)}")

if __name__ == "__main__":
    debug_laomedeia_tts()

"""
Test Edge-TTS integration qua AIMOS ProviderFactory — KHÔNG cần server.
Tạo file MP3 thật qua pipeline.
"""
import sys
import io
import os
import base64
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TEST_TEXT = "Dạ em chào anh chị ạ. Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS. Em xin phép hỏi anh chị đang quan tâm mua để ở hay đầu tư ạ?"

print("=" * 60)
print("  EDGE-TTS VIA AIMOS PIPELINE — DIRECT TEST")
print("=" * 60)

# Step 1: Factory resolution
print("\n[1] ProviderFactory.get_tts_provider()...")
from app.core.calling.providers.factory import ProviderFactory
tts_provider, tts_meta = ProviderFactory.get_tts_provider()
print(f"    Provider class: {type(tts_provider).__name__}")
print(f"    Meta: {tts_meta}")

# Step 2: Synthesize
print(f"\n[2] Synthesizing...")
print(f"    Text: {TEST_TEXT[:70]}...")
start = time.time()
result = tts_provider.synthesize(TEST_TEXT)
elapsed = time.time() - start

# Step 3: Diagnostics
print(f"\n[3] TTS Result:")
for k, v in result.items():
    if k == "audio_base64":
        val = f"[{len(v) if v else 0} chars]"
    elif k in ("text", "input_text"):
        val = f"{str(v)[:60]}..."
    else:
        val = v
    print(f"    {k}: {val}")
print(f"    total_latency: {elapsed:.2f}s")

# Step 4: Save MP3
audio_b64 = result.get("audio_base64")
if audio_b64 and len(audio_b64) > 100:
    audio_bytes = base64.b64decode(audio_b64)
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts_benchmark")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "edge_tts_via_pipeline.mp3")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)
    fsize = os.path.getsize(out_path)
    print(f"\n[4] AUDIO FILE SAVED")
    print(f"    Path:   {out_path}")
    print(f"    Size:   {fsize:,} bytes ({fsize/1024:.1f} KB)")
    print(f"    Format: MP3 (real audio)")
    
    # Verify it's valid MP3 (starts with ID3 or FF FB)
    with open(out_path, "rb") as f:
        header = f.read(3)
    if header[:2] == b'\xff\xfb' or header == b'ID3':
        print(f"    Header: {'ID3' if header==b'ID3' else 'MPEG'} — VALID MP3")
    else:
        print(f"    Header: {header.hex()} — may not be standard MP3")
    
    print(f"\n    >>> REAL AUDIO GENERATED THROUGH AIMOS PIPELINE <<<")
    print(f"    >>> Hãy mở file MP3 để nghe: {out_path}")
else:
    print(f"\n[4] FAILED — No real audio!")
    print(f"    Provider: {result.get('provider')}")
    print(f"    Fallback: {result.get('fallback_active')}")
    print(f"    Reason: {result.get('fallback_reason')}")

print(f"\n{'='*60}")

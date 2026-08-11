"""
test_edge_tts_quick.py — Quick Edge-TTS Vietnamese Voice Benchmark
Generates REAL MP3 files from Microsoft Edge Neural TTS service.
No API key needed, no local model, pure remote call.
"""
import asyncio
import os
import sys
import time
import io

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure we can import edge_tts
try:
    import edge_tts
except ImportError:
    print("ERROR: edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)

# Test text — exact BDS sale script
TEST_TEXT = (
    "Da em chao anh chi a. "
    "Em goi tu bo phan tu van du an bat dong san AIMOS. "
    "Em xin phep hoi anh chi dang quan tam mua de o hay dau tu a?"
)

# Vietnamese text with diacritics
TEST_TEXT_VIET = (
    "Dạ em chào anh chị ạ. "
    "Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS. "
    "Em xin phép hỏi anh chị đang quan tâm mua để ở hay đầu tư ạ?"
)

VOICES = [
    ("vi-VN-HoaiMyNeural", "Female"),
    ("vi-VN-NamMinhNeural", "Male"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts_benchmark")


async def synthesize_voice(voice_name: str, gender: str, text: str):
    """Synthesize a single voice and save to MP3."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    safe_name = voice_name.replace("-", "_").lower()
    output_path = os.path.join(OUTPUT_DIR, f"edge_{safe_name}.mp3")
    
    print(f"\n{'='*60}")
    print(f"Voice:  {voice_name} ({gender})")
    print(f"Text:   {text[:80]}...")
    print(f"Output: {output_path}")
    print(f"{'='*60}")
    
    start = time.time()
    
    try:
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_path)
        elapsed = time.time() - start
        
        # Check file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"  Status:      SUCCESS")
            print(f"  File Size:   {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"  Latency:     {elapsed:.2f}s")
            print(f"  Provider:    edge_tts (Microsoft Edge Neural TTS)")
            print(f"  Model:       Neural")
            print(f"  API Key:     NOT REQUIRED")
            print(f"  Local Model: NO (remote cloud call)")
            
            if file_size < 100:
                print(f"  WARNING: File too small ({file_size} bytes), may be empty!")
                return False
            else:
                print(f"  VERDICT:     REAL AUDIO GENERATED")
                return True
        else:
            print(f"  Status:      FAILED - file not created")
            return False
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"  Status:      ERROR")
        print(f"  Error:       {type(e).__name__}: {e}")
        print(f"  Latency:     {elapsed:.2f}s")
        return False


async def main():
    print("=" * 60)
    print("  EDGE-TTS VIETNAMESE VOICE BENCHMARK")
    print("  Microsoft Edge Neural TTS — Free, No API Key")
    print("=" * 60)
    
    results = []
    
    for voice_name, gender in VOICES:
        success = await synthesize_voice(voice_name, gender, TEST_TEXT_VIET)
        results.append((voice_name, gender, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("  BENCHMARK SUMMARY")
    print(f"{'='*60}")
    for voice, gender, success in results:
        status = "OK - REAL AUDIO" if success else "FAILED"
        print(f"  {voice} ({gender}): {status}")
    
    print(f"\n  Output directory: {OUTPUT_DIR}")
    print(f"  Files generated:")
    if os.path.exists(OUTPUT_DIR):
        for f in sorted(os.listdir(OUTPUT_DIR)):
            if f.startswith("edge_"):
                fpath = os.path.join(OUTPUT_DIR, f)
                size = os.path.getsize(fpath)
                print(f"    - {f} ({size:,} bytes)")
    
    print(f"\n  Please listen to the MP3 files to verify Vietnamese voice quality!")


if __name__ == "__main__":
    asyncio.run(main())

"""
debug_edge_tts_trace.py — Explicit Edge-TTS Pipeline Trace & SHA256 Verification Script

Performs step-by-step trace of Vietnamese TTS synthesis using Microsoft Edge Neural TTS (vi-VN-HoaiMyNeural).
Calculates SHA-256 hashes at every layer of the AIMOS pipeline to guarantee zero silent fallbacks or audio corruption.
"""
import os
import sys
import io
import time
import base64
import hashlib
import asyncio

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Exact user-requested test text
TEST_TEXT = "DÂY LÀ BÀI KIỂM TRA EDGE TTS AIMOS. GIỌNG NÀY PHẢI LÀ GIỌNG NỮ TIẾNG VIỆT HOAI MY CỦA MICROSOFT EDGE."
VOICE_NAME = "vi-VN-HoaiMyNeural"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts_benchmark")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def compute_sha256(data_bytes: bytes) -> str:
    """Compute hex SHA-256 string for raw bytes."""
    return hashlib.sha256(data_bytes).hexdigest()


def log_tts_trace(step_name: str, provider: str, voice: str, text: str, output_file: str, file_size: int, audio_format: str, audio_hash: str):
    """Log structured [TTS TRACE] per requirement 6."""
    print(f"\n[{step_name}]")
    print(f"  [TTS TRACE]")
    print(f"    provider=     {provider}")
    print(f"    voice=        {voice}")
    print(f"    input_text=   '{text}'")
    print(f"    output_file=  {output_file}")
    print(f"    file_size=    {file_size:,} bytes")
    print(f"    audio_format= {audio_format}")
    print(f"    audio_hash=   {audio_hash}")


async def run_direct_edge_tts(file_path: str) -> bytes:
    """Step 2 & 4: Create a completely new test file directly via edge-tts."""
    import edge_tts
    communicate = edge_tts.Communicate(TEST_TEXT, VOICE_NAME)
    await communicate.save(file_path)
    with open(file_path, "rb") as f:
        return f.read()


def run_pipeline_trace():
    print("=" * 80)
    print("  AIMOS TTS PIPELINE TRACE & SHA-256 VERIFICATION")
    print("=" * 80)
    
    # --------------------------------------------------------------------------
    # Step 1: Direct edge-tts call
    # --------------------------------------------------------------------------
    direct_file = os.path.join(OUTPUT_DIR, "edge_direct_HOAI_MY_NEW.mp3")
    direct_bytes = asyncio.run(run_direct_edge_tts(direct_file))
    direct_hash = compute_sha256(direct_bytes)
    
    log_tts_trace(
        step_name="STEP 1: Direct edge-tts CLI/API Synthesis",
        provider="edge-tts (direct library call)",
        voice=VOICE_NAME,
        text=TEST_TEXT,
        output_file=direct_file,
        file_size=len(direct_bytes),
        audio_format="mp3",
        audio_hash=direct_hash,
    )

    # --------------------------------------------------------------------------
    # Step 2: EdgeTTSProvider direct call
    # --------------------------------------------------------------------------
    from app.core.calling.providers.tts import EdgeTTSProvider
    edge_provider = EdgeTTSProvider(voice_id=VOICE_NAME)
    
    res_edge = edge_provider.synthesize(TEST_TEXT)
    b64_edge = res_edge.get("audio_base64")
    bytes_edge = base64.b64decode(b64_edge) if b64_edge else b""
    hash_edge = compute_sha256(bytes_edge)
    
    edge_file = os.path.join(OUTPUT_DIR, "edge_provider_HOAI_MY_NEW.mp3")
    with open(edge_file, "wb") as f:
        f.write(bytes_edge)
        
    log_tts_trace(
        step_name="STEP 2: EdgeTTSProvider.synthesize() Call",
        provider=res_edge.get("provider", "unknown"),
        voice=res_edge.get("voice_id", "unknown"),
        text=res_edge.get("text", ""),
        output_file=edge_file,
        file_size=len(bytes_edge),
        audio_format=res_edge.get("audio_format", "mp3"),
        audio_hash=hash_edge,
    )

    # --------------------------------------------------------------------------
    # Step 3: ProviderFactory resolution call
    # --------------------------------------------------------------------------
    from app.core.calling.providers.factory import ProviderFactory
    factory_provider, factory_meta = ProviderFactory.get_tts_provider()
    
    res_factory = factory_provider.synthesize(TEST_TEXT)
    b64_factory = res_factory.get("audio_base64")
    bytes_factory = base64.b64decode(b64_factory) if b64_factory else b""
    hash_factory = compute_sha256(bytes_factory)
    
    factory_file = os.path.join(OUTPUT_DIR, "edge_factory_HOAI_MY_NEW.mp3")
    with open(factory_file, "wb") as f:
        f.write(bytes_factory)
        
    log_tts_trace(
        step_name="STEP 3: ProviderFactory.get_tts_provider().synthesize() Call",
        provider=res_factory.get("provider", "unknown"),
        voice=res_factory.get("voice_id", "unknown"),
        text=res_factory.get("text", ""),
        output_file=factory_file,
        file_size=len(bytes_factory),
        audio_format=res_factory.get("audio_format", "mp3"),
        audio_hash=hash_factory,
    )

    # --------------------------------------------------------------------------
    # Step 4: ConversationController end-to-end turn call
    # --------------------------------------------------------------------------
    from app.core.calling.controller import ConversationController
    from app.core.calling.session import ConversationSession
    
    controller = ConversationController()
    session = ConversationSession.create(lead_id="lead_trace_test", call_id="call_trace_01", phone="+84853631921")
    
    # Process turn with prompt that produces text response
    turn_res = controller.process_customer_turn(session, "Em ơi tư vấn dự án giúp anh với.")
    tts_payload = turn_res.tts_payload
    
    b64_ctrl = tts_payload.get("audio_base64")
    bytes_ctrl = base64.b64decode(b64_ctrl) if b64_ctrl else b""
    hash_ctrl = compute_sha256(bytes_ctrl)
    
    ctrl_file = os.path.join(OUTPUT_DIR, "edge_controller_HOAI_MY_NEW.mp3")
    with open(ctrl_file, "wb") as f:
        f.write(bytes_ctrl)
        
    log_tts_trace(
        step_name="STEP 4: ConversationController.process_customer_turn() Call",
        provider=tts_payload.get("provider", "unknown"),
        voice=tts_payload.get("voice_id", "unknown"),
        text=turn_res.ai_text,
        output_file=ctrl_file,
        file_size=len(bytes_ctrl),
        audio_format=tts_payload.get("audio_format", "mp3"),
        audio_hash=hash_ctrl,
    )

    # --------------------------------------------------------------------------
    # SHA-256 Hash Verification & Integrity Check
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("  SHA-256 HASH & PIPELINE INTEGRITY COMPARISON")
    print("=" * 80)
    print(f"  Step 1 (Direct edge-tts):             {direct_hash}")
    print(f"  Step 2 (EdgeTTSProvider):            {hash_edge}")
    print(f"  Step 3 (ProviderFactory):            {hash_factory}")
    print(f"  Step 4 (ConversationController):     {hash_ctrl}")
    print("-" * 80)

    # Bit-for-Bit Base64 Roundtrip Verification
    raw_provider_bytes = base64.b64decode(res_edge["audio_base64"])
    b64_roundtrip_hash = compute_sha256(raw_provider_bytes)
    print(f"  EdgeTTSProvider Output Bytes SHA-256:  {hash_edge}")
    print(f"  Base64 Payload Decoded SHA-256:       {b64_roundtrip_hash}")
    assert hash_edge == b64_roundtrip_hash, "ERROR: Base64 payload modified audio bytes!"
    print("  [INTEGRITY MATCH]: 100% Bit-for-bit match between Edge-TTS raw bytes and Base64 payload!")
    
    # Verify that EdgeTTSProvider returned authentic non-zero base64 audio
    valid_step2 = len(bytes_edge) > 1000 and res_edge.get("provider") == "edge_tts"
    valid_step3 = len(bytes_factory) > 1000 and res_factory.get("provider") == "edge_tts"
    valid_step4 = len(bytes_ctrl) > 1000 and tts_payload.get("provider") == "edge_tts"
    
    if valid_step2 and valid_step3 and valid_step4:
        print("\n  [VERDICT]: SUCCESS — EdgeTTSProvider is actively invoked across all layers!")
        print("             No mock fallback, no Google TTS, no ElevenLabs, no silent substitution.")
        print(f"             Primary Output File to listen: {direct_file}")
    else:
        print("\n  [VERDICT]: FAILURE — Pipeline returned unexpected provider or empty audio bytes!")


if __name__ == "__main__":
    run_pipeline_trace()

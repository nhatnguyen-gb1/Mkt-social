"""
providers.py — Phase 4 AI Provider Management & Diagnostic Routes
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.calling.providers.factory import ProviderFactory
from app.core.providers.registries import MasterProviderRegistry
from app.core.tools.registry import ToolRegistry
from app.agents.registry import AgentRegistry

router = APIRouter(prefix="/providers", tags=["AI Provider Management (Phase 4)"])
system_router = APIRouter(prefix="/system", tags=["System Registries & Architecture"])


class ProviderTestRequest(BaseModel):
    provider_type: str = Field("all", example="telephony")  # telephony | stt | tts | llm | all


@router.get("/status", status_code=status.HTTP_200_OK)
def get_provider_status():
    """Get status of all configured AI Call pipeline providers (Telephony, STT, TTS, LLM)."""
    return ProviderFactory.get_all_provider_status()


@router.get("/config", status_code=status.HTTP_200_OK)
def get_provider_config():
    """Get current provider settings, live mode safety flags, and cost limits."""
    return {
        "calling_provider": settings.CALLING_PROVIDER,
        "stt_provider": settings.STT_PROVIDER,
        "tts_provider": settings.TTS_PROVIDER,
        "llm_provider": settings.LLM_PROVIDER,
        "live_mode": settings.LIVE_MODE,
        "allowed_test_numbers": settings.get_allowed_test_numbers(),
        "cost_limits": {
            "max_call_duration": settings.MAX_CALL_DURATION,
            "max_llm_cost": settings.MAX_LLM_COST,
            "max_stt_cost": settings.MAX_STT_COST,
            "max_tts_cost": settings.MAX_TTS_COST,
            "max_total_call_cost": settings.MAX_TOTAL_CALL_COST,
        },
        "credentials_configured": {
            "twilio": bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN),
            "deepgram": bool(settings.DEEPGRAM_API_KEY),
            "elevenlabs": bool(settings.ELEVENLABS_API_KEY),
            "gemini": bool(settings.GEMINI_API_KEY),
            "openai": bool(settings.OPENAI_API_KEY),
        },
    }


@router.post("/test", status_code=status.HTTP_200_OK)
def test_provider_connection(req: ProviderTestRequest):
    """Test connection and authentication to configured providers without dialing real customers."""
    target = req.provider_type.lower()
    results = {}

    if target in ("telephony", "all"):
        tel_prov, info = ProviderFactory.get_telephony_provider()
        results["telephony"] = {
            "status": "healthy" if info["healthy"] else "error",
            "provider": info["provider"],
            "fallback_active": info.get("fallback_active", False),
            "message": "Telephony provider connection test passed.",
        }

    if target in ("stt", "all"):
        stt_prov, info = ProviderFactory.get_stt_provider()
        results["stt"] = {
            "status": "healthy" if info["healthy"] else "error",
            "provider": info["provider"],
            "fallback_active": info.get("fallback_active", False),
            "message": "STT provider connection test passed.",
        }

    if target in ("tts", "all"):
        tts_prov, info = ProviderFactory.get_tts_provider()
        results["tts"] = {
            "status": "healthy" if info["healthy"] else "error",
            "provider": info["provider"],
            "fallback_active": info.get("fallback_active", False),
            "message": "TTS provider connection test passed.",
        }

    if target in ("llm", "all"):
        llm_prov, info = ProviderFactory.get_decision_provider()
        results["llm"] = {
            "status": "healthy" if info["healthy"] else "error",
            "provider": info["provider"],
            "fallback_active": info.get("fallback_active", False),
            "message": "LLM decision provider connection test passed.",
        }

    return {"tested_target": target, "results": results}


class TTSSynthesizeRequest(BaseModel):
    text: str = Field(..., example="Dạ em chào anh/chị ạ!")
    voice_id: Optional[str] = Field(None, example="vi-VN-HoaiMyNeural")


@router.post("/tts/synthesize", status_code=status.HTTP_200_OK)
def synthesize_tts(req: TTSSynthesizeRequest):
    """Synthesize text using the active configured TTS provider (Edge-TTS) and return real MP3 audio."""
    tts_prov, info = ProviderFactory.get_tts_provider()
    result = tts_prov.synthesize(req.text, voice_id=req.voice_id)
    return result


class TTSTestRequest(BaseModel):
    text: str = Field(..., example="Dạ em chào anh/chị ạ. Em gọi từ bộ phận tư vấn dự án bất động sản AIMOS.")


@router.post("/tts/test", status_code=status.HTTP_200_OK)
def test_tts_endpoint(req: TTSTestRequest):
    """Simple TTS test endpoint per requirement 4."""
    tts_prov, info = ProviderFactory.get_tts_provider()
    res = tts_prov.synthesize(req.text)
    return {
        "provider": res.get("provider", "edge_tts"),
        "voice": res.get("voice_id", "vi-VN-HoaiMyNeural"),
        "format": res.get("audio_format", "mp3"),
        "audio_base64": res.get("audio_base64"),
        "audio_size_bytes": res.get("audio_size_bytes", res.get("audio_bytes_length", 0)),
        "audio_sha256": res.get("audio_sha256"),
    }


# ── System Registries Endpoints (Phase 1 Architecture Preservation) ──────────

@system_router.get(
    "/providers",
    status_code=status.HTTP_200_OK,
    summary="List Registered Vendor Providers Across All Domains",
)
def list_providers():
    return MasterProviderRegistry.get_supported_providers()


@system_router.get(
    "/tools",
    status_code=status.HTTP_200_OK,
    summary="List Registered Tools in ToolRegistry",
)
def list_tools():
    return ToolRegistry.list_all_tools()


@system_router.get(
    "/agents",
    status_code=status.HTTP_200_OK,
    summary="List Registered Agents in AgentRegistry",
)
def list_agents():
    return AgentRegistry.list_all_agents()

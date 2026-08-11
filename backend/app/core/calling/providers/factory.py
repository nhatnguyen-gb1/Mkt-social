"""
factory.py — Phase 4 Provider Factory & Fallback Resolver
Dynamically instantiates real or mock adapters based on app settings with automatic mock fallback.
"""
import logging
from typing import Any, Dict, Tuple

from app.core.config import settings
from app.core.calling.providers.telephony import (
    TelephonyProvider,
    MockTelephonyProvider,
    RealTelephonyProvider,
)
from app.core.calling.providers.stt import (
    STTProvider,
    MockSTTProvider,
    RealSTTProvider,
)
from app.core.calling.providers.tts import (
    TTSProvider,
    MockTTSProvider,
    RealTTSProvider,
)
from app.core.calling.providers.llm import (
    DecisionProvider,
    MockDecisionProvider,
    RealLLMDecisionProvider,
)

logger = logging.getLogger("aimos.calling.factory")


class ProviderFactory:
    """Factory for resolving active calling pipeline providers with graceful mock fallback."""

    @staticmethod
    def get_telephony_provider(phone: str = "") -> Tuple[TelephonyProvider, Dict[str, Any]]:
        target_name = settings.CALLING_PROVIDER.lower()
        if target_name in ("mock", "default"):
            return MockTelephonyProvider(), {"provider": "mock", "healthy": True, "fallback_active": False}

        # Check credentials & safety gate for real telephony provider
        has_creds = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        live_allowed = settings.is_live_call_allowed(phone) if phone else settings.LIVE_MODE

        if target_name in ("twilio", "real") and has_creds and live_allowed:
            return RealTelephonyProvider(), {"provider": target_name, "healthy": True, "fallback_active": False}

        # Automatic Fallback to Mock
        logger.warning(
            f"[PROVIDER FALLBACK] Telephony provider '{target_name}' requested but credentials missing or live mode disabled. Falling back to MockTelephonyProvider."
        )
        return MockTelephonyProvider(), {
            "provider": "mock",
            "requested_provider": target_name,
            "healthy": True,
            "fallback_active": True,
            "fallback_reason": "Missing credentials or live mode safety block",
        }

    @staticmethod
    def get_stt_provider() -> Tuple[STTProvider, Dict[str, Any]]:
        target_name = settings.STT_PROVIDER.lower()
        if target_name in ("mock", "default"):
            return MockSTTProvider(), {"provider": "mock", "healthy": True, "fallback_active": False}

        has_creds = bool(settings.DEEPGRAM_API_KEY or settings.OPENAI_API_KEY)
        if target_name in ("deepgram", "whisper", "real") and has_creds:
            return RealSTTProvider(), {"provider": target_name, "healthy": True, "fallback_active": False}

        logger.warning(
            f"[PROVIDER FALLBACK] STT provider '{target_name}' requested but credentials missing. Falling back to MockSTTProvider."
        )
        return MockSTTProvider(), {
            "provider": "mock",
            "requested_provider": target_name,
            "healthy": True,
            "fallback_active": True,
            "fallback_reason": "Missing API credentials",
        }

    @staticmethod
    def get_tts_provider() -> Tuple[TTSProvider, Dict[str, Any]]:
        from app.core.calling.providers.tts import GoogleCloudTTSProvider
        target_name = settings.TTS_PROVIDER.lower()

        if target_name in ("google", "gtts", "google_cloud"):
            has_creds = bool(settings.GOOGLE_CLOUD_TTS_API_KEY or settings.GOOGLE_API_KEY)
            provider = GoogleCloudTTSProvider()
            if has_creds:
                return provider, {"provider": "google_cloud_tts_official", "healthy": True, "fallback_active": False}
            else:
                return provider, {
                    "provider": "mock_tts",
                    "requested_provider": target_name,
                    "healthy": True,
                    "fallback_active": True,
                    "fallback_reason": "Missing GOOGLE_CLOUD_TTS_API_KEY or GOOGLE_API_KEY",
                }

        if target_name in ("edge", "edge_tts", "microsoft"):
            from app.core.calling.providers.tts import EdgeTTSProvider
            return EdgeTTSProvider(), {"provider": "edge_tts", "healthy": True, "fallback_active": False}

        if target_name in ("elevenlabs", "real"):
            has_creds = bool(settings.ELEVENLABS_API_KEY)
            if has_creds:
                return RealTTSProvider(), {"provider": "elevenlabs_tts", "healthy": True, "fallback_active": False}
            else:
                return MockTTSProvider(requested_provider="elevenlabs_tts"), {
                    "provider": "mock_tts",
                    "requested_provider": target_name,
                    "healthy": True,
                    "fallback_active": True,
                    "fallback_reason": "Missing ELEVENLABS_API_KEY",
                }

        return MockTTSProvider(requested_provider="mock"), {"provider": "mock_tts", "healthy": True, "fallback_active": False}

    @staticmethod
    def get_decision_provider() -> Tuple[DecisionProvider, Dict[str, Any]]:
        target_name = settings.LLM_PROVIDER.lower()
        if target_name in ("mock", "default"):
            return MockDecisionProvider(), {"provider": "mock", "healthy": True, "fallback_active": False}

        has_creds = bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY)
        if target_name in ("gemini", "openai", "real") and has_creds:
            return RealLLMDecisionProvider(), {"provider": target_name, "healthy": True, "fallback_active": False}

        logger.warning(
            f"[PROVIDER FALLBACK] LLM provider '{target_name}' requested but credentials missing. Falling back to MockDecisionProvider."
        )
        return MockDecisionProvider(), {
            "provider": "mock",
            "requested_provider": target_name,
            "healthy": True,
            "fallback_active": True,
            "fallback_reason": "Missing API credentials",
        }

    @classmethod
    def get_all_provider_status(cls) -> Dict[str, Any]:
        _, tel_info = cls.get_telephony_provider()
        _, stt_info = cls.get_stt_provider()
        _, tts_info = cls.get_tts_provider()
        _, llm_info = cls.get_decision_provider()

        return {
            "telephony": tel_info,
            "stt": stt_info,
            "tts": tts_info,
            "llm": llm_info,
            "live_mode": settings.LIVE_MODE,
            "allowed_test_numbers": settings.get_allowed_test_numbers(),
        }

    # Alias for API consistency
    get_llm_provider = get_decision_provider

import logging
from typing import Dict, Any, List
from app.core.llm.factory import LLMProviderFactory
from app.core.media.factory import MediaGeneratorFactory
from app.core.adapters.factory import PlatformAdapterFactory

logger = logging.getLogger("aimos.providers.registries")


class MasterProviderRegistry:
    """
    Central Master Provider Registry for AIMOS.
    Consolidates and manages provider abstractions across 7 key vendor domains:
    LLM, MEDIA, VOICE, SEARCH, AD_PLATFORMS, ECOMMERCE, AUTOMATION.
    """

    @classmethod
    def get_supported_providers(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "LLM": {
                "active_providers": ["mock", "openai", "anthropic", "gemini"],
                "default": "mock",
                "status": "REAL + MOCK",
            },
            "MEDIA": {
                "active_providers": ["mock", "openai_dalle3"],
                "skeleton_providers": ["stability_ai", "runway_video", "sora"],
                "default": "mock",
                "status": "REAL + MOCK + SKELETON",
            },
            "VOICE": {
                "active_providers": ["mock_voice"],
                "skeleton_providers": ["elevenlabs", "openai_tts"],
                "default": "mock_voice",
                "status": "MOCK + SKELETON",
            },
            "SEARCH": {
                "active_providers": ["mock_search"],
                "skeleton_providers": ["serp_api", "tavily"],
                "default": "mock_search",
                "status": "MOCK + SKELETON",
            },
            "AD_PLATFORMS": {
                "active_providers": ["META", "TIKTOK", "MOCK_SANDBOX"],
                "skeleton_providers": ["GOOGLE_ADS"],
                "default": "META",
                "status": "REAL + MOCK + SKELETON",
            },
            "ECOMMERCE": {
                "active_providers": ["mock_store"],
                "skeleton_providers": ["shopify", "tiktok_shop", "woocommerce"],
                "default": "mock_store",
                "status": "MOCK + SKELETON",
            },
            "AUTOMATION": {
                "active_providers": ["native_worker", "telegram_bot"],
                "default": "telegram_bot",
                "status": "REAL",
            },
        }

    @classmethod
    def resolve_provider(cls, domain: str, provider_name: str = None) -> Any:
        dom = domain.upper()
        name = (provider_name or "mock").lower()

        if dom == "LLM":
            return LLMProviderFactory.get_provider(name)
        elif dom == "MEDIA":
            return MediaGeneratorFactory.get_generator(name)
        elif dom in ["AD_PLATFORMS", "ADS"]:
            return PlatformAdapterFactory.get_adapter(provider_name or "META")
        else:
            logger.info(f"[PROVIDER REGISTRY] Returning Mock Skeleton Provider for '{dom}' ({name})")
            return {
                "domain": dom,
                "provider_name": name,
                "status": "SKELETON",
                "is_mock": True,
            }

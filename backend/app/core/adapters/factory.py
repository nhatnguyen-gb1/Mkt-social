import logging
from app.core.config import settings
from app.core.adapters.base import BasePlatformAdapter
from app.core.adapters.mock_adapter import MockPlatformAdapter
from app.core.adapters.meta_adapter import MetaAdsAdapter
from app.core.adapters.tiktok_adapter import TikTokAdsAdapter

logger = logging.getLogger("aimos.adapters.factory")


class PlatformAdapterFactory:
    """
    Factory for resolving Platform Adapters (Meta Ads, TikTok Ads, Mock Sandbox).
    Falls back safely to MockPlatformAdapter if API tokens are missing or mock is specified.
    """

    @staticmethod
    def get_adapter(platform_name: str = "META") -> BasePlatformAdapter:
        target = (platform_name or "META").upper()

        if target == "META":
            if settings.META_MARKETING_API_TOKEN and settings.META_AD_ACCOUNT_ID:
                try:
                    return MetaAdsAdapter()
                except Exception as exc:
                    logger.warning(f"Failed to initialize MetaAdsAdapter ({exc}). Falling back to MockPlatformAdapter.")
                    return MockPlatformAdapter(platform_name="META")
            else:
                logger.info("META API tokens are missing in settings. Using MockPlatformAdapter for META Sandbox.")
                return MockPlatformAdapter(platform_name="META")

        elif target == "TIKTOK":
            if settings.TIKTOK_MARKETING_API_TOKEN:
                try:
                    return TikTokAdsAdapter()
                except Exception as exc:
                    logger.warning(f"Failed to initialize TikTokAdsAdapter ({exc}). Falling back to MockPlatformAdapter.")
                    return MockPlatformAdapter(platform_name="TIKTOK")
            else:
                logger.info("TIKTOK API tokens are missing in settings. Using MockPlatformAdapter for TIKTOK Sandbox.")
                return MockPlatformAdapter(platform_name="TIKTOK")

        else:
            logger.info(f"Unknown platform '{target}'. Using MockPlatformAdapter.")
            return MockPlatformAdapter(platform_name=target)

import uuid
import logging
from typing import Dict, Any
from app.core.adapters.base import BasePlatformAdapter

logger = logging.getLogger("aimos.adapters.mock")


class MockPlatformAdapter(BasePlatformAdapter):
    """
    Mock Platform Adapter for Sandbox execution and automated tests.
    Simulates campaign, adset, and ad creation on Meta/TikTok with zero API cost.
    """

    def __init__(self, platform_name: str = "META"):
        self.platform_name = platform_name.upper()

    def get_platform_name(self) -> str:
        return self.platform_name

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MOCK PLATFORM ADAPTER ({self.platform_name})] Creating campaign '{campaign_data.get('name')}'")
        ext_id = f"mock_{self.platform_name.lower()}_cmp_{uuid.uuid4().hex[:8]}"
        return {
            "external_campaign_id": ext_id,
            "status": "ACTIVE",
            "is_mock": True,
            "platform": self.platform_name,
            "message": f"Successfully published campaign to {self.platform_name} Sandbox.",
        }

    async def create_ad_set(self, adset_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MOCK PLATFORM ADAPTER ({self.platform_name})] Creating ad set '{adset_data.get('name')}'")
        ext_id = f"mock_{self.platform_name.lower()}_adset_{uuid.uuid4().hex[:8]}"
        return {
            "external_adset_id": ext_id,
            "status": "ACTIVE",
            "is_mock": True,
        }

    async def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MOCK PLATFORM ADAPTER ({self.platform_name})] Creating ad '{ad_data.get('name')}'")
        ext_id = f"mock_{self.platform_name.lower()}_ad_{uuid.uuid4().hex[:8]}"
        return {
            "external_ad_id": ext_id,
            "status": "ACTIVE",
            "is_mock": True,
        }

    async def sync_campaign_metrics(self, external_campaign_id: str) -> Dict[str, Any]:
        logger.info(f"[MOCK PLATFORM ADAPTER ({self.platform_name})] Syncing metrics for {external_campaign_id}")
        return {
            "external_campaign_id": external_campaign_id,
            "impressions": 12500,
            "clicks": 450,
            "ctr": 3.6,
            "spend_usd": 45.0,
            "conversions": 18,
            "cpa_usd": 2.5,
            "is_mock": True,
        }

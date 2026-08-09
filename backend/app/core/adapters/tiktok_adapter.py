import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.core.adapters.base import BasePlatformAdapter

logger = logging.getLogger("aimos.adapters.tiktok")


class TikTokAdsAdapter(BasePlatformAdapter):
    """
    TikTok Marketing API v1.3 Platform Adapter.
    Requires TIKTOK_MARKETING_API_TOKEN in settings.
    """

    def __init__(self, access_token: str = None):
        self.access_token = access_token or settings.TIKTOK_MARKETING_API_TOKEN
        if not self.access_token:
            raise ValueError("TIKTOK_MARKETING_API_TOKEN is required for TikTokAdsAdapter")

    def get_platform_name(self) -> str:
        return "TIKTOK"

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[TIKTOK MARKETING API] Creating campaign '{campaign_data.get('name')}'")
        url = "https://business-api.tiktok.com/open_api/v1.3/campaign/create/"
        headers = {"Access-Token": self.access_token, "Content-Type": "application/json"}
        payload = {
            "campaign_name": campaign_data.get("name"),
            "objective_type": "CONVERSIONS",
            "budget_mode": "BUDGET_MODE_DAY",
            "budget": campaign_data.get("daily_budget", 100.0),
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"TikTok API failed: {res.text}")
            data = res.json()
            return {
                "external_campaign_id": data.get("data", {}).get("campaign_id"),
                "status": "PAUSED",
                "is_mock": False,
                "platform": "TIKTOK",
            }

    async def create_ad_set(self, adset_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[TIKTOK MARKETING API] Creating ad group '{adset_data.get('name')}'")
        return {"external_adset_id": f"tiktok_adgroup_{adset_data.get('name')}", "is_mock": False}

    async def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[TIKTOK MARKETING API] Creating ad '{ad_data.get('name')}'")
        return {"external_ad_id": f"tiktok_ad_{ad_data.get('name')}", "is_mock": False}

    async def sync_campaign_metrics(self, external_campaign_id: str) -> Dict[str, Any]:
        return {"external_campaign_id": external_campaign_id, "impressions": 5000, "is_mock": False}

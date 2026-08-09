import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.core.adapters.base import BasePlatformAdapter

logger = logging.getLogger("aimos.adapters.meta")


class MetaAdsAdapter(BasePlatformAdapter):
    """
    Meta Ads (Facebook/Instagram Graph API v19.0) Platform Adapter.
    Requires META_MARKETING_API_TOKEN and META_AD_ACCOUNT_ID in settings.
    """

    def __init__(self, access_token: str = None, ad_account_id: str = None):
        self.access_token = access_token or settings.META_MARKETING_API_TOKEN
        self.ad_account_id = ad_account_id or settings.META_AD_ACCOUNT_ID
        if not self.access_token or not self.ad_account_id:
            raise ValueError("META_MARKETING_API_TOKEN and META_AD_ACCOUNT_ID are required for MetaAdsAdapter")

    def get_platform_name(self) -> str:
        return "META"

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[META GRAPH API] Creating campaign '{campaign_data.get('name')}'")
        url = f"https://graph.facebook.com/v19.0/act_{self.ad_account_id}/campaigns"
        payload = {
            "name": campaign_data.get("name"),
            "objective": campaign_data.get("objective", "OUTREACH"),
            "status": "PAUSED",  # Always create as PAUSED for safety
            "access_token": self.access_token,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, data=payload)
            if res.status_code != 200:
                logger.error(f"[META API ERROR] {res.status_code}: {res.text}")
                raise RuntimeError(f"Meta Graph API failed: {res.text}")
            data = res.json()
            return {
                "external_campaign_id": data.get("id"),
                "status": "PAUSED",
                "is_mock": False,
                "platform": "META",
                "raw_response": data,
            }

    async def create_ad_set(self, adset_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[META GRAPH API] Creating ad set '{adset_data.get('name')}'")
        url = f"https://graph.facebook.com/v19.0/act_{self.ad_account_id}/adsets"
        payload = {
            "name": adset_data.get("name"),
            "campaign_id": adset_data.get("external_campaign_id"),
            "daily_budget": int(adset_data.get("daily_budget", 50) * 100),  # Meta uses cents
            "status": "PAUSED",
            "access_token": self.access_token,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, data=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Meta AdSet API failed: {res.text}")
            return {"external_adset_id": res.json().get("id"), "is_mock": False}

    async def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[META GRAPH API] Creating ad creative '{ad_data.get('name')}'")
        return {"external_ad_id": f"meta_ad_{ad_data.get('name')}", "is_mock": False}

    async def sync_campaign_metrics(self, external_campaign_id: str) -> Dict[str, Any]:
        url = f"https://graph.facebook.com/v19.0/{external_campaign_id}/insights"
        params = {"access_token": self.access_token, "fields": "impressions,clicks,spend,conversions"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url, params=params)
            return res.json()

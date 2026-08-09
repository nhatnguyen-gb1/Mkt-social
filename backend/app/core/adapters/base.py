from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePlatformAdapter(ABC):
    """
    Abstract Base Class for Ad Platform Adapters (Meta Ads, TikTok Ads, Google Ads).
    Isolates external advertising APIs behind a unified interface.
    """

    @abstractmethod
    def get_platform_name(self) -> str:
        """Returns platform identifier name, e.g. 'META' or 'TIKTOK'."""
        pass

    @abstractmethod
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a campaign on the remote ad platform API.
        Returns dictionary with external_campaign_id, status, and raw response.
        """
        pass

    @abstractmethod
    async def create_ad_set(self, adset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an ad set/group on the remote ad platform API.
        Returns dictionary with external_adset_id.
        """
        pass

    @abstractmethod
    async def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an ad creative on the remote ad platform API.
        Returns dictionary with external_ad_id.
        """
        pass

    @abstractmethod
    async def sync_campaign_metrics(self, external_campaign_id: str) -> Dict[str, Any]:
        """
        Fetches performance metrics (impressions, clicks, spend, conversions) from the platform API.
        """
        pass

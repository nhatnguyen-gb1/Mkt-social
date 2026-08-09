import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.campaign import Campaign, AdSet, Ad
from app.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    """
    Repository for managing Campaign, AdSet, and Ad entity database operations with eager loading.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Campaign, session)

    async def get_by_id(self, id: uuid.UUID) -> Optional[Campaign]:
        stmt = (
            select(Campaign)
            .options(selectinload(Campaign.ad_sets).selectinload(AdSet.ads))
            .where(Campaign.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_product_id(
        self, product_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Campaign]:
        stmt = (
            select(Campaign)
            .options(selectinload(Campaign.ad_sets).selectinload(AdSet.ads))
            .where(Campaign.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .order_by(Campaign.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[Campaign]:
        stmt = (
            select(Campaign)
            .options(selectinload(Campaign.ad_sets).selectinload(AdSet.ads))
            .offset(skip)
            .limit(limit)
            .order_by(Campaign.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_campaign_with_structure(self, campaign_data: dict) -> Campaign:
        ad_sets_data = campaign_data.pop("ad_sets", [])
        
        campaign = Campaign(**campaign_data)
        self.session.add(campaign)
        await self.session.flush()

        for adset_in in ad_sets_data:
            ads_data = adset_in.pop("ads", [])
            ad_set = AdSet(campaign_id=campaign.id, **adset_in)
            self.session.add(ad_set)
            await self.session.flush()

            for ad_in in ads_data:
                ad = Ad(ad_set_id=ad_set.id, **ad_in)
                self.session.add(ad)

        await self.session.flush()
        return await self.get_by_id(campaign.id)

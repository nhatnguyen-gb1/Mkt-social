import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analytics import CampaignMetric
from app.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository[CampaignMetric]):
    """
    Repository for managing CampaignMetric entity database operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(CampaignMetric, session)

    async def get_metrics_by_campaign_id(
        self, campaign_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[CampaignMetric]:
        stmt = (
            select(CampaignMetric)
            .where(CampaignMetric.campaign_id == campaign_id)
            .offset(skip)
            .limit(limit)
            .order_by(CampaignMetric.recorded_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_metric_by_campaign_id(
        self, campaign_id: uuid.UUID
    ) -> Optional[CampaignMetric]:
        stmt = (
            select(CampaignMetric)
            .where(CampaignMetric.campaign_id == campaign_id)
            .order_by(CampaignMetric.recorded_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

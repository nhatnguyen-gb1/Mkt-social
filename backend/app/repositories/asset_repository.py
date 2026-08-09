import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """
    Repository for managing Asset entity database operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Asset, session)

    async def get_by_product_id(
        self, product_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .order_by(Asset.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type(
        self, asset_type: str, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.asset_type == asset_type)
            .offset(skip)
            .limit(limit)
            .order_by(Asset.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_multi_ordered(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        result = await self.session.execute(
            select(Product).offset(skip).limit(limit).order_by(Product.created_at.desc())
        )
        return list(result.scalars().all())

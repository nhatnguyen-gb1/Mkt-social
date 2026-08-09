from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    def __init__(self, session: AsyncSession):
        super().__init__(Job, session)

    async def get_multi_ordered(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        result = await self.session.execute(
            select(Job).offset(skip).limit(limit).order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

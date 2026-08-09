from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)

    async def get_multi_ordered(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        result = await self.session.execute(
            select(AuditLog).offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())

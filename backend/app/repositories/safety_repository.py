import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.safety import PolicyRule, ApprovalRequest
from app.repositories.base import BaseRepository


class SafetyRepository(BaseRepository[PolicyRule]):
    """
    Repository for managing PolicyRule and ApprovalRequest entities.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(PolicyRule, session)

    async def get_active_rules(self) -> List[PolicyRule]:
        stmt = (
            select(PolicyRule)
            .where(PolicyRule.is_active == True)
            .order_by(PolicyRule.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_approval_request(self, data: dict) -> ApprovalRequest:
        req = ApprovalRequest(**data)
        self.session.add(req)
        await self.session.flush()
        await self.session.refresh(req)
        return req

    async def get_approval_request_by_id(self, req_id: uuid.UUID) -> Optional[ApprovalRequest]:
        stmt = select(ApprovalRequest).where(ApprovalRequest.id == req_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_pending_approval_requests(
        self, skip: int = 0, limit: int = 100
    ) -> List[ApprovalRequest]:
        stmt = (
            select(ApprovalRequest)
            .where(ApprovalRequest.status == "PENDING")
            .offset(skip)
            .limit(limit)
            .order_by(ApprovalRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_approval_request(
        self, req: ApprovalRequest, data: dict
    ) -> ApprovalRequest:
        for k, v in data.items():
            if hasattr(req, k) and v is not None:
                setattr(req, k, v)
        await self.session.flush()
        await self.session.refresh(req)
        return req

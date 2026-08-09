import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_run import AgentRun, LLMUsage
from app.repositories.base import BaseRepository


class AgentRepository(BaseRepository[AgentRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(AgentRun, session)

    async def create_llm_usage(self, usage_data: dict) -> LLMUsage:
        usage = LLMUsage(**usage_data)
        self.session.add(usage)
        await self.session.flush()
        await self.session.refresh(usage)
        return usage

    async def get_usages_for_run(self, agent_run_id: uuid.UUID) -> List[LLMUsage]:
        result = await self.session.execute(
            select(LLMUsage).where(LLMUsage.agent_run_id == agent_run_id)
        )
        return list(result.scalars().all())

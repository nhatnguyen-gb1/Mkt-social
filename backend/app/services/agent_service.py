import time
import uuid
from typing import Optional, Any
from fastapi import HTTPException, status
from app.core.llm.factory import LLMProviderFactory
from app.repositories.agent_repository import AgentRepository
from app.services.audit_service import AuditService
from app.agents.market_research_agent import MarketResearchAgent
from app.agents.marketing_strategy_agent import MarketingStrategyAgent
from app.agents.creative_agent import CreativeAgent
from app.agents.ads_agent import AdsAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.tools.product_tool import ProductLookupTool
from app.agents.tools.image_tool import ImageGenerationTool
from app.schemas.agent import AgentResearchRequest, AgentRunResponse
from app.schemas.creative import StrategyRequest, CreativeRequest
from app.schemas.campaign import AdsAgentRequest
from app.schemas.analytics import OptimizationAgentRequest
from app.models.base import utc_now


class AgentService:
    def __init__(
        self, agent_repo: AgentRepository, audit_service: AuditService
    ):
        self.agent_repo = agent_repo
        self.audit_service = audit_service

    async def _execute_agent_flow(
        self,
        agent_name: str,
        agent_instance_class: Any,
        input_payload: dict,
        provider_name: str,
        tools: list = None,
        actor_id: Optional[str] = None,
    ) -> AgentRunResponse:
        start_time = time.time()

        agent_run = await self.agent_repo.create(
            {
                "agent_name": agent_name,
                "status": "RUNNING",
                "input_data": input_payload,
            }
        )

        await self.audit_service.log_action(
            action="AGENT_STARTED",
            entity_type="AgentRun",
            entity_id=agent_run.id,
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            input_data=input_payload,
        )

        try:
            provider = LLMProviderFactory.get_provider(provider_name)
            agent = agent_instance_class(llm_provider=provider, tools=tools or [])
            state = await agent.run(input_payload)
            elapsed_ms = int((time.time() - start_time) * 1000)

            usage_rec = provider.get_last_usage()
            await self.agent_repo.create_llm_usage(
                {
                    "agent_run_id": agent_run.id,
                    "provider": usage_rec.provider,
                    "model_name": usage_rec.model_name,
                    "prompt_tokens": usage_rec.prompt_tokens,
                    "completion_tokens": usage_rec.completion_tokens,
                    "total_tokens": usage_rec.total_tokens,
                    "estimated_cost_usd": usage_rec.estimated_cost_usd,
                }
            )

            if state.status == "COMPLETED":
                updated_run = await self.agent_repo.update(
                    agent_run,
                    {
                        "status": "COMPLETED",
                        "output_data": state.final_result,
                        "execution_time_ms": elapsed_ms,
                        "completed_at": utc_now(),
                    },
                )
                await self.audit_service.log_action(
                    action="AGENT_COMPLETED",
                    entity_type="AgentRun",
                    entity_id=agent_run.id,
                    actor_type="USER" if actor_id else "SYSTEM",
                    actor_id=actor_id,
                    output_data=state.final_result,
                )
                return AgentRunResponse(
                    run_id=updated_run.id,
                    agent_name=updated_run.agent_name,
                    status=updated_run.status,
                    provider_used=provider.get_provider_name(),
                    input_data=updated_run.input_data,
                    result=updated_run.output_data,
                    execution_time_ms=updated_run.execution_time_ms,
                    created_at=updated_run.created_at,
                )
            else:
                updated_run = await self.agent_repo.update(
                    agent_run,
                    {
                        "status": "FAILED",
                        "error_message": state.error or "Unknown agent execution error",
                        "execution_time_ms": elapsed_ms,
                        "completed_at": utc_now(),
                    },
                )
                await self.audit_service.log_action(
                    action="AGENT_FAILED",
                    entity_type="AgentRun",
                    entity_id=agent_run.id,
                    actor_type="USER" if actor_id else "SYSTEM",
                    actor_id=actor_id,
                    status="FAILURE",
                    output_data={"error": state.error},
                )
                return AgentRunResponse(
                    run_id=updated_run.id,
                    agent_name=updated_run.agent_name,
                    status=updated_run.status,
                    provider_used=provider.get_provider_name(),
                    input_data=updated_run.input_data,
                    error_message=updated_run.error_message,
                    execution_time_ms=updated_run.execution_time_ms,
                    created_at=updated_run.created_at,
                )
        except Exception as ex:
            elapsed_ms = int((time.time() - start_time) * 1000)
            await self.agent_repo.update(
                agent_run,
                {
                    "status": "FAILED",
                    "error_message": str(ex),
                    "execution_time_ms": elapsed_ms,
                    "completed_at": utc_now(),
                },
            )
            await self.audit_service.log_action(
                action="AGENT_FAILED",
                entity_type="AgentRun",
                entity_id=agent_run.id,
                status="FAILURE",
                output_data={"error": str(ex)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent execution error: {str(ex)}",
            )

    async def run_market_research(
        self, request: AgentResearchRequest, actor_id: Optional[str] = None
    ) -> AgentRunResponse:
        tools = [ProductLookupTool(self.agent_repo.session)]
        return await self._execute_agent_flow(
            agent_name="MarketResearchAgent",
            agent_instance_class=MarketResearchAgent,
            input_payload=request.model_dump(),
            provider_name=request.provider,
            tools=tools,
            actor_id=actor_id,
        )

    async def run_marketing_strategy(
        self, request: StrategyRequest, actor_id: Optional[str] = None
    ) -> AgentRunResponse:
        tools = [ProductLookupTool(self.agent_repo.session)]
        return await self._execute_agent_flow(
            agent_name="MarketingStrategyAgent",
            agent_instance_class=MarketingStrategyAgent,
            input_payload=request.model_dump(),
            provider_name=request.provider,
            tools=tools,
            actor_id=actor_id,
        )

    async def run_creative_generation(
        self, request: CreativeRequest, actor_id: Optional[str] = None
    ) -> AgentRunResponse:
        tools = [
            ProductLookupTool(self.agent_repo.session),
            ImageGenerationTool(provider_name=request.provider or "mock"),
        ]
        return await self._execute_agent_flow(
            agent_name="CreativeAgent",
            agent_instance_class=CreativeAgent,
            input_payload=request.model_dump(),
            provider_name=request.provider,
            tools=tools,
            actor_id=actor_id,
        )

    async def run_ads_agent(
        self, request: AdsAgentRequest, actor_id: Optional[str] = None
    ) -> AgentRunResponse:
        tools = [ProductLookupTool(self.agent_repo.session)]
        return await self._execute_agent_flow(
            agent_name="AdsAgent",
            agent_instance_class=AdsAgent,
            input_payload=request.model_dump(),
            provider_name=request.provider,
            tools=tools,
            actor_id=actor_id,
        )

    async def run_optimization_agent(
        self, request: OptimizationAgentRequest, actor_id: Optional[str] = None
    ) -> AgentRunResponse:
        tools = [ProductLookupTool(self.agent_repo.session)]
        payload = request.model_dump(mode="json")
        return await self._execute_agent_flow(
            agent_name="OptimizationAgent",
            agent_instance_class=OptimizationAgent,
            input_payload=payload,
            provider_name=request.provider,
            tools=tools,
            actor_id=actor_id,
        )

    async def get_agent_run(self, run_id: uuid.UUID) -> AgentRunResponse:
        agent_run = await self.agent_repo.get_by_id(run_id)
        if not agent_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AgentRun with id '{run_id}' not found",
            )
        return AgentRunResponse(
            run_id=agent_run.id,
            agent_name=agent_run.agent_name,
            status=agent_run.status,
            provider_used="unknown",
            input_data=agent_run.input_data or {},
            result=agent_run.output_data,
            error_message=agent_run.error_message,
            execution_time_ms=agent_run.execution_time_ms,
            created_at=agent_run.created_at,
        )

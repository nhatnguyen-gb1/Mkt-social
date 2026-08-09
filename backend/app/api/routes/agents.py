import uuid
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_agent_service
from app.services.agent_service import AgentService
from app.schemas.agent import AgentResearchRequest, AgentRunResponse
from app.schemas.creative import StrategyRequest, CreativeRequest
from app.schemas.campaign import AdsAgentRequest
from app.schemas.analytics import OptimizationAgentRequest

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.post(
    "/research",
    response_model=AgentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Market Research AI Agent",
)
async def run_market_research_api(
    request: AgentResearchRequest,
    service: AgentService = Depends(get_agent_service),
):
    """
    Triggers the MarketResearchAgent to analyze product opportunities and competitor risks.
    """
    return await service.run_market_research(request)


@router.post(
    "/strategy",
    response_model=AgentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Marketing Strategy AI Agent",
)
async def run_marketing_strategy_api(
    request: StrategyRequest,
    service: AgentService = Depends(get_agent_service),
):
    """
    Triggers the MarketingStrategyAgent to formulate brand positioning, ad angles, and copy.
    """
    return await service.run_marketing_strategy(request)


@router.post(
    "/creative",
    response_model=AgentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Creative Generation AI Agent",
)
async def run_creative_generation_api(
    request: CreativeRequest,
    service: AgentService = Depends(get_agent_service),
):
    """
    Triggers the CreativeAgent to generate visual prompts and video scripts.
    """
    return await service.run_creative_generation(request)


@router.post(
    "/ads",
    response_model=AgentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Ads AI Agent",
)
async def run_ads_agent_api(
    request: AdsAgentRequest,
    service: AgentService = Depends(get_agent_service),
):
    """
    Triggers the AdsAgent to structure campaign budget allocations, targeting criteria, and ad copy parameters.
    """
    return await service.run_ads_agent(request)


@router.post(
    "/optimization",
    response_model=AgentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Optimization AI Agent",
)
async def run_optimization_agent_api(
    request: OptimizationAgentRequest,
    service: AgentService = Depends(get_agent_service),
):
    """
    Triggers the OptimizationAgent to analyze campaign performance metrics and suggest scaling/pausing actions.
    """
    return await service.run_optimization_agent(request)


@router.get(
    "/runs/{run_id}",
    response_model=AgentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Agent Run Status & Result",
)
async def get_agent_run(
    run_id: uuid.UUID,
    service: AgentService = Depends(get_agent_service),
):
    """
    Retrieves the status, execution time, and output payload of an Agent execution run.
    """
    return await service.get_agent_run(run_id)

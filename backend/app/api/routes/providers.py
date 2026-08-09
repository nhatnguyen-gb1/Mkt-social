from fastapi import APIRouter, status
from app.core.providers.registries import MasterProviderRegistry
from app.core.tools.registry import ToolRegistry
from app.agents.registry import AgentRegistry

router = APIRouter(prefix="/system", tags=["System Registries & Architecture"])


@router.get(
    "/providers",
    status_code=status.HTTP_200_OK,
    summary="List Registered Vendor Providers Across All Domains",
)
async def list_providers():
    """
    Retrieves all master provider abstractions (LLM, Media, Voice, Search, Ad Platforms, E-commerce, Automation).
    """
    return MasterProviderRegistry.get_supported_providers()


@router.get(
    "/tools",
    status_code=status.HTTP_200_OK,
    summary="List Registered Tools in ToolRegistry",
)
async def list_tools():
    """
    Retrieves all registered tools grouped by category.
    """
    return ToolRegistry.list_all_tools()


@router.get(
    "/agents",
    status_code=status.HTTP_200_OK,
    summary="List Registered Agents in AgentRegistry",
)
async def list_agents():
    """
    Retrieves all registered AI Agents in AIMOS with their domain and status.
    """
    return AgentRegistry.list_all_agents()

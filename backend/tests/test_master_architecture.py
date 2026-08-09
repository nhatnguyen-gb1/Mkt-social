import pytest
from httpx import AsyncClient
from app.core.tools.registry import ToolRegistry
from app.core.providers.registries import MasterProviderRegistry
from app.agents.registry import AgentRegistry


@pytest.mark.asyncio
async def test_tool_registry_registration():
    all_tools = ToolRegistry.list_all_tools()
    assert "image_generation_tool" in all_tools
    assert "competitor_analysis_tool" in all_tools
    assert "ad_performance_tool" in all_tools
    assert "ecommerce_catalog_tool" in all_tools

    research_tools = ToolRegistry.get_tools_for_category("RESEARCH")
    assert len(research_tools) >= 1


@pytest.mark.asyncio
async def test_master_provider_registry():
    providers = MasterProviderRegistry.get_supported_providers()
    assert "LLM" in providers
    assert "MEDIA" in providers
    assert "AD_PLATFORMS" in providers

    resolved_llm = MasterProviderRegistry.resolve_provider("LLM", "mock")
    assert resolved_llm.get_provider_name() == "mock"


@pytest.mark.asyncio
async def test_agent_registry():
    agents = AgentRegistry.list_all_agents()
    assert len(agents) >= 7
    agent_names = [a["agent_name"] for a in agents]
    assert "MarketResearchAgent" in agent_names
    assert "AutomationAgent" in agent_names
    assert "EcommerceAgent" in agent_names


@pytest.mark.asyncio
async def test_system_registries_api_endpoints(client: AsyncClient):
    providers_res = await client.get("/api/v1/system/providers")
    assert providers_res.status_code == 200
    assert "LLM" in providers_res.json()

    tools_res = await client.get("/api/v1/system/tools")
    assert tools_res.status_code == 200

    agents_res = await client.get("/api/v1/system/agents")
    assert agents_res.status_code == 200
    assert len(agents_res.json()) >= 7


@pytest.mark.asyncio
async def test_ecommerce_skeleton_api_endpoint(client: AsyncClient):
    res = await client.get("/api/v1/ecommerce/products")
    assert res.status_code == 200
    assert res.json()["status"] == "SKELETON"
    assert len(res.json()["items"]) >= 1


@pytest.mark.asyncio
async def test_e2e_master_workflow_pipeline(client: AsyncClient):
    payload = {
        "product_name": "Bánh Trung Thu Thượng Hạng",
        "target_market": "Vietnam",
        "platform": "META",
        "daily_budget_usd": 150.0,
        "provider": "mock",
        "auto_publish": True,
    }
    res = await client.post("/api/v1/workflows/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["product_name"] == "Bánh Trung Thu Thượng Hạng"
    assert len(data["steps_executed"]) == 6
    assert data["status"] in ["PENDING_APPROVAL", "ACTIVE"]
    assert data["final_campaign_id"] is not None

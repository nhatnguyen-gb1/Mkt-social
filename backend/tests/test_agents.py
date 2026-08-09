import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.llm import MockLLMProvider
from app.agents import (
    AgentState,
    ProductLookupTool,
    MarketResearchAgent,
)
from app.repositories.product_repository import ProductRepository
from app.repositories.agent_repository import AgentRepository


@pytest.mark.asyncio
async def test_product_lookup_tool(db_session: AsyncSession):
    # Insert dummy product
    product_repo = ProductRepository(db_session)
    product = await product_repo.create({"name": "Ultima Running Shoes", "category": "Footwear"})
    await db_session.commit()

    tool = ProductLookupTool(db_session)
    res = await tool.execute(product_name="Ultima")
    assert res["found"] is True
    assert res["name"] == "Ultima Running Shoes"


@pytest.mark.asyncio
async def test_market_research_agent_direct_run(db_session: AsyncSession):
    tool = ProductLookupTool(db_session)
    provider = MockLLMProvider()
    agent = MarketResearchAgent(llm_provider=provider, tools=[tool])

    input_data = {"product_name": "Mooncake", "target_market": "Vietnam"}
    state = await agent.run(input_data)

    assert state.status == "COMPLETED"
    assert state.final_result is not None
    assert state.final_result["product_name"] == "Mooncake"
    assert state.final_result["target_market"] == "Vietnam"


@pytest.mark.asyncio
async def test_agent_research_api_endpoint(client: AsyncClient):
    payload = {
        "product_name": "Matcha Tea Powder",
        "target_market": "Japan",
        "provider": "mock",
    }
    response = await client.post("/api/v1/agents/research", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["provider_used"] == "mock"
    assert data["result"]["product_name"] == "Matcha Tea Powder"
    assert data["result"]["target_market"] == "Japan"
    assert "summary" in data["result"]

    run_id = data["run_id"]
    get_res = await client.get(f"/api/v1/agents/runs/{run_id}")
    assert get_res.status_code == 200
    assert get_res.json()["run_id"] == run_id

    # Verify Audit log recorded
    audit_res = await client.get("/api/v1/audit-logs")
    assert audit_res.status_code == 200
    actions = [item["action"] for item in audit_res.json()["items"]]
    assert "AGENT_STARTED" in actions
    assert "AGENT_COMPLETED" in actions

import pytest
import uuid
from httpx import AsyncClient
from app.core.llm.mock_provider import MockLLMProvider
from app.agents.optimization_agent import OptimizationAgent


@pytest.mark.asyncio
async def test_optimization_agent_direct_execution():
    llm = MockLLMProvider()
    agent = OptimizationAgent(llm_provider=llm)
    state = await agent.run(
        {
            "campaign_id": str(uuid.uuid4()),
            "target_cpa_usd": 5.0,
            "min_ctr_percent": 2.0,
            "metrics_summary": {"impressions": 12500, "clicks": 450, "spend": 45.0, "conversions": 18},
        }
    )
    assert state.status == "COMPLETED"
    assert "overall_health" in state.final_result
    assert len(state.final_result["recommendations"]) >= 1


@pytest.mark.asyncio
async def test_optimization_agent_api_endpoint(client: AsyncClient):
    payload = {
        "campaign_id": str(uuid.uuid4()),
        "target_cpa_usd": 5.0,
        "min_ctr_percent": 2.0,
        "provider": "mock",
    }
    response = await client.post("/api/v1/agents/optimization", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["agent_name"] == "OptimizationAgent"
    assert "recommendations" in data["result"]


@pytest.mark.asyncio
async def test_analytics_metrics_sync_and_summary(client: AsyncClient):
    # 1. Create Campaign
    cmp_payload = {
        "name": "Chiến dịch Đo Lường Analytics Test",
        "platform": "META",
        "objective": "CONVERSIONS",
        "daily_budget": 100.0,
    }
    create_res = await client.post("/api/v1/campaigns", json=cmp_payload)
    assert create_res.status_code == 201
    campaign_id = create_res.json()["id"]

    # 2. Sync Campaign Metrics from Platform API/Sandbox
    sync_res = await client.post(f"/api/v1/analytics/sync/{campaign_id}")
    assert sync_res.status_code == 200
    metric_data = sync_res.json()
    assert metric_data["campaign_id"] == campaign_id
    assert metric_data["impressions"] > 0
    assert metric_data["ctr"] > 0

    # 3. Get Campaign Analytics Summary
    summary_res = await client.get(f"/api/v1/analytics/campaigns/{campaign_id}")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["campaign_id"] == campaign_id
    assert summary_data["total_impressions"] > 0
    assert len(summary_data["metrics_history"]) >= 1

import pytest
import uuid
from httpx import AsyncClient
from app.core.adapters.factory import PlatformAdapterFactory
from app.core.adapters.mock_adapter import MockPlatformAdapter
from app.core.llm.mock_provider import MockLLMProvider
from app.agents.ads_agent import AdsAgent


@pytest.mark.asyncio
async def test_platform_adapter_factory():
    meta_adapter = PlatformAdapterFactory.get_adapter("META")
    assert isinstance(meta_adapter, MockPlatformAdapter)
    assert meta_adapter.get_platform_name() == "META"

    tiktok_adapter = PlatformAdapterFactory.get_adapter("TIKTOK")
    assert isinstance(tiktok_adapter, MockPlatformAdapter)
    assert tiktok_adapter.get_platform_name() == "TIKTOK"

    res = await meta_adapter.create_campaign({"name": "Test Meta Campaign"})
    assert "external_campaign_id" in res
    assert res["is_mock"] is True


@pytest.mark.asyncio
async def test_ads_agent_execution():
    llm = MockLLMProvider()
    agent = AdsAgent(llm_provider=llm)
    state = await agent.run({"product_name": "Bánh Trung Thu", "target_platform": "META", "total_budget_usd": 150.0})
    assert state.status == "COMPLETED"
    assert "recommended_campaign_name" in state.final_result
    assert state.final_result["objective"] == "CONVERSIONS"


@pytest.mark.asyncio
async def test_ads_agent_api_endpoint(client: AsyncClient):
    payload = {
        "product_name": "Bánh Trung Thu",
        "target_platform": "META",
        "total_budget_usd": 250.0,
        "provider": "mock",
    }
    response = await client.post("/api/v1/agents/ads", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["agent_name"] == "AdsAgent"
    assert "targeting_recommendations" in data["result"]


@pytest.mark.asyncio
async def test_campaign_create_publish_and_retrieve(client: AsyncClient):
    # 1. Create Campaign
    cmp_payload = {
        "name": "Chiến dịch Bánh Trung Thu - Test",
        "platform": "META",
        "objective": "CONVERSIONS",
        "daily_budget": 100.0,
        "ad_sets": [
            {
                "name": "Nhóm Ads 1 - Khách Hàng Cá Nhân",
                "daily_budget": 50.0,
                "targeting": {"age_range": "22-40", "locations": ["Vietnam"]},
                "ads": [
                    {
                        "name": "Ad Copy 1 - Quà Tặng",
                        "headline": "Món Quà Thành Ý",
                        "primary_text": "Chiêm ngưỡng bộ sưu tập bánh thượng hạng.",
                        "call_to_action": "SHOP_NOW",
                    }
                ],
            }
        ],
    }
    create_res = await client.post("/api/v1/campaigns", json=cmp_payload)
    assert create_res.status_code == 201
    cmp_data = create_res.json()
    assert cmp_data["name"] == "Chiến dịch Bánh Trung Thu - Test"
    assert cmp_data["status"] == "DRAFT"
    assert len(cmp_data["ad_sets"]) == 1
    cmp_id = cmp_data["id"]

    # 2. Publish Campaign -> Policy Engine routes to PENDING_APPROVAL
    pub_res = await client.post(f"/api/v1/campaigns/{cmp_id}/publish")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["status"] == "PENDING_APPROVAL"

    # 3. Approve via Human Approval Gate
    app_list_res = await client.get("/api/v1/approvals")
    req_id = app_list_res.json()["items"][0]["id"]
    await client.post(f"/api/v1/approvals/{req_id}/approve", json={"reviewer_id": "test_marketer"})

    # 4. Get Campaign by ID -> Status is now ACTIVE
    get_res = await client.get(f"/api/v1/campaigns/{cmp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "ACTIVE"

    # 5. List Campaigns
    list_res = await client.get("/api/v1/campaigns")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

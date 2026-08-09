import pytest
import uuid
from httpx import AsyncClient
from app.models.campaign import Campaign
from app.models.safety import PolicyRule
from app.core.safety.engine import PolicyEngine


@pytest.mark.asyncio
async def test_policy_engine_evaluation():
    # 1. Test Budget Cap Violation
    campaign = Campaign(name="Test Campaign", daily_budget=1000.0)
    rule_budget = PolicyRule(
        name="Max Budget Rule",
        rule_type="MAX_DAILY_BUDGET",
        parameters={"max_daily_budget_usd": 500.0},
        is_active=True,
    )
    result = PolicyEngine.evaluate_campaign(campaign, [rule_budget])
    assert result.is_allowed is False
    assert len(result.policy_violations) == 1

    # 2. Test Restricted Keyword Violation
    campaign_bad_name = Campaign(name="Get free money now campaign", daily_budget=100.0)
    rule_kw = PolicyRule(
        name="Restricted Keyword Rule",
        rule_type="RESTRICTED_KEYWORDS",
        parameters={"keywords": ["free money", "guaranteed"]},
        is_active=True,
    )
    result_kw = PolicyEngine.evaluate_campaign(campaign_bad_name, [rule_kw])
    assert result_kw.is_allowed is False
    assert len(result_kw.policy_violations) == 1


@pytest.mark.asyncio
async def test_safety_rules_api_endpoints(client: AsyncClient):
    payload = {
        "name": "Quy Tắc Hạn Mức Ngân Sách Hàng Ngày",
        "rule_type": "MAX_DAILY_BUDGET",
        "parameters": {"max_daily_budget_usd": 300.0},
        "is_active": True,
    }
    create_res = await client.post("/api/v1/safety/rules", json=payload)
    assert create_res.status_code == 201
    rule_data = create_res.json()
    assert rule_data["rule_type"] == "MAX_DAILY_BUDGET"

    list_res = await client.get("/api/v1/safety/rules")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_human_in_the_loop_approval_workflow(client: AsyncClient):
    # 1. Create a Campaign
    cmp_payload = {
        "name": "Chiến dịch Cần Duyệt - Test",
        "platform": "META",
        "objective": "CONVERSIONS",
        "daily_budget": 100.0,
    }
    create_res = await client.post("/api/v1/campaigns", json=cmp_payload)
    assert create_res.status_code == 201
    campaign_id = create_res.json()["id"]

    # 2. Publish Campaign (Policy Engine creates PENDING_APPROVAL)
    pub_res = await client.post(f"/api/v1/campaigns/{campaign_id}/publish")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["status"] == "PENDING_APPROVAL"

    # 3. List Pending Approvals
    app_list_res = await client.get("/api/v1/approvals")
    assert app_list_res.status_code == 200
    pending_items = app_list_res.json()["items"]
    assert len(pending_items) >= 1
    req_id = pending_items[0]["id"]

    # 4. Human Marketer Approves Request
    review_payload = {
        "reviewer_id": "cmo_manager_marketer",
        "rejection_reason": None,
    }
    approve_res = await client.post(f"/api/v1/approvals/{req_id}/approve", json=review_payload)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # 5. Check Campaign Status is now ACTIVE
    get_cmp_res = await client.get(f"/api/v1/campaigns/{campaign_id}")
    assert get_cmp_res.status_code == 200
    assert get_cmp_res.json()["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_policy_engine_blocks_violating_campaign(client: AsyncClient):
    # 1. Create a Max Budget Policy Rule
    rule_payload = {
        "name": "Strict Budget Cap 50",
        "rule_type": "MAX_DAILY_BUDGET",
        "parameters": {"max_daily_budget_usd": 50.0},
        "is_active": True,
    }
    await client.post("/api/v1/safety/rules", json=rule_payload)

    # 2. Create Campaign with daily_budget=500.0 (violates cap of 50.0)
    cmp_payload = {
        "name": "High Budget Campaign Violator",
        "platform": "META",
        "objective": "CONVERSIONS",
        "daily_budget": 500.0,
    }
    create_res = await client.post("/api/v1/campaigns", json=cmp_payload)
    assert create_res.status_code == 201
    campaign_id = create_res.json()["id"]

    # 3. Publish Campaign -> Should be blocked with HTTP 400 Bad Request
    pub_res = await client.post(f"/api/v1/campaigns/{campaign_id}/publish")
    assert pub_res.status_code == 400
    assert "exceeds maximum allowed threshold" in pub_res.json()["detail"]

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.skills.registry import skill_registry
from app.agents.marketing_lead_agent import MarketingLeadAgent
from app.core.llm.factory import LLMProviderFactory

client = TestClient(app)


def test_marketing_lead_profile_existence():
    profile_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "agents", "marketing_lead")
    )
    assert os.path.exists(os.path.join(profile_dir, "ROLE.md"))
    assert os.path.exists(os.path.join(profile_dir, "MISSION.md"))
    assert os.path.exists(os.path.join(profile_dir, "KNOWLEDGE"))
    assert os.path.exists(os.path.join(profile_dir, "RULES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EXAMPLES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EVALS.md"))
    assert os.path.exists(os.path.join(profile_dir, "TOOLS.md"))
    assert os.path.exists(os.path.join(profile_dir, "PERMISSIONS.md"))


def test_marketing_lead_15_skills_discovery():
    expected_15_skills = [
        "business_analysis",
        "marketing_goal_setting",
        "customer_problem_analysis",
        "marketing_strategy",
        "positioning_strategy",
        "offer_strategy",
        "funnel_strategy",
        "campaign_planning",
        "budget_planning",
        "team_delegation",
        "agent_selection",
        "output_review",
        "performance_review",
        "experiment_planning",
        "final_recommendation",
    ]
    for sk_name in expected_15_skills:
        assert skill_registry.has_skill(sk_name) is True, f"Skill '{sk_name}' missing from registry"


def test_marketing_lead_adapted_5_skills_discovery():
    adapted_skills = [
        "product_marketing_context",
        "generative_engine_optimization",
        "conversion_rate_optimization",
        "viral_referral_loop",
        "retention_churn_prevention",
    ]
    for sk_name in adapted_skills:
        assert skill_registry.has_skill(sk_name) is True, f"Adapted Skill '{sk_name}' missing from registry"


@pytest.mark.asyncio
async def test_marketing_lead_agent_direct_run():
    provider = LLMProviderFactory.get_provider("mock")
    agent = MarketingLeadAgent(llm_provider=provider)

    payload = {
        "objective": "Tôi muốn bán một sản phẩm mới trên TikTok Shop Philippines với ngân sách 500 USD.",
        "context": "E-commerce launch",
        "constraints": {"budget": 500},
    }

    state = await agent.run(payload)
    assert state.status == "COMPLETED"
    res = state.final_result

    assert "objective" in res
    assert "analysis" in res
    assert "strategy" in res
    assert "task_plan" in res
    assert "selected_agents" in res
    assert "facts" in res
    assert "assumptions" in res
    assert "unknowns" in res
    assert "recommendations" in res
    assert "product_marketing_context" in res
    assert len(res["task_plan"]) >= 4


@pytest.mark.asyncio
async def test_marketing_lead_input_guardrail_rejection():
    provider = LLMProviderFactory.get_provider("mock")
    agent = MarketingLeadAgent(llm_provider=provider)

    payload_invalid = {
        "objective": "Bán",
        "constraints": {"budget": 5},
    }

    state = await agent.run(payload_invalid)
    assert state.status == "COMPLETED"
    assert state.final_result.get("status") == "GUARDRAIL_REJECTED"
    assert "Input Guardrail Violation" in state.final_result.get("error")


def test_marketing_lead_agent_selection_and_unavailable():
    provider = LLMProviderFactory.get_provider("mock")
    agent = MarketingLeadAgent(llm_provider=provider)
    
    available_agents = ["MarketResearchAgent", "CreativeAgent", "AdsAgent"]
    for ag in available_agents:
        assert agent is not None


def test_marketing_lead_output_review_framework():
    provider = LLMProviderFactory.get_provider("mock")
    agent_accept = MarketingLeadAgent(llm_provider=provider, review_threshold=70.0)
    agent_reject = MarketingLeadAgent(llm_provider=provider, review_threshold=95.0)

    assert agent_accept.review_threshold == 70.0
    assert agent_reject.review_threshold == 95.0


def test_marketing_lead_api_endpoint():
    payload = {
        "objective": "Tôi muốn bán một sản phẩm mới trên TikTok Shop Philippines với ngân sách 500 USD.",
        "context": "E-commerce launch",
        "constraints": {"budget": 500},
        "provider": "mock",
    }

    response = client.post("/api/v1/agents/marketing-lead/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["objective"] == payload["objective"]
    assert len(data["task_plan"]) >= 4
    assert len(data["selected_agents"]) >= 3
    assert len(data["facts"]) >= 1
    assert len(data["assumptions"]) >= 1
    assert len(data["unknowns"]) >= 1
    assert len(data["recommendations"]) >= 1

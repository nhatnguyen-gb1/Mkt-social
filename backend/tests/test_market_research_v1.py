import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.skills.registry import skill_registry
from app.agents.market_research_agent import MarketResearchAgent
from app.core.llm.factory import LLMProviderFactory

client = TestClient(app)


def test_market_research_profile_existence():
    profile_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "agents", "market_research")
    )
    assert os.path.exists(os.path.join(profile_dir, "ROLE.md"))
    assert os.path.exists(os.path.join(profile_dir, "MISSION.md"))
    assert os.path.exists(os.path.join(profile_dir, "KNOWLEDGE"))
    assert os.path.exists(os.path.join(profile_dir, "RULES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EXAMPLES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EVALS.md"))
    assert os.path.exists(os.path.join(profile_dir, "TOOLS.md"))
    assert os.path.exists(os.path.join(profile_dir, "PERMISSIONS.md"))


def test_market_research_17_skills_discovery():
    expected_17_skills = [
        "market_overview",
        "market_segmentation",
        "customer_analysis",
        "customer_pain_point_analysis",
        "demand_analysis",
        "trend_analysis",
        "competitor_analysis",
        "competitor_positioning",
        "product_market_analysis",
        "pricing_analysis",
        "market_saturation_analysis",
        "opportunity_analysis",
        "risk_analysis",
        "market_comparison",
        "research_synthesis",
        "evidence_evaluation",
        "research_report_generation",
    ]
    for sk_name in expected_17_skills:
        assert skill_registry.has_skill(sk_name) is True, f"Skill '{sk_name}' missing from registry"


@pytest.mark.asyncio
async def test_market_research_agent_mock_test():
    provider = LLMProviderFactory.get_provider("mock")
    agent = MarketResearchAgent(llm_provider=provider)

    payload = {
        "research_question": "Đánh giá cơ hội bán một sản phẩm mới trên TikTok Shop Philippines.",
        "market": "Philippines",
        "product": "Máy pha cà phê mini",
    }

    state = await agent.run(payload)
    assert state.status == "COMPLETED"
    report = state.final_result

    # Schema contract verification
    assert report["research_question"] == payload["research_question"]
    assert report["market"] == payload["market"]
    assert "objective" in report
    assert "target_customer" in report
    assert "market_overview" in report
    assert "demand_analysis" in report
    assert "trend_analysis" in report
    assert "competitor_analysis" in report
    assert "customer_analysis" in report
    assert "pricing_analysis" in report
    assert "opportunity_analysis" in report
    assert "risk_analysis" in report
    assert isinstance(report["evidence"], list)
    assert isinstance(report["assumptions"], list)
    assert isinstance(report["unknowns"], list)
    assert "recommendation" in report
    assert isinstance(report["confidence"], (int, float))
    assert len(report["evidence"]) >= 1
    assert len(report["assumptions"]) >= 1
    assert len(report["unknowns"]) >= 1


def test_market_research_api_endpoint():
    payload = {
        "research_question": "Đánh giá cơ hội bán một sản phẩm mới trên TikTok Shop Philippines.",
        "market": "Philippines",
        "product": "Máy pha cà phê mini",
        "provider": "mock",
    }

    response = client.post("/api/v1/agents/market-research/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["research_question"] == payload["research_question"]
    assert data["market"] == payload["market"]
    assert "opportunity_analysis" in data
    assert "recommendation" in data
    assert data["confidence"] >= 70

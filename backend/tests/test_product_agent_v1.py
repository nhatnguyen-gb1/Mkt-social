import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.skills.registry import skill_registry
from app.agents.product_agent import ProductAgent
from app.core.llm.factory import LLMProviderFactory

client = TestClient(app)


def test_product_profile_existence():
    profile_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "agents", "product")
    )
    assert os.path.exists(os.path.join(profile_dir, "ROLE.md"))
    assert os.path.exists(os.path.join(profile_dir, "MISSION.md"))
    assert os.path.exists(os.path.join(profile_dir, "KNOWLEDGE"))
    assert os.path.exists(os.path.join(profile_dir, "RULES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EXAMPLES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EVALS.md"))
    assert os.path.exists(os.path.join(profile_dir, "TOOLS.md"))
    assert os.path.exists(os.path.join(profile_dir, "PERMISSIONS.md"))


def test_product_17_skills_discovery():
    expected_17_skills = [
        "product_analysis",
        "customer_problem_analysis",
        "customer_persona",
        "jobs_to_be_done",
        "value_proposition",
        "usp_generation",
        "positioning_strategy",
        "differentiation_analysis",
        "product_market_fit_analysis",
        "product_validation",
        "offer_strategy",
        "pricing_strategy",
        "product_competitive_analysis",
        "product_risk_analysis",
        "product_launch_strategy",
        "product_comparison",
        "product_recommendation",
    ]
    for sk_name in expected_17_skills:
        assert skill_registry.has_skill(sk_name) is True, f"Skill '{sk_name}' missing from registry"


@pytest.mark.asyncio
async def test_product_agent_mock_test():
    provider = LLMProviderFactory.get_provider("mock")
    agent = ProductAgent(llm_provider=provider)

    payload = {
        "product": "Đây là một sản phẩm mới (Máy pha cà phê mini cá nhân pin sạc). Hãy đánh giá xem có nên đưa sản phẩm này ra bán trên TikTok Shop Philippines hay không.",
        "market": "Philippines",
        "constraints": {"budget": 500},
    }

    state = await agent.run(payload)
    assert state.status == "COMPLETED"
    report = state.final_result

    # Schema contract verification
    assert "product" in report
    assert "target_customer" in report
    assert "customer_problem" in report
    assert "customer_need" in report
    assert "value_proposition" in report
    assert isinstance(report["usp"], list)
    assert "uvp" in report
    assert "positioning" in report
    assert isinstance(report["differentiation"], list)
    assert isinstance(report["offer_strategy"], dict)
    assert isinstance(report["pricing_analysis"], dict)
    assert isinstance(report["product_market_fit"], dict)
    assert isinstance(report["validation_plan"], dict)
    assert isinstance(report["risks"], list)
    assert isinstance(report["assumptions"], list)
    assert isinstance(report["unknowns"], list)
    assert "recommendation" in report
    assert isinstance(report["confidence"], (int, float))
    assert len(report["usp"]) >= 1
    assert len(report["differentiation"]) >= 1


def test_product_api_endpoint():
    payload = {
        "product": {"name": "Máy pha cà phê mini cá nhân", "category": "Gia dụng thông minh"},
        "market": "Philippines",
        "provider": "mock",
    }

    response = client.post("/api/v1/agents/product/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "product" in data
    assert "product_market_fit" in data
    assert "offer_strategy" in data
    assert "recommendation" in data
    assert data["confidence"] >= 70

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.skills.loader import SkillLoader
from app.core.skills.registry import SkillRegistry, skill_registry
from app.core.skills.executor import SkillExecutor
from app.core.skills.evaluator import SkillEvaluator
from app.agents.market_research_agent import MarketResearchAgent
from app.core.llm.factory import LLMProviderFactory

client = TestClient(app)


def test_skill_discovery():
    skills = skill_registry.list_skills()
    assert len(skills) >= 10
    names = [s.metadata.name for s in skills]
    expected = [
        "market_research",
        "competitor_analysis",
        "customer_analysis",
        "trend_analysis",
        "demand_analysis",
        "pricing_analysis",
        "product_validation",
        "opportunity_scoring",
        "risk_analysis",
        "market_report",
    ]
    for name in expected:
        assert name in names


def test_skill_registry():
    assert skill_registry.has_skill("competitor_analysis") is True
    assert skill_registry.has_skill("non_existent_skill") is False

    skill = skill_registry.get_skill("competitor_analysis")
    assert skill is not None
    assert skill.metadata.name == "competitor_analysis"
    assert skill.metadata.version == "1.0.0"
    assert skill_registry.get_skill_version("competitor_analysis") == "1.0.0"


def test_skill_loading():
    skills_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "skills", "market_research")
    )
    skill = SkillLoader.load_skill_from_dir(skills_dir)
    assert skill.is_valid is True
    assert skill.metadata.name == "market_research"
    assert len(skill.rules_content) > 0
    assert len(skill.examples_content) > 0
    assert len(skill.evals_content) > 0


def test_missing_skill_file_graceful_handling(tmp_path):
    # Empty dir without SKILL.md
    empty_skill_dir = str(tmp_path / "broken_skill")
    os.makedirs(empty_skill_dir, exist_ok=True)

    skill = SkillLoader.load_skill_from_dir(empty_skill_dir)
    assert skill.is_valid is False
    assert "missing" in skill.validation_error.lower()


def test_invalid_skill_validation():
    registry = SkillRegistry()
    assert registry.has_skill("invalid_one") is False
    assert registry.get_skill("invalid_one") is None


def test_rules_loading():
    skill = skill_registry.get_skill("market_research")
    assert "Nguyên tắc" in skill.rules_content or "Rules" in skill.rules_content or len(skill.rules_content) > 0


def test_examples_loading():
    skill = skill_registry.get_skill("market_research")
    assert "Example" in skill.examples_content or "Input" in skill.examples_content


def test_evaluation_loading():
    skill = skill_registry.get_skill("market_research")
    assert "Test Case" in skill.evals_content or "Rules to Verify" in skill.evals_content or len(skill.evals_content) > 0


@pytest.mark.asyncio
async def test_skill_execution():
    executor = SkillExecutor()
    res = await executor.execute_skill(
        skill_name="market_research",
        input_data={"product_name": "Xe máy điện", "target_market": "Vietnam"},
        agent_name="TestAgent",
        provider_name="mock",
    )
    assert res.status in ("SUCCESS", "MOCK_SUCCESS")
    assert res.skill_name == "market_research"
    assert "market_size_estimate" in res.result


@pytest.mark.asyncio
async def test_mock_provider():
    executor = SkillExecutor()
    res = await executor.execute_skill(
        skill_name="competitor_analysis",
        input_data={"product_name": "Bánh Trung Thu", "target_market": "Vietnam"},
        provider_name="mock",
    )
    assert res.provider_used == "mock"
    assert res.status == "MOCK_SUCCESS"
    assert "direct_competitors" in res.result


@pytest.mark.asyncio
async def test_market_research_agent_with_skill_system():
    provider = LLMProviderFactory.get_provider("mock")
    agent = MarketResearchAgent(llm_provider=provider)
    state = await agent.run({"product_name": "Portable Blender", "target_market": "Vietnam"})

    assert state.status == "COMPLETED"
    assert "opportunities" in state.final_result
    assert "risks" in state.final_result
    assert len(state.intermediate_steps) >= 4  # Skill chain executed


@pytest.mark.asyncio
async def test_skill_chain_execution():
    executor = SkillExecutor()
    chain = ["market_research", "competitor_analysis", "opportunity_scoring"]
    results = []

    for sk_name in chain:
        res = await executor.execute_skill(
            skill_name=sk_name,
            input_data={"product_name": "Smart Watch", "target_market": "Vietnam"},
        )
        results.append(res)
        assert res.status in ("SUCCESS", "MOCK_SUCCESS")

    assert len(results) == 3


def test_skills_api_endpoints():
    # 1. GET /api/v1/skills
    res_list = client.get("/api/v1/skills")
    assert res_list.status_code == 200
    skills_data = res_list.json()
    assert len(skills_data) >= 10

    # 2. GET /api/v1/skills/competitor_analysis
    res_detail = client.get("/api/v1/skills/competitor_analysis")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["metadata"]["name"] == "competitor_analysis"

    # 3. POST /api/v1/skills/competitor_analysis/validate
    res_val = client.post("/api/v1/skills/competitor_analysis/validate")
    assert res_val.status_code == 200
    val_data = res_val.json()
    assert val_data["is_valid"] is True
    assert val_data["files_checked"]["SKILL.md"] is True

    # 4. POST /api/v1/skills/competitor_analysis/execute
    res_exec = client.post(
        "/api/v1/skills/competitor_analysis/execute",
        json={
            "input_payload": {"product_name": "Portable Blender", "target_market": "Vietnam"},
            "provider": "mock",
        },
    )
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["status"] in ("SUCCESS", "MOCK_SUCCESS")
    assert "direct_competitors" in exec_data["result"]

    # 5. GET /api/v1/skills/competitor_analysis/evals
    res_eval = client.get(
        "/api/v1/skills/competitor_analysis/evals?product_name=Portable+Blender&target_market=Vietnam"
    )
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["score"] >= 80.0
    assert eval_data["skill_name"] == "competitor_analysis"

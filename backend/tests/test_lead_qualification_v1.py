import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.skills.registry import skill_registry
from app.agents.lead_qualification_agent import LeadQualificationAgent
from app.core.llm.factory import LLMProviderFactory

client = TestClient(app)


def test_lead_qualification_profile_existence():
    profile_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "agents", "lead_qualification")
    )
    assert os.path.exists(os.path.join(profile_dir, "ROLE.md"))
    assert os.path.exists(os.path.join(profile_dir, "MISSION.md"))
    assert os.path.exists(os.path.join(profile_dir, "KNOWLEDGE"))
    assert os.path.exists(os.path.join(profile_dir, "RULES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EXAMPLES.md"))
    assert os.path.exists(os.path.join(profile_dir, "EVALS.md"))
    assert os.path.exists(os.path.join(profile_dir, "TOOLS.md"))
    assert os.path.exists(os.path.join(profile_dir, "PERMISSIONS.md"))


def test_lead_qualification_14_skills_discovery():
    expected_14_skills = [
        "lead_intake",
        "qualification_planning",
        "intent_detection",
        "customer_information_extraction",
        "pain_point_detection",
        "need_detection",
        "objection_detection",
        "conversation_context_tracking",
        "qualification_question_selection",
        "lead_scoring",
        "lead_classification",
        "qualification_summary",
        "sales_handoff",
        "next_action_recommendation",
    ]
    for sk_name in expected_14_skills:
        assert skill_registry.has_skill(sk_name) is True, f"Skill '{sk_name}' missing from registry"


@pytest.mark.asyncio
async def test_lead_qualification_8_mock_scenarios():
    provider = LLMProviderFactory.get_provider("mock")
    agent = LeadQualificationAgent(llm_provider=provider)

    # Scenario 1: Clear Intent & Budget
    res1 = await agent.run({
        "lead": {"source": "Facebook Ads", "phone": "+84901234567"},
        "conversation": [{"speaker": "CUSTOMER", "text": "Anh đang tìm căn 2 phòng ngủ khoảng 3 tỷ, chắc cuối tháng mới mua."}]
    })
    data1 = res1.final_result
    assert data1["classification"] == "HOT"
    assert data1["score"]["score"] >= 80.0
    assert data1["qualification"]["product_interest"] == "Căn hộ 2 Phòng Ngủ"
    assert data1["qualification"]["budget"] == "3.000.000.000 VND"
    assert "location" in data1["handoff"]["missing_information"]

    # Scenario 2: Exploring
    res2 = await agent.run({"message": "Anh chỉ xem cho biết thôi chứ chưa có ý định mua."})
    data2 = res2.final_result
    assert data2["classification"] in ("COLD", "WARM")

    # Scenario 3: Busy
    res3 = await agent.run({"message": "Anh đang họp, gọi lại sau nhé."})
    data3 = res3.final_result
    assert data3["qualification"]["intent"] == "BUSY"

    # Scenario 4: Rejection
    res4 = await agent.run({"message": "Tôi nhầm số rồi, đừng gọi nữa."})
    data4 = res4.final_result
    assert data4["qualification"]["intent"] == "REJECT"
    assert data4["classification"] == "INVALID"

    # Scenario 5: Missing Info
    res5 = await agent.run({"message": "Tôi muốn tìm mua căn hộ giá rẻ."})
    data5 = res5.final_result
    assert len(data5["handoff"]["missing_information"]) >= 2

    # Scenario 6: Contradictory Info
    res6 = await agent.run({"message": "Tôi muốn mua biệt thự cao cấp nhưng ngân sách chỉ có 500 triệu."})
    data6 = res6.final_result
    assert "qualification" in data6

    # Scenario 7: High Intent but Missing Info
    res7 = await agent.run({"message": "Tôi cần chuyển nhượng mua ngay trong tuần này."})
    data7 = res7.final_result
    assert data7["qualification"]["timeline"] is not None

    # Scenario 8: Loan Financing
    res8 = await agent.run({"message": "Tài chính anh có 1 tỷ, cần vay thêm 50% được không?"})
    data8 = res8.final_result
    assert data8["qualification"] is not None


def test_lead_qualification_api_endpoint():
    payload = {
        "lead": {"source": "Facebook Ads", "phone": "+84901234567"},
        "conversation": [
            {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ."},
            {"speaker": "CUSTOMER", "text": "Ngân sách khoảng 3 tỷ."},
            {"speaker": "CUSTOMER", "text": "Cuối tháng anh muốn mua."}
        ],
        "provider": "mock"
    }

    response = client.post("/api/v1/agents/lead-qualification/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "qualification" in data
    assert "score" in data
    assert "classification" in data
    assert "next_question" in data
    assert "handoff" in data
    assert data["classification"] == "HOT"
    assert data["handoff"]["score"] >= 80.0

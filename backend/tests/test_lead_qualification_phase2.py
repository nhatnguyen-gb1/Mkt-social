import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.qualification.engine import QualificationEngine
from app.core.qualification.dataset import MOCK_DATASET_100
from app.agents.lead_qualification_agent import LeadQualificationAgent
from app.core.llm.factory import LLMProviderFactory

client = TestClient(app)


def test_qualification_engine_100_scenarios_dataset():
    engine = QualificationEngine()
    
    tp_hot = 0
    fp_hot = 0
    fn_hot = 0
    tn_hot = 0

    total_scenarios = len(MOCK_DATASET_100)
    assert total_scenarios == 100, f"Expected 100 scenarios, got {total_scenarios}"

    for scenario in MOCK_DATASET_100:
        result = engine.process(
            lead_data=scenario["lead"],
            conversation=scenario["conversation"],
        )
        actual_cls = result["classification"]
        expected_cls = scenario["expected_classification"]

        if expected_cls == "HOT":
            if actual_cls == "HOT":
                tp_hot += 1
            else:
                fn_hot += 1
        else:
            if actual_cls == "HOT":
                fp_hot += 1
            else:
                tn_hot += 1

        if scenario.get("has_contradiction"):
            assert result["contradiction"]["has_contradiction"] is True

    # Calculate HOT Lead Metrics
    hot_precision = tp_hot / (tp_hot + fp_hot) if (tp_hot + fp_hot) > 0 else 0.0
    hot_recall = tp_hot / (tp_hot + fn_hot) if (tp_hot + fn_hot) > 0 else 0.0
    hot_f1 = (2 * hot_precision * hot_recall) / (hot_precision + hot_recall) if (hot_precision + hot_recall) > 0 else 0.0

    print(f"\n--- EVALUATION METRICS REPORT (100 SCENARIOS) ---")
    print(f"HOT Lead TP: {tp_hot}, FP: {fp_hot}, FN: {fn_hot}, TN: {tn_hot}")
    print(f"HOT Lead Precision: {hot_precision:.4f}")
    print(f"HOT Lead Recall:    {hot_recall:.4f}")
    print(f"HOT Lead F1 Score:  {hot_f1:.4f}")

    assert hot_precision >= 0.90, f"HOT Precision {hot_precision} below threshold 0.90"
    assert hot_recall >= 0.90, f"HOT Recall {hot_recall} below threshold 0.90"
    assert hot_f1 >= 0.90, f"HOT F1 Score {hot_f1} below threshold 0.90"


def test_contradiction_detection():
    engine = QualificationEngine()
    
    # Case with contradiction
    res = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh có ngân sách khoảng 3 tỷ."},
            {"speaker": "CUSTOMER", "text": "Thực ra anh chỉ có khoảng 1.5 tỷ thôi."}
        ]
    )
    assert res["contradiction"]["has_contradiction"] is True
    assert res["contradiction"]["needs_clarification"] is True
    assert "3.000.000.000 VND" in res["contradiction"]["conflicting_values"]
    assert "1.500.000.000 VND" in res["contradiction"]["conflicting_values"]
    assert res["classification"] == "UNKNOWN"


def test_confidence_calibration():
    engine = QualificationEngine()
    
    # Clear high-evidence scenario -> high confidence
    res1 = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[{"speaker": "CUSTOMER", "text": "Anh mua căn 2 phòng ngủ 3 tỷ cuối tháng này tại Quận 7."}]
    )
    assert res1["confidence"] >= 0.85

    # Ambiguous scenario -> lower confidence
    res2 = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[{"speaker": "CUSTOMER", "text": "Anh chỉ xem cho biết thôi."}]
    )
    assert res2["confidence"] <= 0.80


def test_6_manual_swagger_cases():
    provider = LLMProviderFactory.get_provider("mock")
    agent = LeadQualificationAgent(llm_provider=provider)

    # CASE 1: Clear High Intent
    c1 = client.post("/api/v1/agents/lead-qualification/analyze", json={
        "lead": {"phone": "+84901234567"},
        "conversation": [{"speaker": "CUSTOMER", "text": "Anh đang tìm căn 2 phòng ngủ khoảng 3 tỷ, cuối tháng muốn mua."}]
    }).json()
    assert c1["classification"] == "HOT"
    assert c1["score"]["score"] >= 80.0

    # CASE 2: Browsing / Low Intent
    c2 = client.post("/api/v1/agents/lead-qualification/analyze", json={
        "lead": {"phone": "+84901234567"},
        "conversation": [{"speaker": "CUSTOMER", "text": "Anh chỉ xem thử thôi, chưa có nhu cầu."}]
    }).json()
    assert c2["classification"] == "COLD"

    # CASE 3: Busy Callback
    c3 = client.post("/api/v1/agents/lead-qualification/analyze", json={
        "lead": {"phone": "+84901234567"},
        "conversation": [{"speaker": "CUSTOMER", "text": "Anh đang bận, lúc khác gọi lại."}]
    }).json()
    assert c3["next_action"] == "SCHEDULE_CALLBACK"

    # CASE 4: Missing Budget
    c4 = client.post("/api/v1/agents/lead-qualification/analyze", json={
        "lead": {"phone": "+84901234567"},
        "conversation": [{"speaker": "CUSTOMER", "text": "Anh muốn mua nhưng chưa biết ngân sách."}]
    }).json()
    assert "budget" in c4["handoff"]["missing_information"]

    # CASE 5: Contradiction
    c5 = client.post("/api/v1/agents/lead-qualification/analyze", json={
        "lead": {"phone": "+84901234567"},
        "conversation": [
            {"speaker": "CUSTOMER", "text": "Anh có 3 tỷ."},
            {"speaker": "CUSTOMER", "text": "Thực ra anh chỉ có 1.5 tỷ."}
        ]
    }).json()
    assert c5["contradiction"]["has_contradiction"] is True

    # CASE 6: Wrong Number / Rejection
    c6 = client.post("/api/v1/agents/lead-qualification/analyze", json={
        "lead": {"phone": "+84901234567"},
        "conversation": [{"speaker": "CUSTOMER", "text": "Không phải tôi đăng ký số này."}]
    }).json()
    assert c6["classification"] == "INVALID"

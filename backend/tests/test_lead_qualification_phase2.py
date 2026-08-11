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


# ====================================================================
# VALIDATION PHASE 2 ADDITIONAL TESTS — Anti-Hallucination & Score Consistency
# ====================================================================

def test_minimal_evidence_no_hallucination():
    """
    TEST A: Chỉ cung cấp product + budget.
    Tất cả các field không được suy diễn (purpose, location, timeline, financing, appointment_intent)
    phải là UNKNOWN/null.
    """
    engine = QualificationEngine()
    res = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ, ngân sách khoảng 3 tỷ."}
        ]
    )
    q = res["qualification"]

    # Thông tin CÓ evidence trực tiếp
    assert q["product_interest"] == "Căn hộ 2 Phòng Ngủ", "product_interest phải được extract từ conversation"
    assert "3" in q["budget"] and "VND" in q["budget"], "budget phải được extract từ conversation"

    # Thông tin KHÔNG CÓ evidence → phải UNKNOWN
    assert q["purpose"] == "UNKNOWN", f"purpose phải UNKNOWN khi khách chưa nói mục đích, got: {q['purpose']}"
    assert q["location"] == "UNKNOWN", f"location phải UNKNOWN, got: {q['location']}"
    assert q["timeline"] == "UNKNOWN", f"timeline phải UNKNOWN, got: {q['timeline']}"
    assert q["financing"] == "UNKNOWN", f"financing phải UNKNOWN, got: {q['financing']}"
    assert q["appointment_intent"] == "UNKNOWN", f"appointment_intent phải UNKNOWN khi chưa có agreement, got: {q['appointment_intent']}"


def test_explicit_purpose_evidence():
    """
    TEST B: purpose chỉ được xác định khi có evidence tường minh từ khách hàng.
    """
    engine = QualificationEngine()

    # Có evidence "để ở" → purpose được xác định
    res_with_evidence = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh mua căn 2 phòng ngủ để ở cùng gia đình."}
        ]
    )
    q = res_with_evidence["qualification"]
    assert q["purpose"] != "UNKNOWN", "purpose phải được detect khi khách nói 'để ở'"
    assert q["purpose_evidence"] is not None, "purpose_evidence phải có giá trị khi có evidence"

    # Không có evidence → UNKNOWN
    res_without = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ, ngân sách khoảng 3 tỷ."}
        ]
    )
    q2 = res_without["qualification"]
    assert q2["purpose"] == "UNKNOWN", f"purpose phải UNKNOWN khi không có evidence mục đích, got: {q2['purpose']}"
    assert q2["purpose_evidence"] is None, "purpose_evidence phải None khi không có evidence"


def test_appointment_intent_never_assumed():
    """
    TEST C: appointment_intent phải là UNKNOWN cho đến khi khách đồng ý rõ ràng.
    Kể cả HOT lead cũng không được tự set ACCEPTED.
    """
    engine = QualificationEngine()

    # HOT lead — vẫn phải UNKNOWN cho appointment
    hot_res = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh đang tìm căn 2 phòng ngủ khoảng 3 tỷ, cuối tháng muốn mua."}
        ]
    )
    assert hot_res["classification"] == "HOT", "Scenario này phải là HOT"
    q = hot_res["qualification"]
    assert q["appointment_intent"] == "UNKNOWN", (
        f"appointment_intent phải UNKNOWN cho HOT lead chưa đồng ý lịch hẹn, got: {q['appointment_intent']}"
    )

    # WARM lead — cũng phải UNKNOWN
    warm_res = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[{"speaker": "CUSTOMER", "text": "Anh đang bận, lúc khác gọi lại."}]
    )
    q2 = warm_res["qualification"]
    assert q2["appointment_intent"] == "UNKNOWN", (
        f"appointment_intent phải UNKNOWN cho BUSY/WARM lead, got: {q2['appointment_intent']}"
    )


def test_score_reasoning_consistency():
    """
    TEST D & E: Kiểm tra score calculation nhất quán với reasoning.
    Tổng các giá trị điều chỉnh trong reasoning phải khớp final score.
    """
    engine = QualificationEngine()

    test_cases = [
        # (description, conversation_text)
        ("HOT với budget + timeline", "Anh tìm căn 2 phòng ngủ 3 tỷ, cuối tháng mua."),
        ("WARM BUSY", "Anh đang bận họp."),
        ("COLD BROWSING", "Anh chỉ xem cho biết thôi."),
        ("Có mâu thuẫn budget", "Anh có 3 tỷ. Thực ra chỉ có 1.5 tỷ."),
        ("Thiếu nhiều thông tin", "Anh tìm nhà."),
    ]

    for desc, text in test_cases:
        res = engine.process(
            lead_data={"phone": "+84901234567"},
            conversation=[{"speaker": "CUSTOMER", "text": text}]
        )
        score_obj = res["score"]
        final_score = score_obj["score"]
        reasoning_list = score_obj["reasoning"]

        # Kiểm tra reasoning có "Tổng điểm" dòng tổng kết
        tally_lines = [r for r in reasoning_list if "Tổng điểm" in r]
        assert len(tally_lines) == 1, (
            f"[{desc}] Phải có đúng 1 dòng 'Tổng điểm' trong reasoning, got: {reasoning_list}"
        )

        # Parse tổng điểm từ dòng tổng kết
        tally_str = tally_lines[0]
        # Format: "Tổng điểm = 30 + 30 + 25 + 15 = 100"
        parts = tally_str.split("=")
        assert len(parts) >= 2, f"[{desc}] Dòng tổng kết format không hợp lệ: {tally_str}"
        declared_total = float(parts[-1].strip())
        assert declared_total == final_score, (
            f"[{desc}] Tổng điểm trong reasoning ({declared_total}) KHÔNG khớp final_score ({final_score})"
        )


def test_score_no_hardcoded_mismatch():
    """
    TEST D bổ sung: Kiểm tra cụ thể case "2 phòng ngủ + 3 tỷ" không có qualification_score = 85 sai.
    Base=30 + Intent_BUY=30 + Budget=25 = 85, KHÔNG có timeline nên không +15.
    """
    engine = QualificationEngine()
    res = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ, ngân sách khoảng 3 tỷ."}
        ]
    )
    score = res["score"]["score"]
    # Base 30 + BUY 30 + Budget 25 = 85 (no timeline → no +15)
    assert score == 85.0, f"Expected score=85.0 (30+30+25), got {score}"

    reasoning = res["score"]["reasoning"]
    # Tất cả adjustment phải xuất hiện trong reasoning
    reasoning_text = " ".join(reasoning)
    assert "30" in reasoning_text and "25" in reasoning_text, (
        f"Reasoning thiếu các adjustment: {reasoning}"
    )

    # Tổng điểm trong tally line phải khớp
    tally = [r for r in reasoning if "Tổng điểm" in r]
    assert len(tally) == 1
    declared = float(tally[0].split("=")[-1].strip())
    assert declared == score, f"Score declared in tally ({declared}) != final_score ({score})"


def test_investment_purpose_explicit():
    """
    TEST B phụ: Purpose đầu tư chỉ được detect khi có từ khóa đầu tư/cho thuê tường minh.
    """
    engine = QualificationEngine()
    res = engine.process(
        lead_data={"phone": "+84901234567"},
        conversation=[
            {"speaker": "CUSTOMER", "text": "Anh muốn mua để đầu tư, cho thuê kiếm dòng tiền."}
        ]
    )
    q = res["qualification"]
    assert q["purpose"] != "UNKNOWN", "purpose phải detect được khi có từ khóa đầu tư/cho thuê"
    assert "đầu tư" in q["purpose"].lower() or "cho thuê" in q["purpose"].lower()

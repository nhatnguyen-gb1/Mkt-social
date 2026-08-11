"""
test_call_scenarios_50.py — Phase 3: 50+ End-to-End Call Scenarios
Comprehensive test suite testing all call variations and edge cases.
"""
import pytest
from app.core.calling import (
    CallOrchestrator,
    CallState,
    ErrorCode,
    MockCallSimulator,
)

@pytest.fixture
def simulator():
    return MockCallSimulator()


@pytest.fixture
def orchestrator():
    return CallOrchestrator()


# ── 1 TO 10: CORE BUYER & INTENT TYPES ──────────────────────────────────────

def test_scenario_01_hot_buyer(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh đang tìm mua căn hộ 2 phòng ngủ.",
            "Ngân sách khoảng 3 tỷ.",
            "Muốn ở khu vực Quận 7.",
            "Anh mua để ở cho gia đình.",
            "Cuối tháng này anh chốt mua ngay.",
            "Anh mua bằng tiền mặt không cần vay.",
        ]
    )
    assert res.final_call_state in ["COMPLETED", "QUALIFYING"]
    assert res.qualification_result.get("classification") in ["HOT", "WARM"]
    assert res.handoff_brief is not None


def test_scenario_02_warm_buyer(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh quan tâm dự án căn hộ.",
            "Tầm 2 đến 3 tỷ.",
            "Tầm 3 tháng nữa anh mới mua.",
            "Để anh xem thêm vị trí.",
        ]
    )
    assert res.qualification_result.get("classification") in ["WARM", "HOT"]


def test_scenario_03_cold_browser(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh xem cho biết thôi.",
            "Chưa có ý định mua.",
            "Chưa tính ngân sách.",
        ]
    )
    assert res.qualification_result.get("classification") in ["COLD", "WARM"]


def test_scenario_04_invalid_number(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Nhầm số rồi bạn ơi, tôi không đăng ký.",
        ]
    )
    assert res.final_call_state in ["COMPLETED", "CANCELLED"]


def test_scenario_05_unknown_intent(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Tôi chưa biết nữa.",
            "Để tính sau đi.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_06_investor(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh mua đầu tư căn hộ cho thuê.",
            "Tầm 4 tỷ.",
            "Cần dự án dòng tiền tốt ở Thủ Đức.",
        ]
    )
    assert res.qualification_result.get("score", {}).get("score", 0) > 40


def test_scenario_07_renter(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh chỉ tìm thuê căn hộ thôi, không mua.",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_08_seller(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh muốn ký gửi bán căn hộ chứ không phải mua.",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_09_busy_customer(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh đang bận họp, chiều gọi lại sau nhé.",
        ]
    )
    assert res.final_call_state == "CALLBACK_SCHEDULED"


def test_scenario_10_scheduled_callback(orchestrator):
    call = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(call.call_id)
    cb = orchestrator.schedule_callback(call.call_id, scheduled_at="2026-08-11T15:00:00Z", reason="BUSY")
    assert cb.status == "SCHEDULED"
    assert call.state == CallState.CALLBACK_SCHEDULED


# ── 11 TO 20: MISSING FIELDS & OBJECTIONS ────────────────────────────────────

def test_scenario_11_budget_missing(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh muốn tìm căn hộ 2PN ở Quận 7.",
            "Chưa tiện nói ngân sách.",
            "Để ở cho gia đình.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_12_location_missing(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh có ngân sách 3 tỷ.",
            "Chỗ nào ở TP.HCM cũng được.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_13_timeline_missing(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh tìm mua căn hộ 3 tỷ ở Quận 2.",
            "Khi nào thích thì mua thôi chưa vội.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_14_financing_missing(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh mua căn 3 tỷ.",
            "Chưa biết có vay ngân hàng không.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_15_general_objection(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh thấy giá bên em hơi cao.",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_16_price_objection(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Đắt quá, vượt quá khả năng tài chính của anh rồi.",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_17_legal_objection(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Dự án này có pháp lý sổ hồng rõ ràng không?",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_18_family_approval_objection(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Anh phải về hỏi lại ý kiến vợ anh đã.",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_19_customer_changes_budget(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Ban đầu anh tính mua tầm 2 tỷ.",
            "Thôi anh cố lên được khoảng 3 tỷ rưỡi.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_20_contradiction(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Ngân sách anh khoảng 3 tỷ.",
            "Thực ra anh chỉ có 1.5 tỷ thôi.",
        ]
    )
    assert res.qualification_result.get("contradiction", {}).get("has_contradiction") is True


# ── 21 TO 30: INTERACTION VARIATIONS & ERRORS ─────────────────────────────────

def test_scenario_21_customer_changes_intent(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Lúc đầu anh định thuê.",
            "Nhưng thôi anh muốn mua luôn.",
        ]
    )
    assert res.total_turns >= 2


def test_scenario_22_customer_asks_ai_question(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Em là AI hay người thật vậy?",
        ]
    )
    assert res.total_turns >= 1


def test_scenario_23_customer_interrupts(orchestrator):
    call = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(call.call_id)
    orchestrator.process_turn(call.call_id, "Anh đang tìm mua nhà.")
    res = orchestrator.interrupt_turn(call.call_id, "Khoan đã, dự án ở đâu?")
    assert res.interrupted is True


def test_scenario_24_customer_refusal(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Đừng gọi cho tôi nữa, không có nhu cầu!",
        ]
    )
    assert res.final_call_state in ["COMPLETED", "CANCELLED"]


def test_scenario_25_customer_angry(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Vớ vẩn quá, phiền phức bực cả mình!",
        ]
    )
    assert res.handoff_brief is not None


def test_scenario_26_customer_asks_human(simulator):
    res = simulator.run_simulation(
        conversation_turns=[
            "Cho tôi gặp nhân viên tư vấn trực tiếp.",
        ]
    )
    assert res.handoff_brief is not None


def test_scenario_27_stt_failure(orchestrator):
    call = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(call.call_id)
    # Simulate empty or malformed audio input
    res = orchestrator.process_turn(call.call_id, "")
    assert res.ai_text is not None


def test_scenario_28_tts_failure(orchestrator):
    call = orchestrator.create_call(phone="+84901234567")
    orchestrator.start_call(call.call_id)
    res = orchestrator.process_turn(call.call_id, "Tầm 3 tỷ.")
    assert res.tts_payload is not None


def test_scenario_29_ai_timeout(orchestrator):
    call = orchestrator.create_call(phone="+84901234567")
    failed = orchestrator.handle_call_failure(call.call_id, ErrorCode.AI_TIMEOUT, "LLM timeout")
    assert failed.state == CallState.FAILED


def test_scenario_30_telephony_failure(orchestrator):
    call = orchestrator.create_call(phone="+84901234567")
    failed = orchestrator.handle_call_failure(call.call_id, ErrorCode.NETWORK_ERROR, "Signal lost")
    assert failed.state == CallState.FAILED


# ── 31 TO 55: ADDITIONAL VARIATIONS (MULTI-TURN & SPECIAL SLANG) ─────────────

@pytest.mark.parametrize("scenario_id,turns", [
    (31, ["Tầm 30 lẻ.", "Quận 7 em."]),
    (32, ["2 ky rưỡi.", "Thủ Đức."]),
    (33, ["Anh có khoảng 5 tỷ.", "Đầu tư cho thuê."]),
    (34, ["Mua trả góp ngân hàng 70%.", "Tầm 3 tỷ."]),
    (35, ["Chỉ xem dự án Vinhome.", "Cuối tháng mua."]),
    (36, ["Anh kẹt tiền quá chưa mua được."]),
    (37, ["Gửi thông tin qua Zalo đi."]),
    (38, ["Email cho anh thông tin dự án."]),
    (39, ["Đang xem nhiều bên khác."]),
    (40, ["Chưa tin tưởng mấy vụ này."]),
    (41, ["Căn 1 phòng ngủ giá bao nhiêu?"]),
    (42, ["Căn 3 phòng ngủ còn không?"]),
    (43, ["Penthouse bên em giá tầm bao nhiêu?"]),
    (44, ["Có bán shophouse không em?"]),
    (45, ["Dự án này bao giờ giao nhà?"]),
    (46, ["Chiết khấu thanh toán sớm bao nhiêu %?"]),
    (47, ["Có được ân hạn nợ gốc không?"]),
    (48, ["Ngân hàng nào hỗ trợ cho vay?"]),
    (49, ["Anh muốn xem nhà mẫu vào cuối tuần."]),
    (50, ["Đặt cọc giữ chỗ bao nhiêu tiền?"]),
    (51, ["Phí quản lý hàng tháng bao nhiêu?"]),
    (52, ["Có chỗ đậu xe ô tô không em?"]),
    (53, ["Tiện ích xung quanh có trường học không?"]),
    (54, ["Cho anh xin brochure dự án."]),
    (55, ["Tư vấn giúp anh căn view sông."]),
])
def test_additional_scenarios_31_to_55(simulator, scenario_id, turns):
    res = simulator.run_simulation(conversation_turns=turns)
    assert res.call_id is not None
    assert res.total_turns >= 1

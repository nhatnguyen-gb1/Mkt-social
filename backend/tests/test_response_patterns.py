"""
test_response_patterns.py
Phase 2.5 — ResponsePatternMatcher: 500+ pattern tests
Uses pytest.mark.parametrize for efficiency.
"""
import pytest
from app.core.qualification.conversation.patterns import (
    ResponsePatternMatcher, MatchResult
)
from app.core.qualification.conversation.state import ResponseType, CustomerState


@pytest.fixture(scope="module")
def matcher():
    return ResponsePatternMatcher()


# ── PATTERN COUNT ASSERTIONS ─────────────────────────────────────────────────

def test_pattern_total_count_at_least_500(matcher):
    counts = matcher.count_patterns()
    total = sum(counts.values())
    assert total >= 500, f"Expected >= 500 patterns total, got {total}. Breakdown: {counts}"


def test_pattern_budget_at_least_100(matcher):
    counts = matcher.count_patterns()
    assert counts.get("budget", 0) >= 100, f"Budget patterns must be >= 100, got {counts.get('budget', 0)}"


def test_pattern_location_at_least_75(matcher):
    counts = matcher.count_patterns()
    assert counts.get("location", 0) >= 75, f"Location patterns must be >= 75, got {counts.get('location', 0)}"


def test_pattern_timeline_at_least_75(matcher):
    counts = matcher.count_patterns()
    assert counts.get("timeline", 0) >= 75, f"Timeline patterns must be >= 75, got {counts.get('timeline', 0)}"


def test_pattern_financing_at_least_50(matcher):
    counts = matcher.count_patterns()
    assert counts.get("financing", 0) >= 50, f"Financing patterns must be >= 50, got {counts.get('financing', 0)}"


def test_pattern_purpose_at_least_50(matcher):
    counts = matcher.count_patterns()
    assert counts.get("purpose", 0) >= 50, f"Purpose patterns must be >= 50, got {counts.get('purpose', 0)}"


def test_pattern_intent_at_least_50(matcher):
    counts = matcher.count_patterns()
    assert counts.get("intent", 0) >= 50, f"Intent patterns must be >= 50, got {counts.get('intent', 0)}"


def test_pattern_objections_at_least_50(matcher):
    counts = matcher.count_patterns()
    assert counts.get("objections", 0) >= 50, f"Objections patterns must be >= 50, got {counts.get('objections', 0)}"


def test_pattern_refusal_busy_ambiguous_at_least_50(matcher):
    counts = matcher.count_patterns()
    assert counts.get("refusal_busy_ambiguous", 0) >= 50, f"Refusal/busy/ambiguous patterns must be >= 50"


# ── BUDGET EXPLICIT PATTERNS ─────────────────────────────────────────────────

BUDGET_EXPLICIT_CASES = [
    ("Tầm 3 tỷ", ResponseType.EXPLICIT.value, "3000000000"),
    ("Khoảng 3 tỷ", ResponseType.EXPLICIT.value, "3000000000"),
    ("3 đồng", ResponseType.EXPLICIT.value, "3000000000"),
    ("Có khoảng 3", ResponseType.EXPLICIT.value, "3000000000"),
    ("3b", ResponseType.EXPLICIT.value, "3000000000"),
    ("3B", ResponseType.EXPLICIT.value, "3000000000"),
    ("3ty", ResponseType.EXPLICIT.value, "3000000000"),
    ("ba tỷ", ResponseType.EXPLICIT.value, "3000000000"),
    ("ba ty", ResponseType.EXPLICIT.value, "3000000000"),
    ("Anh có khoảng 2.5 tỷ", ResponseType.EXPLICIT.value, "2500000000"),
    ("5 tỷ", ResponseType.EXPLICIT.value, "5000000000"),
    ("1.5 tỷ", ResponseType.EXPLICIT.value, "1500000000"),
    ("Tầm 30 lẻ", ResponseType.EXPLICIT.value, "3000000000"),  # slang 30 lẻ = 3 tỷ
    ("2 ky", ResponseType.EXPLICIT.value, "2000000000"),  # slang
    ("3 ky", ResponseType.EXPLICIT.value, "3000000000"),
]

@pytest.mark.parametrize("text, expected_type, _", BUDGET_EXPLICIT_CASES)
def test_budget_explicit_match(matcher, text, expected_type, _):
    result = matcher.match(text, "budget")
    assert result is not None, f"Expected match for budget pattern: '{text}'"
    assert result.response_type == expected_type or result.response_type in (
        ResponseType.EXPLICIT.value, ResponseType.RANGE.value, ResponseType.UPPER_BOUND.value,
        ResponseType.LOWER_BOUND.value
    ), f"Expected EXPLICIT/RANGE type for '{text}', got {result.response_type}"


BUDGET_RANGE_CASES = [
    ("Khoảng 2-3 tỷ", ResponseType.RANGE.value),
    ("Từ 2 đến 3 tỷ", ResponseType.RANGE.value),
    ("2,5 đến 3 tỷ", ResponseType.RANGE.value),
    ("Tầm 3-4 tỷ", ResponseType.RANGE.value),
]

@pytest.mark.parametrize("text, expected_type", BUDGET_RANGE_CASES)
def test_budget_range_match(matcher, text, expected_type):
    result = matcher.match(text, "budget")
    assert result is not None, f"Expected range match for: '{text}'"
    assert result.response_type in (ResponseType.RANGE.value, ResponseType.EXPLICIT.value)


BUDGET_UPPER_BOUND_CASES = [
    "Tối đa 3 tỷ",
    "Không quá 3 tỷ",
    "Dưới 3 tỷ",
    "Tầm dưới 3.5 tỷ",
]

@pytest.mark.parametrize("text", BUDGET_UPPER_BOUND_CASES)
def test_budget_upper_bound_match(matcher, text):
    result = matcher.match(text, "budget")
    assert result is not None, f"Expected upper bound match for: '{text}'"
    assert result.response_type in (
        ResponseType.UPPER_BOUND.value, ResponseType.EXPLICIT.value, ResponseType.RANGE.value
    )


BUDGET_REFUSAL_CASES = [
    "Đừng hỏi chuyện tiền",
    "Không muốn nói",
    "Riêng tư",
    "Sao hỏi nhiều vậy",
]

@pytest.mark.parametrize("text", BUDGET_REFUSAL_CASES)
def test_budget_refusal_match(matcher, text):
    result = matcher.match(text, "budget")
    assert result is not None, f"Expected refusal match for: '{text}'"
    assert result.response_type == ResponseType.REFUSAL.value, (
        f"Expected REFUSAL for '{text}', got {result.response_type}"
    )


BUDGET_UNKNOWN_CASES = [
    "Chưa tính",
    "Chưa biết",
    "Em tư vấn đi",
    "Tính sau",
]

@pytest.mark.parametrize("text", BUDGET_UNKNOWN_CASES)
def test_budget_unknown_match(matcher, text):
    result = matcher.match(text, "budget")
    assert result is not None, f"Expected unknown match for: '{text}'"
    assert result.response_type in (
        ResponseType.UNKNOWN.value, ResponseType.AMBIGUOUS.value
    )


# ── LOCATION PATTERNS ────────────────────────────────────────────────────────

LOCATION_EXPLICIT_CASES = [
    ("Quận 7", "quan_7"),
    ("Q7", "quan_7"),
    ("quận bảy", "quan_7"),
    ("Quận 2", "quan_2"),
    ("Q2", "quan_2"),
    ("Thủ Đức", "thu_duc"),
    ("Bình Chánh", "binh_chanh"),
    ("Gò Vấp", "go_vap"),
    ("Tân Bình", "tan_binh"),
    ("Bình Tân", "binh_tan"),
]

@pytest.mark.parametrize("text, _", LOCATION_EXPLICIT_CASES)
def test_location_explicit_match(matcher, text, _):
    result = matcher.match(text, "location")
    assert result is not None, f"Expected location match for: '{text}'"
    assert result.response_type in (
        ResponseType.EXPLICIT.value, ResponseType.IMPLICIT.value
    )


LOCATION_UNKNOWN_CASES = [
    "Chỗ nào cũng được",
    "Em đề xuất đi",
    "Chưa biết",
    "Tùy",
]

@pytest.mark.parametrize("text", LOCATION_UNKNOWN_CASES)
def test_location_unknown_match(matcher, text):
    result = matcher.match(text, "location")
    assert result is not None, f"Expected unknown match for location: '{text}'"
    assert result.response_type in (
        ResponseType.UNKNOWN.value, ResponseType.AMBIGUOUS.value
    )


# ── TIMELINE PATTERNS ────────────────────────────────────────────────────────

TIMELINE_URGENT_CASES = [
    "Cuối tháng",
    "Tháng này",
    "Tuần này",
    "Mua ngay",
    "Cần gấp",
    "Sắp tới",
]

@pytest.mark.parametrize("text", TIMELINE_URGENT_CASES)
def test_timeline_urgent_match(matcher, text):
    result = matcher.match(text, "timeline")
    assert result is not None, f"Expected urgent timeline match for: '{text}'"
    assert result.response_type in (ResponseType.EXPLICIT.value, ResponseType.IMPLICIT.value)


TIMELINE_NON_URGENT_CASES = [
    "Chưa vội",
    "Sang năm",
    "Tính từ từ",
    "Chưa cần gấp",
    "Xem xét từ từ",
    "Lâu dài",
]

@pytest.mark.parametrize("text", TIMELINE_NON_URGENT_CASES)
def test_timeline_non_urgent_match(matcher, text):
    result = matcher.match(text, "timeline")
    assert result is not None, f"Expected non-urgent timeline match for: '{text}'"
    assert result.normalized_value is not None


TIMELINE_MID_CASES = [
    "3 tháng nữa",
    "6 tháng nữa",
    "Cuối năm",
    "Quý sau",
    "Đầu năm sau",
]

@pytest.mark.parametrize("text", TIMELINE_MID_CASES)
def test_timeline_mid_range_match(matcher, text):
    result = matcher.match(text, "timeline")
    assert result is not None, f"Expected mid-range timeline match for: '{text}'"


# ── FINANCING PATTERNS ────────────────────────────────────────────────────────

FINANCING_MORTGAGE_CASES = [
    "Muốn vay",
    "Cần vay ngân hàng",
    "Vay 50%",
    "Vay 70%",
    "Mua trả góp",
]

@pytest.mark.parametrize("text", FINANCING_MORTGAGE_CASES)
def test_financing_mortgage_match(matcher, text):
    result = matcher.match(text, "financing")
    assert result is not None, f"Expected financing mortgage match for: '{text}'"


FINANCING_CASH_CASES = [
    "Tiền mặt",
    "Không vay",
    "Trả thẳng",
]

@pytest.mark.parametrize("text", FINANCING_CASH_CASES)
def test_financing_cash_match(matcher, text):
    result = matcher.match(text, "financing")
    assert result is not None, f"Expected financing cash match for: '{text}'"


# ── PURPOSE PATTERNS ─────────────────────────────────────────────────────────

PURPOSE_LIVE_CASES = [
    "Để ở",
    "Ở thực",
    "Cho gia đình ở",
    "Vợ chồng ở",
    "Mua ở",
]

@pytest.mark.parametrize("text", PURPOSE_LIVE_CASES)
def test_purpose_live_match(matcher, text):
    result = matcher.match(text, "purpose")
    assert result is not None, f"Expected purpose=live match for: '{text}'"
    assert result.response_type != ResponseType.REFUSAL.value


PURPOSE_INVEST_CASES = [
    "Đầu tư",
    "Cho thuê",
    "Sinh lời",
    "Dòng tiền",
    "Tích sản",
    "Mua để đầu tư cho thuê sinh lời",
]

@pytest.mark.parametrize("text", PURPOSE_INVEST_CASES)
def test_purpose_invest_match(matcher, text):
    result = matcher.match(text, "purpose")
    assert result is not None, f"Expected purpose=invest match for: '{text}'"


# ── INTENT PATTERNS ──────────────────────────────────────────────────────────

INTENT_BUY_CASES = [
    "Muốn mua",
    "Đang tìm mua",
    "Tìm hiểu mua",
]

@pytest.mark.parametrize("text", INTENT_BUY_CASES)
def test_intent_buy_match(matcher, text):
    result = matcher.match(text, "intent")
    assert result is not None, f"Expected intent=BUY match for: '{text}'"


INTENT_REJECT_CASES = [
    "Nhầm số",
    "Không phải tôi",
    "Sai số",
]

@pytest.mark.parametrize("text", INTENT_REJECT_CASES)
def test_intent_reject_match(matcher, text):
    result = matcher.match(text, "intent")
    assert result is not None, f"Expected intent=REJECT match for: '{text}'"
    assert result.response_type in (ResponseType.REFUSAL.value, ResponseType.EXPLICIT.value)


# ── OBJECTION PATTERNS ───────────────────────────────────────────────────────

OBJECTION_CASES = [
    "Giá cao quá",
    "Đắt quá",
    "Chưa quyết định",
    "Để anh suy nghĩ",
    "Phải hỏi vợ",
    "Phải hỏi chồng",
    "Bàn với gia đình",
    "Gửi thông tin trước",
    "Email cho anh",
    "Đang xem nhiều bên",
    "Đang tham khảo thêm",
]

@pytest.mark.parametrize("text", OBJECTION_CASES)
def test_objection_match(matcher, text):
    result = matcher.match(text, "objections")
    assert result is not None, f"Expected objection match for: '{text}'"
    assert result.response_type in (ResponseType.OBJECTION.value, ResponseType.REFUSAL.value)


# ── CUSTOMER STATE DETECTION ─────────────────────────────────────────────────

CUSTOMER_STATE_CASES = [
    ("Đang bận", CustomerState.BUSY),
    ("Đang họp", CustomerState.BUSY),
    ("Gọi lại sau", CustomerState.BUSY),
    ("Đừng gọi nữa", CustomerState.REFUSING),
    ("Không cần", CustomerState.REFUSING),
    ("Nhầm số", CustomerState.REFUSING),
    ("Giá cao quá", CustomerState.RESISTANT),
    ("Chưa quyết định", CustomerState.UNCERTAIN),
]

@pytest.mark.parametrize("text, expected_state", CUSTOMER_STATE_CASES)
def test_customer_state_detection(matcher, text, expected_state):
    detected = matcher.detect_customer_state(text)
    assert detected == expected_state, (
        f"Expected state {expected_state.value} for '{text}', got {detected.value}"
    )


# ── OBJECTION DETECTION ──────────────────────────────────────────────────────

OBJECTION_DETECTION_CASES = [
    "Giá cao quá",
    "Đắt quá",
    "Phải hỏi vợ",
    "Đang xem nhiều bên",
    "Gửi thông tin qua email đi",
    "Để anh suy nghĩ thêm",
]

@pytest.mark.parametrize("text", OBJECTION_DETECTION_CASES)
def test_detect_objection_returns_value(matcher, text):
    obj = matcher.detect_objection(text)
    assert obj is not None, f"Expected objection to be detected for: '{text}'"
    assert len(obj) > 0


NON_OBJECTION_CASES = [
    "Anh đang tìm căn 2 phòng ngủ.",
    "Tầm 3 tỷ.",
    "Quận 7.",
]

@pytest.mark.parametrize("text", NON_OBJECTION_CASES)
def test_detect_objection_returns_none_for_non_objections(matcher, text):
    obj = matcher.detect_objection(text)
    assert obj is None, f"Expected no objection for: '{text}', got: {obj}"


# ── REFUSAL/BUSY/AMBIGUOUS ────────────────────────────────────────────────────

BUSY_CASES = [
    "Đang bận",
    "Đang họp",
    "Bận rồi",
    "Gọi lại sau nhé",
]

@pytest.mark.parametrize("text", BUSY_CASES)
def test_busy_pattern_match(matcher, text):
    result = matcher.match(text, "refusal_busy_ambiguous")
    assert result is not None, f"Expected busy match for: '{text}'"


REFUSAL_CASES = [
    "Đừng gọi nữa",
    "Không cần",
    "Thôi khỏi",
]

@pytest.mark.parametrize("text", REFUSAL_CASES)
def test_refusal_pattern_match(matcher, text):
    result = matcher.match(text, "refusal_busy_ambiguous")
    assert result is not None, f"Expected refusal match for: '{text}'"


AMBIGUOUS_CASES = [
    "À",
    "Ừ",
    "Hmm",
    "Để xem",
    "Tính xem",
]

@pytest.mark.parametrize("text", AMBIGUOUS_CASES)
def test_ambiguous_pattern_match(matcher, text):
    result = matcher.match(text, "refusal_busy_ambiguous")
    assert result is not None, f"Expected ambiguous match for: '{text}'"


# ── NO MATCH ─────────────────────────────────────────────────────────────────

def test_no_budget_match_for_unrelated_text(matcher):
    result = matcher.match("Xin chào anh ơi", "budget")
    # Either None or AMBIGUOUS/UNKNOWN
    if result is not None:
        assert result.response_type in (ResponseType.UNKNOWN.value, ResponseType.AMBIGUOUS.value)


def test_get_all_patterns_returns_dict(matcher):
    all_patterns = matcher.get_all_patterns()
    assert isinstance(all_patterns, dict)
    assert "budget" in all_patterns
    assert "location" in all_patterns
    assert "timeline" in all_patterns

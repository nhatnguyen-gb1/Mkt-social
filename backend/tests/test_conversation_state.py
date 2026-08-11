"""
test_conversation_state.py
Phase 2.5 — ConversationState Unit Tests
"""
import pytest
from app.core.qualification.conversation.state import (
    ConversationState,
    CustomerState,
    ResponseType,
    ProvenanceStatus,
    ExtractedValue,
    ConversationTurn,
)


def make_state(phone="+84901234567") -> ConversationState:
    import uuid
    return ConversationState(phone=phone, session_id=f"test_{uuid.uuid4().hex[:6]}")


def make_extracted_value(
    field="budget",
    raw_text="khoảng 3 tỷ",
    normalized_value="3000000000",
    response_type=ResponseType.EXPLICIT.value,
    provenance=ProvenanceStatus.STATED.value,
    confidence=0.95,
    evidence="khoảng 3 tỷ",
    turn_index=0,
) -> ExtractedValue:
    return ExtractedValue(
        field=field,
        raw_text=raw_text,
        normalized_value=normalized_value,
        response_type=response_type,
        provenance=provenance,
        confidence=confidence,
        evidence=evidence,
        turn_index=turn_index,
    )


# ── STATE INITIALIZATION ─────────────────────────────────────────────────────

def test_state_initialization():
    state = make_state()
    assert state.phone == "+84901234567"
    assert state.customer_state == CustomerState.UNKNOWN
    assert state.extracted_fields == {}
    assert state.objections == []
    assert state.questions_asked == []
    assert state.contradiction_log == []
    assert state.turns == []


def test_state_has_session_id():
    state = make_state()
    assert state.session_id is not None
    assert len(state.session_id) > 0


# ── ADD TURN ─────────────────────────────────────────────────────────────────

def test_add_customer_turn():
    state = make_state()
    turn = state.add_turn("CUSTOMER", "Anh đang tìm căn 2 phòng ngủ.")
    assert isinstance(turn, ConversationTurn)
    assert turn.speaker == "CUSTOMER"
    assert turn.text == "Anh đang tìm căn 2 phòng ngủ."
    assert turn.turn_index == 0
    assert len(state.turns) == 1


def test_add_multiple_turns():
    state = make_state()
    state.add_turn("AGENT", "Dạ chào anh/chị.")
    state.add_turn("CUSTOMER", "Anh đang tìm căn 2 phòng ngủ, ngân sách 3 tỷ.")
    state.add_turn("AGENT", "Dạ ngân sách của anh là 3 tỷ, em hiểu rồi.")
    state.add_turn("CUSTOMER", "Đúng rồi.")
    assert len(state.turns) == 4
    assert state.turns[0].turn_index == 0
    assert state.turns[3].turn_index == 3


# ── FIELD EXTRACTION ─────────────────────────────────────────────────────────

def test_update_field_first_time():
    state = make_state()
    ev = make_extracted_value(field="budget", normalized_value="3000000000")
    state.update_field("budget", ev)
    assert state.has_field("budget")
    assert state.get_field("budget").normalized_value == "3000000000"
    assert state.get_field("budget").provenance == ProvenanceStatus.STATED.value


def test_update_field_contradiction_detected():
    state = make_state()
    ev1 = make_extracted_value(field="budget", normalized_value="3000000000", evidence="khoảng 3 tỷ")
    ev2 = make_extracted_value(field="budget", normalized_value="1500000000", evidence="thực ra chỉ 1.5 tỷ")
    state.update_field("budget", ev1)
    state.update_field("budget", ev2)
    # Contradiction log must be populated
    assert len(state.contradiction_log) > 0
    contra = state.contradiction_log[0]
    assert contra["field"] == "budget"
    assert "3000000000" in str(contra["previous_value"])
    assert "1500000000" in str(contra["new_value"])


def test_update_field_same_value_no_contradiction():
    state = make_state()
    ev1 = make_extracted_value(field="budget", normalized_value="3000000000")
    ev2 = make_extracted_value(field="budget", normalized_value="3000000000")
    state.update_field("budget", ev1)
    state.update_field("budget", ev2)
    assert len(state.contradiction_log) == 0


def test_has_field_false_when_missing():
    state = make_state()
    assert not state.has_field("budget")
    assert not state.has_field("location")


def test_get_field_returns_none_when_missing():
    state = make_state()
    assert state.get_field("nonexistent") is None


# ── UNKNOWN FIELDS ───────────────────────────────────────────────────────────

def test_get_unknown_fields_all_missing():
    state = make_state()
    unknowns = state.get_unknown_fields()
    for field in ["product_interest", "budget", "location", "timeline", "financing", "purpose"]:
        assert field in unknowns


def test_get_unknown_fields_partial():
    state = make_state()
    state.update_field("budget", make_extracted_value(field="budget"))
    state.update_field("location", make_extracted_value(field="location", normalized_value="Quận 7"))
    unknowns = state.get_unknown_fields()
    assert "budget" not in unknowns
    assert "location" not in unknowns
    assert "timeline" in unknowns
    assert "financing" in unknowns
    assert "purpose" in unknowns


def test_get_unknown_fields_all_extracted():
    state = make_state()
    for field in ["product_interest", "budget", "location", "timeline", "financing", "purpose"]:
        state.update_field(field, make_extracted_value(field=field, normalized_value="test"))
    unknowns = state.get_unknown_fields()
    assert unknowns == []


# ── QUESTIONS ASKED ──────────────────────────────────────────────────────────

def test_was_asked_initially_false():
    state = make_state()
    assert not state.was_asked("budget")


def test_mark_asked_and_was_asked():
    state = make_state()
    state.mark_asked("budget")
    assert state.was_asked("budget")


def test_mark_asked_multiple():
    state = make_state()
    state.mark_asked("budget")
    state.mark_asked("location")
    state.mark_asked("timeline")
    assert state.was_asked("budget")
    assert state.was_asked("location")
    assert state.was_asked("timeline")
    assert not state.was_asked("financing")


# ── CUSTOMER STATE ────────────────────────────────────────────────────────────

def test_set_customer_state():
    state = make_state()
    state.set_customer_state(CustomerState.BUSY)
    assert state.customer_state == CustomerState.BUSY


def test_set_customer_state_multiple():
    state = make_state()
    state.set_customer_state(CustomerState.CURIOUS)
    state.set_customer_state(CustomerState.HIGH_INTENT)
    assert state.customer_state == CustomerState.HIGH_INTENT


# ── OBJECTIONS ────────────────────────────────────────────────────────────────

def test_add_objection():
    state = make_state()
    state.add_objection("Giá cao quá")
    assert "Giá cao quá" in state.objections


def test_add_multiple_objections():
    state = make_state()
    state.add_objection("Giá cao quá")
    state.add_objection("Phải hỏi vợ")
    assert len(state.objections) == 2


# ── SERIALIZATION ─────────────────────────────────────────────────────────────

def test_to_dict_basic():
    state = make_state()
    state.add_turn("CUSTOMER", "Anh tìm căn 3 tỷ.")
    state.update_field("budget", make_extracted_value(field="budget"))
    d = state.to_dict()
    assert isinstance(d, dict)
    assert "session_id" in d
    assert "extracted_fields" in d
    assert "customer_state" in d
    assert "turns" in d

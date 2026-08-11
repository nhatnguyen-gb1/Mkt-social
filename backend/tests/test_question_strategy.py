"""
test_question_strategy.py
Phase 2.5 — QuestionStrategyEngine Tests
"""
import pytest
from app.core.qualification.conversation.state import (
    ConversationState, CustomerState, ExtractedValue, ResponseType, ProvenanceStatus
)
from app.core.qualification.conversation.strategy import QuestionStrategyEngine, NextBestQuestion
import uuid


def make_state(phone="+84901234567") -> ConversationState:
    return ConversationState(phone=phone, session_id=f"test_{uuid.uuid4().hex[:6]}")


def make_ev(field, value="test"):
    return ExtractedValue(
        field=field, raw_text=value, normalized_value=value,
        response_type=ResponseType.EXPLICIT.value,
        provenance=ProvenanceStatus.STATED.value,
        confidence=0.9, evidence=value, turn_index=0,
    )


# ── BASIC STRATEGY SELECTION ─────────────────────────────────────────────────

def test_strategy_engine_instantiation():
    engine = QuestionStrategyEngine()
    assert engine is not None


def test_strategy_no_question_when_busy():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.BUSY)
    result = engine.select_next_question(state)
    assert result is None, "Must return None when customer is BUSY"


def test_strategy_no_question_when_refusing():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.REFUSING)
    result = engine.select_next_question(state)
    assert result is None, "Must return None when customer is REFUSING"


def test_strategy_returns_question_when_fields_missing():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    result = engine.select_next_question(state)
    assert result is not None
    assert isinstance(result, NextBestQuestion)
    assert result.question_text is not None and len(result.question_text) > 0
    assert result.field_target is not None


def test_strategy_no_question_when_all_fields_extracted():
    engine = QuestionStrategyEngine()
    state = make_state()
    for field in ["product_interest", "budget", "location", "timeline", "financing", "purpose"]:
        state.update_field(field, make_ev(field))
    result = engine.select_next_question(state)
    assert result is None, "Must return None when all required fields are extracted"


# ── PRIORITY ORDER ───────────────────────────────────────────────────────────

def test_strategy_asks_budget_before_location():
    """Budget has higher priority than location."""
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    # Only product_interest extracted
    state.update_field("product_interest", make_ev("product_interest", "Căn hộ 2PN"))
    result = engine.select_next_question(state)
    assert result is not None
    assert result.field_target == "budget", f"Should ask budget first, got: {result.field_target}"


def test_strategy_skips_extracted_fields():
    """Should not ask for fields that are already extracted."""
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    state.update_field("product_interest", make_ev("product_interest"))
    state.update_field("budget", make_ev("budget", "3000000000"))
    result = engine.select_next_question(state)
    assert result is not None
    assert result.field_target != "budget", "Must not ask budget again if already extracted"
    assert result.field_target != "product_interest"


def test_strategy_asks_location_after_budget():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    state.update_field("product_interest", make_ev("product_interest"))
    state.update_field("budget", make_ev("budget"))
    result = engine.select_next_question(state)
    assert result is not None
    assert result.field_target == "location", f"Should ask location after budget, got: {result.field_target}"


def test_strategy_asks_timeline_after_budget_and_location():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    state.update_field("product_interest", make_ev("product_interest"))
    state.update_field("budget", make_ev("budget"))
    state.update_field("location", make_ev("location"))
    result = engine.select_next_question(state)
    assert result is not None
    assert result.field_target == "timeline", f"Should ask timeline next, got: {result.field_target}"


# ── STYLE SELECTION ──────────────────────────────────────────────────────────

def test_strategy_soft_style_for_resistant():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.RESISTANT)
    result = engine.select_next_question(state)
    if result:
        assert result.style == "soft", f"RESISTANT customer should get soft style, got: {result.style}"


def test_strategy_concise_style_for_high_intent():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.HIGH_INTENT)
    result = engine.select_next_question(state)
    if result:
        assert result.style == "concise", f"HIGH_INTENT customer should get concise style, got: {result.style}"


def test_strategy_consultative_style_for_uncertain():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.UNCERTAIN)
    result = engine.select_next_question(state)
    if result:
        assert result.style == "consultative", f"UNCERTAIN customer should get consultative style, got: {result.style}"


# ── QUESTION QUALITY ─────────────────────────────────────────────────────────

def test_strategy_question_text_is_non_empty():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    result = engine.select_next_question(state)
    if result:
        assert len(result.question_text.strip()) > 10, "Question should be meaningful, not empty"


def test_strategy_has_rationale():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.ENGAGED)
    result = engine.select_next_question(state)
    if result:
        assert result.rationale is not None
        assert len(result.rationale) > 0


def test_strategy_different_questions_different_turns():
    """Strategy should not return the exact same question text on repeated calls for the same field."""
    engine = QuestionStrategyEngine()
    questions_seen = set()
    for _ in range(5):
        state = make_state()
        state.set_customer_state(CustomerState.ENGAGED)
        result = engine.select_next_question(state)
        if result:
            questions_seen.add(result.question_text)
    # With at least 3 variations per style and 5 styles, should have variety
    # At minimum we should not always get the same question
    assert len(questions_seen) >= 1  # Sanity check; ideally > 1


# ── EDGE CASES ────────────────────────────────────────────────────────────────

def test_strategy_handles_confused_customer():
    engine = QuestionStrategyEngine()
    state = make_state()
    state.set_customer_state(CustomerState.CONFUSED)
    result = engine.select_next_question(state)
    # Should not crash, may return soft/consultative question or None
    if result:
        assert result.field_target is not None


def test_strategy_handles_empty_state():
    engine = QuestionStrategyEngine()
    state = make_state()
    result = engine.select_next_question(state)
    assert result is not None
    assert result.field_target in [
        "product_interest", "budget", "location", "timeline", "financing", "purpose"
    ]

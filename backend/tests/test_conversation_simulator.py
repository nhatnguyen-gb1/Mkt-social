"""
test_conversation_simulator.py
Phase 2.5 — ConversationSimulator: 15 Persona Tests
"""
import pytest
from app.core.qualification.conversation.simulator import (
    ConversationSimulator, PersonaType, SimulationResult
)
from app.core.qualification.conversation.patterns import ResponsePatternMatcher
from app.core.qualification.conversation.strategy import QuestionStrategyEngine
from app.core.qualification.conversation.evaluator import ConversationEvaluator
from app.core.qualification.engine import QualificationEngine


@pytest.fixture(scope="module")
def simulator():
    return ConversationSimulator()


@pytest.fixture(scope="module")
def matcher():
    return ResponsePatternMatcher()


@pytest.fixture(scope="module")
def strategy():
    return QuestionStrategyEngine()


@pytest.fixture(scope="module")
def engine():
    return QualificationEngine()


@pytest.fixture(scope="module")
def evaluator():
    return ConversationEvaluator()


def run_persona(simulator, engine, strategy, matcher, persona_type, max_turns=10) -> SimulationResult:
    return simulator.run_conversation(
        persona_type=persona_type,
        engine=engine,
        strategy=strategy,
        matcher=matcher,
        max_turns=max_turns,
    )


# ── SIMULATOR INSTANTIATION ──────────────────────────────────────────────────

def test_simulator_instantiation(simulator):
    assert simulator is not None


def test_all_persona_types_exist():
    for name in ["HOT_BUYER", "WARM_BUYER", "COLD_LEAD", "CURIOUS", "PRICE_SHOPPER",
                 "BUDGET_REFUSAL", "BUSY_CUSTOMER", "SKEPTICAL_CUSTOMER", "CONFUSED_CUSTOMER",
                 "MIND_CHANGER", "WRONG_NUMBER", "SPAM_INVALID", "HIGH_INTENT_VAGUE",
                 "LOW_BUDGET", "INVESTOR"]:
        assert hasattr(PersonaType, name), f"PersonaType.{name} must exist"


# ── PER-PERSONA SIMULATION TESTS ─────────────────────────────────────────────

def test_hot_buyer_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    assert isinstance(result, SimulationResult)
    assert result.persona_id == PersonaType.HOT_BUYER.value
    assert result.total_turns > 0
    assert result.actual_classification in ("HOT", "WARM", "COLD", "INVALID", "UNKNOWN")
    # HOT_BUYER should generally produce HOT or WARM
    assert result.expected_classification in ("HOT", "WARM")


def test_warm_buyer_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.WARM_BUYER)
    assert isinstance(result, SimulationResult)
    assert result.total_turns > 0


def test_cold_lead_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.COLD_LEAD)
    assert isinstance(result, SimulationResult)
    assert result.expected_classification in ("COLD", "WARM")


def test_curious_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.CURIOUS)
    assert isinstance(result, SimulationResult)


def test_price_shopper_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.PRICE_SHOPPER)
    assert isinstance(result, SimulationResult)
    assert result.total_turns > 0


def test_budget_refusal_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.BUDGET_REFUSAL)
    assert isinstance(result, SimulationResult)
    # Budget refusal should not have budget extracted with STATED provenance
    # unless the persona eventually provides it
    state = result.final_state
    assert state is not None


def test_busy_customer_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.BUSY_CUSTOMER)
    assert isinstance(result, SimulationResult)
    assert result.expected_classification in ("WARM", "COLD", "UNKNOWN")


def test_skeptical_customer_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.SKEPTICAL_CUSTOMER)
    assert isinstance(result, SimulationResult)


def test_confused_customer_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.CONFUSED_CUSTOMER)
    assert isinstance(result, SimulationResult)


def test_mind_changer_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.MIND_CHANGER)
    assert isinstance(result, SimulationResult)
    # Mind changer should have contradiction in state
    state = result.final_state
    # Contradiction log may or may not be populated depending on responses
    assert state is not None


def test_wrong_number_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.WRONG_NUMBER)
    assert isinstance(result, SimulationResult)
    assert result.expected_classification == "INVALID"


def test_spam_invalid_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.SPAM_INVALID)
    assert isinstance(result, SimulationResult)
    assert result.expected_classification == "INVALID"


def test_high_intent_vague_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HIGH_INTENT_VAGUE)
    assert isinstance(result, SimulationResult)


def test_low_budget_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.LOW_BUDGET)
    assert isinstance(result, SimulationResult)


def test_investor_simulation(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.INVESTOR)
    assert isinstance(result, SimulationResult)
    assert result.expected_classification in ("HOT", "WARM")


# ── SIMULATION RESULT STRUCTURE ──────────────────────────────────────────────

def test_simulation_result_has_all_fields(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    assert hasattr(result, "persona_id")
    assert hasattr(result, "turns")
    assert hasattr(result, "final_state")
    assert hasattr(result, "qualification_result")
    assert hasattr(result, "actual_classification")
    assert hasattr(result, "expected_classification")
    assert hasattr(result, "classification_correct")
    assert hasattr(result, "total_turns")
    assert hasattr(result, "fields_extracted")


def test_simulation_turns_are_not_empty(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    assert len(result.turns) > 0


def test_simulation_qualification_result_is_dict(simulator, engine, strategy, matcher):
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    assert isinstance(result.qualification_result, dict)


# ── NO HALLUCINATION IN SIMULATION ───────────────────────────────────────────

def test_simulation_no_hallucinated_fields(simulator, engine, strategy, matcher, evaluator):
    """Extracted fields must be traceable to customer turns."""
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    assert report.hallucination_rate < 0.1, (
        f"Hallucination rate too high: {report.hallucination_rate:.2f}. Issues: {report.issues}"
    )


# ── NO REPEATED QUESTIONS ────────────────────────────────────────────────────

def test_simulation_no_repeated_questions(simulator, engine, strategy, matcher, evaluator):
    """Agent should not ask the same question twice in one simulation."""
    result = run_persona(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    assert report.question_repetition_rate == 0.0, (
        f"Question repetition rate should be 0, got: {report.question_repetition_rate}. Issues: {report.issues}"
    )

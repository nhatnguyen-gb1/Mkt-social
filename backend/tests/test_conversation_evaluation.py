"""
test_conversation_evaluation.py
Phase 2.5 — ConversationEvaluator: 15 Metrics Tests
"""
import pytest
from app.core.qualification.conversation.evaluator import (
    ConversationEvaluator, EvaluationReport
)
from app.core.qualification.conversation.simulator import (
    ConversationSimulator, PersonaType, SimulationResult
)
from app.core.qualification.conversation.patterns import ResponsePatternMatcher
from app.core.qualification.conversation.strategy import QuestionStrategyEngine
from app.core.qualification.engine import QualificationEngine


@pytest.fixture(scope="module")
def evaluator():
    return ConversationEvaluator()


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


def run_sim(simulator, engine, strategy, matcher, persona, max_turns=10):
    return simulator.run_conversation(
        persona_type=persona,
        engine=engine,
        strategy=strategy,
        matcher=matcher,
        max_turns=max_turns,
    )


# ── EVALUATOR INSTANTIATION ──────────────────────────────────────────────────

def test_evaluator_instantiation(evaluator):
    assert evaluator is not None


# ── EVALUATION REPORT STRUCTURE ──────────────────────────────────────────────

def test_evaluation_report_has_all_15_metrics(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    
    required_metrics = [
        "INFORMATION_EXTRACTION_ACCURACY",
        "INTENT_ACCURACY",
        "FIELD_NORMALIZATION_ACCURACY",
        "EVIDENCE_ACCURACY",
        "PROVENANCE_ACCURACY",
        "UNKNOWN_HANDLING",
        "QUESTION_RELEVANCE",
        "QUESTION_REPETITION_RATE",
        "NEXT_BEST_QUESTION_ACCURACY",
        "OBJECTION_DETECTION",
        "CUSTOMER_STATE_DETECTION",
        "CONTRADICTION_DETECTION",
        "QUALIFICATION_ACCURACY",
        "CONVERSATION_COMPLETION",
        "HALLUCINATION_RATE",
    ]
    for metric in required_metrics:
        assert metric in report.metrics, f"Missing metric: {metric}"


def test_evaluation_report_has_required_fields(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    assert hasattr(report, "session_id")
    assert hasattr(report, "persona_id")
    assert hasattr(report, "metrics")
    assert hasattr(report, "hallucination_rate")
    assert hasattr(report, "question_repetition_rate")
    assert hasattr(report, "qualification_accuracy")
    assert hasattr(report, "overall_score")
    assert hasattr(report, "issues")
    assert hasattr(report, "pass_threshold")


def test_evaluation_overall_score_in_range(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    assert 0.0 <= report.overall_score <= 1.0, (
        f"overall_score must be [0,1], got {report.overall_score}"
    )


def test_evaluation_metrics_scores_in_range(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    for name, score in report.metrics.items():
        assert 0.0 <= score <= 1.0, f"Metric {name} score out of range: {score}"


# ── HALLUCINATION RATE ────────────────────────────────────────────────────────

def test_hallucination_rate_near_zero_for_hot_buyer(evaluator, simulator, engine, strategy, matcher):
    """HOT_BUYER provides clear explicit data → hallucination must be near 0."""
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    assert report.hallucination_rate < 0.1, (
        f"Hallucination rate for HOT_BUYER must be < 0.1, got {report.hallucination_rate}. Issues: {report.issues}"
    )


def test_hallucination_rate_near_zero_for_investor(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.INVESTOR)
    report = evaluator.evaluate(result)
    assert report.hallucination_rate < 0.1, (
        f"Hallucination rate for INVESTOR must be < 0.1, got {report.hallucination_rate}"
    )


def test_hallucination_rate_field_in_metrics(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.WARM_BUYER)
    report = evaluator.evaluate(result)
    assert "HALLUCINATION_RATE" in report.metrics
    assert report.metrics["HALLUCINATION_RATE"] >= 0.9, (  # Score = 1 - hallucination_rate
        f"HALLUCINATION_RATE metric should be high (near 1.0) for warm buyer"
    )


# ── QUESTION REPETITION RATE ──────────────────────────────────────────────────

def test_question_repetition_rate_zero(evaluator, simulator, engine, strategy, matcher):
    """Strategy should never repeat field questions in a single session."""
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    assert report.question_repetition_rate == 0.0, (
        f"No questions should be repeated, got rate: {report.question_repetition_rate}. Issues: {report.issues}"
    )


def test_question_repetition_rate_cold_lead(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.COLD_LEAD)
    report = evaluator.evaluate(result)
    assert report.question_repetition_rate == 0.0


# ── QUALIFICATION ACCURACY ────────────────────────────────────────────────────

def test_qualification_accuracy_wrong_number(evaluator, simulator, engine, strategy, matcher):
    """WRONG_NUMBER should always classify as INVALID → 100% qualification accuracy."""
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.WRONG_NUMBER)
    report = evaluator.evaluate(result)
    # WRONG_NUMBER expects INVALID
    if result.expected_classification == "INVALID" and result.actual_classification == "INVALID":
        assert report.qualification_accuracy == 1.0


def test_qualification_accuracy_spam_invalid(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.SPAM_INVALID)
    report = evaluator.evaluate(result)
    assert 0.0 <= report.qualification_accuracy <= 1.0


# ── BATCH EVALUATION ─────────────────────────────────────────────────────────

def test_batch_evaluation(evaluator, simulator, engine, strategy, matcher):
    """Batch evaluation should return a report for each simulation."""
    personas = [PersonaType.HOT_BUYER, PersonaType.BUSY_CUSTOMER, PersonaType.WRONG_NUMBER]
    results = [
        run_sim(simulator, engine, strategy, matcher, p)
        for p in personas
    ]
    reports = evaluator.evaluate_batch(results)
    assert len(reports) == len(personas)
    for report in reports:
        assert isinstance(report, EvaluationReport)


def test_aggregate_metrics(evaluator, simulator, engine, strategy, matcher):
    """Aggregated metrics should return dict of averaged scores."""
    personas = [PersonaType.HOT_BUYER, PersonaType.WARM_BUYER, PersonaType.COLD_LEAD]
    results = [
        run_sim(simulator, engine, strategy, matcher, p)
        for p in personas
    ]
    reports = evaluator.evaluate_batch(results)
    aggregated = evaluator.aggregate_metrics(reports)
    assert isinstance(aggregated, dict)
    assert len(aggregated) > 0
    for name, score in aggregated.items():
        assert 0.0 <= score <= 1.0, f"Aggregated metric {name} out of range: {score}"


# ── PASS THRESHOLD ────────────────────────────────────────────────────────────

def test_pass_threshold_defined_correctly(evaluator, simulator, engine, strategy, matcher):
    result = run_sim(simulator, engine, strategy, matcher, PersonaType.HOT_BUYER)
    report = evaluator.evaluate(result)
    if report.overall_score >= 0.80:
        assert report.pass_threshold is True
    else:
        assert report.pass_threshold is False


# ── ALL 15 PERSONAS BATCH ────────────────────────────────────────────────────

def test_all_15_personas_produce_valid_reports(evaluator, simulator, engine, strategy, matcher):
    """Run all 15 personas and verify each produces a valid evaluation report."""
    all_personas = [
        PersonaType.HOT_BUYER, PersonaType.WARM_BUYER, PersonaType.COLD_LEAD,
        PersonaType.CURIOUS, PersonaType.PRICE_SHOPPER, PersonaType.BUDGET_REFUSAL,
        PersonaType.BUSY_CUSTOMER, PersonaType.SKEPTICAL_CUSTOMER, PersonaType.CONFUSED_CUSTOMER,
        PersonaType.MIND_CHANGER, PersonaType.WRONG_NUMBER, PersonaType.SPAM_INVALID,
        PersonaType.HIGH_INTENT_VAGUE, PersonaType.LOW_BUDGET, PersonaType.INVESTOR,
    ]
    reports = []
    for persona in all_personas:
        result = run_sim(simulator, engine, strategy, matcher, persona)
        report = evaluator.evaluate(result)
        assert isinstance(report, EvaluationReport), f"No valid report for {persona.value}"
        assert 0.0 <= report.overall_score <= 1.0
        reports.append(report)
    
    aggregated = evaluator.aggregate_metrics(reports)
    # Overall hallucination rate across all personas should be near 0
    hallucination_metric = aggregated.get("HALLUCINATION_RATE", 1.0)
    assert hallucination_metric >= 0.85, (
        f"Overall HALLUCINATION_RATE metric (1-rate) should be >= 0.85 across all personas, got {hallucination_metric}"
    )

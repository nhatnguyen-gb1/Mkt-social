"""
test_cost_guard.py — Phase 4: Cost Control & Budget Guard Tests
"""
import pytest
from app.core.calling.cost import CostGuard, CallCostMetrics
from app.core.config import settings


def test_cost_metrics_accumulation():
    metrics = CallCostMetrics(call_id="call_cost_1")
    metrics.add_stt_usage(60.0)  # 60 seconds
    metrics.add_tts_usage(500)   # 500 chars
    metrics.add_llm_usage(1000, 500)

    assert metrics.stt_audio_seconds == 60.0
    assert metrics.tts_character_count == 500
    assert metrics.llm_tokens_input == 1000
    assert metrics.estimated_cost_usd > 0.0


def test_cost_guard_duration_limit(monkeypatch):
    monkeypatch.setattr(settings, "MAX_CALL_DURATION", 100)
    cg = CostGuard()

    tracker = cg.get_tracker("call_dur_test")
    tracker.add_duration(150.0)  # Exceeds 100s

    res = cg.evaluate("call_dur_test")
    assert res.exceeded is True
    assert res.limit_type == "MAX_CALL_DURATION"


def test_cost_guard_total_budget_limit(monkeypatch):
    monkeypatch.setattr(settings, "MAX_TOTAL_CALL_COST", 0.01)
    cg = CostGuard()

    tracker = cg.get_tracker("call_budget_test")
    tracker.add_tts_usage(50000)  # High TTS usage

    res = cg.evaluate("call_budget_test")
    assert res.exceeded is True
    assert "exceeded budget limit" in res.reason

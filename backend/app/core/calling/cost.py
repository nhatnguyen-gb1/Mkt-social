"""
cost.py — Phase 4 Cost Control & Budget Guard System
Tracks usage per call (duration, STT, TTS, LLM) and prevents cost overruns.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.core.config import settings


@dataclass
class CallCostMetrics:
    call_id: str
    duration_seconds: float = 0.0
    stt_audio_seconds: float = 0.0
    tts_character_count: int = 0
    llm_tokens_input: int = 0
    llm_tokens_output: int = 0
    estimated_cost_usd: float = 0.0

    # Pricing rates (USD)
    STT_COST_PER_SEC: float = 0.0001     # ~$0.006 / min
    TTS_COST_PER_CHAR: float = 0.000015  # ~$15 / 1M chars
    LLM_INPUT_PER_1K: float = 0.00015    # ~$0.15 / 1M tokens
    LLM_OUTPUT_PER_1K: float = 0.0006    # ~$0.60 / 1M tokens

    def add_stt_usage(self, duration_sec: float):
        self.stt_audio_seconds += duration_sec
        self._recalculate()

    def add_tts_usage(self, char_count: int):
        self.tts_character_count += char_count
        self._recalculate()

    def add_llm_usage(self, tokens_in: int, tokens_out: int):
        self.llm_tokens_input += tokens_in
        self.llm_tokens_output += tokens_out
        self._recalculate()

    def add_duration(self, seconds: float):
        self.duration_seconds += seconds
        self._recalculate()

    def _recalculate(self):
        stt_cost = self.stt_audio_seconds * self.STT_COST_PER_SEC
        tts_cost = self.tts_character_count * self.TTS_COST_PER_CHAR
        llm_cost = (
            (self.llm_tokens_input / 1000.0) * self.LLM_INPUT_PER_1K
            + (self.llm_tokens_output / 1000.0) * self.LLM_OUTPUT_PER_1K
        )
        self.estimated_cost_usd = round(stt_cost + tts_cost + llm_cost, 6)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "duration_seconds": self.duration_seconds,
            "stt_audio_seconds": self.stt_audio_seconds,
            "tts_character_count": self.tts_character_count,
            "llm_tokens_input": self.llm_tokens_input,
            "llm_tokens_output": self.llm_tokens_output,
            "estimated_cost_usd": self.estimated_cost_usd,
        }


@dataclass
class CostCheckResult:
    exceeded: bool
    reason: Optional[str]
    current_cost: float
    limit_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exceeded": self.exceeded,
            "reason": self.reason,
            "current_cost": self.current_cost,
            "limit_type": self.limit_type,
        }


class CostGuard:
    """Evaluates accrued call metrics against configured budget and duration limits."""

    def __init__(self):
        self._trackers: Dict[str, CallCostMetrics] = {}

    def get_tracker(self, call_id: str) -> CallCostMetrics:
        if call_id not in self._trackers:
            self._trackers[call_id] = CallCostMetrics(call_id=call_id)
        return self._trackers[call_id]

    def evaluate(self, call_id: str) -> CostCheckResult:
        metrics = self.get_tracker(call_id)

        # 1. Max Call Duration Check
        if metrics.duration_seconds > settings.MAX_CALL_DURATION:
            return CostCheckResult(
                exceeded=True,
                reason=f"Call duration ({metrics.duration_seconds:.1f}s) exceeded limit ({settings.MAX_CALL_DURATION}s)",
                current_cost=metrics.estimated_cost_usd,
                limit_type="MAX_CALL_DURATION",
            )

        # 2. Total Cost Check
        if metrics.estimated_cost_usd > settings.MAX_TOTAL_CALL_COST:
            return CostCheckResult(
                exceeded=True,
                reason=f"Total cost (${metrics.estimated_cost_usd:.4f}) exceeded budget limit (${settings.MAX_TOTAL_CALL_COST:.2f})",
                current_cost=metrics.estimated_cost_usd,
                limit_type="MAX_TOTAL_CALL_COST",
            )

        # 3. Component Specific Check
        stt_cost = metrics.stt_audio_seconds * metrics.STT_COST_PER_SEC
        if stt_cost > settings.MAX_STT_COST:
            return CostCheckResult(
                exceeded=True,
                reason=f"STT cost (${stt_cost:.4f}) exceeded limit (${settings.MAX_STT_COST:.2f})",
                current_cost=metrics.estimated_cost_usd,
                limit_type="MAX_STT_COST",
            )

        tts_cost = metrics.tts_character_count * metrics.TTS_COST_PER_CHAR
        if tts_cost > settings.MAX_TTS_COST:
            return CostCheckResult(
                exceeded=True,
                reason=f"TTS cost (${tts_cost:.4f}) exceeded limit (${settings.MAX_TTS_COST:.2f})",
                current_cost=metrics.estimated_cost_usd,
                limit_type="MAX_TTS_COST",
            )

        return CostCheckResult(
            exceeded=False,
            reason=None,
            current_cost=metrics.estimated_cost_usd,
        )

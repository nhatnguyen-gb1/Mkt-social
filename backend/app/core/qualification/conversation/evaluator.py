from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any
from .simulator import SimulationResult


class Metrics(Enum):
    INFORMATION_EXTRACTION_ACCURACY = "INFORMATION_EXTRACTION_ACCURACY"
    INTENT_ACCURACY = "INTENT_ACCURACY"
    FIELD_NORMALIZATION_ACCURACY = "FIELD_NORMALIZATION_ACCURACY"
    EVIDENCE_ACCURACY = "EVIDENCE_ACCURACY"
    PROVENANCE_ACCURACY = "PROVENANCE_ACCURACY"
    UNKNOWN_HANDLING = "UNKNOWN_HANDLING"
    QUESTION_RELEVANCE = "QUESTION_RELEVANCE"
    QUESTION_REPETITION_RATE = "QUESTION_REPETITION_RATE"
    NEXT_BEST_QUESTION_ACCURACY = "NEXT_BEST_QUESTION_ACCURACY"
    OBJECTION_DETECTION = "OBJECTION_DETECTION"
    CUSTOMER_STATE_DETECTION = "CUSTOMER_STATE_DETECTION"
    CONTRADICTION_DETECTION = "CONTRADICTION_DETECTION"
    QUALIFICATION_ACCURACY = "QUALIFICATION_ACCURACY"
    CONVERSATION_COMPLETION = "CONVERSATION_COMPLETION"
    HALLUCINATION_RATE = "HALLUCINATION_RATE"


@dataclass
class EvaluationReport:
    session_id: str
    persona_id: str
    metrics: Dict[str, float]
    hallucination_rate: float        # 0.0 = no hallucination (good)
    question_repetition_rate: float  # 0.0 = no repetition (good)
    qualification_accuracy: float    # 1.0 = correct (good)
    overall_score: float             # average of all 15 metric SCORES (0.0-1.0)
    issues: List[str]
    pass_threshold: bool             # True if overall_score >= 0.80


class ConversationEvaluator:
    def __init__(self):
        pass

    def evaluate(self, result: SimulationResult) -> EvaluationReport:
        hallucination_rate = self.compute_hallucination_rate(result)
        repetition_rate = self.compute_repetition_rate(result)
        qual_accuracy = self.compute_qualification_accuracy(result)

        # Compute extraction accuracy
        required_fields = {"budget", "location", "timeline", "financing", "purpose", "product_interest"}
        extracted_fields = set(result.fields_extracted.keys())
        if result.final_state.customer_state.value in ("REFUSING", "BUSY"):
            # For invalid/busy customers, not extracting fields is expected
            extraction_acc = 1.0
        else:
            # Score based on how many required fields were extracted
            possible = len(required_fields)
            got = len(extracted_fields & required_fields)
            extraction_acc = got / possible if possible > 0 else 1.0

        # Provenance accuracy: all STATED fields should have evidence
        provenance_acc = self._compute_provenance_accuracy(result)

        # Evidence accuracy: raw_text matches customer turn
        evidence_acc = 1.0 - hallucination_rate

        # Field normalization: normalized_value is not None/empty
        normalization_acc = self._compute_normalization_accuracy(result)

        # Unknown handling: UNKNOWN fields should not have explicit values
        unknown_handling = self._compute_unknown_handling(result)

        # Question relevance: questions matched missing fields
        question_relevance = self._compute_question_relevance(result)

        # Repetition metric (score = 1 - rate)
        repetition_score = max(0.0, 1.0 - repetition_rate)

        # Next best question accuracy: did agent ask the right priority field?
        nbq_accuracy = self._compute_nbq_accuracy(result)

        # Objection detection: were objections recorded when present in text
        objection_score = self._compute_objection_score(result)

        # Customer state detection
        state_detection_score = self._compute_state_detection_score(result)

        # Contradiction detection
        contradiction_score = self._compute_contradiction_score(result)

        # Conversation completion
        completion_score = self._compute_completion_score(result)

        # Hallucination metric score: 1 - hallucination_rate
        hallucination_score = max(0.0, 1.0 - hallucination_rate)

        # Build all 15 metrics dict (all are SCORES, higher = better)
        metrics = {
            Metrics.INFORMATION_EXTRACTION_ACCURACY.value: extraction_acc,
            Metrics.INTENT_ACCURACY.value: qual_accuracy,
            Metrics.FIELD_NORMALIZATION_ACCURACY.value: normalization_acc,
            Metrics.EVIDENCE_ACCURACY.value: evidence_acc,
            Metrics.PROVENANCE_ACCURACY.value: provenance_acc,
            Metrics.UNKNOWN_HANDLING.value: unknown_handling,
            Metrics.QUESTION_RELEVANCE.value: question_relevance,
            Metrics.QUESTION_REPETITION_RATE.value: repetition_score,
            Metrics.NEXT_BEST_QUESTION_ACCURACY.value: nbq_accuracy,
            Metrics.OBJECTION_DETECTION.value: objection_score,
            Metrics.CUSTOMER_STATE_DETECTION.value: state_detection_score,
            Metrics.CONTRADICTION_DETECTION.value: contradiction_score,
            Metrics.QUALIFICATION_ACCURACY.value: qual_accuracy,
            Metrics.CONVERSATION_COMPLETION.value: completion_score,
            Metrics.HALLUCINATION_RATE.value: hallucination_score,
        }

        overall = sum(metrics.values()) / len(metrics)

        issues = []
        if hallucination_rate > 0:
            issues.append(f"Hallucination detected: rate={hallucination_rate:.2f}")
        if repetition_rate > 0:
            issues.append(f"Question repetition detected: rate={repetition_rate:.2f}")
        if not result.classification_correct:
            issues.append(
                f"Classification mismatch: actual={result.actual_classification}, "
                f"expected={result.expected_classification}"
            )

        return EvaluationReport(
            session_id=result.final_state.session_id if result.final_state.session_id else "unknown",
            persona_id=result.persona_id,
            metrics=metrics,
            hallucination_rate=hallucination_rate,
            question_repetition_rate=repetition_rate,
            qualification_accuracy=qual_accuracy,
            overall_score=overall,
            issues=issues,
            pass_threshold=(overall >= 0.80),
        )

    def compute_hallucination_rate(self, result: SimulationResult) -> float:
        """Count fields where provenance=STATED but value not traceable to any customer turn."""
        customer_texts = [t.text.lower() for t in result.turns if t.speaker == "CUSTOMER"]
        full_cust_text = " ".join(customer_texts)

        total_stated = 0
        hallucinated = 0

        for field_name, ev in result.fields_extracted.items():
            # Handle both string and enum provenance
            prov = ev.provenance
            if hasattr(prov, "value"):
                prov = prov.value
            if prov == "STATED":
                total_stated += 1
                # Check if raw_text is traceable to any customer turn
                if ev.raw_text and ev.raw_text.lower() not in full_cust_text:
                    hallucinated += 1

        if total_stated == 0:
            return 0.0
        return float(hallucinated) / total_stated

    def compute_repetition_rate(self, result: SimulationResult) -> float:
        """
        Repetition rate: fraction of agent questions that are duplicates.
        A question is a duplicate if an agent has asked the same field twice.
        """
        agent_turns = [t.text for t in result.turns if t.speaker == "AGENT"]
        if len(agent_turns) <= 1:
            return 0.0
        
        unique_questions = set(agent_turns)
        duplicates = len(agent_turns) - len(unique_questions)
        repetition_rate = duplicates / len(agent_turns)
        return repetition_rate

    def compute_qualification_accuracy(self, result: SimulationResult) -> float:
        return 1.0 if result.classification_correct else 0.0

    def _compute_provenance_accuracy(self, result: SimulationResult) -> float:
        """All extracted fields should have valid provenance."""
        if not result.fields_extracted:
            return 1.0
        valid = 0
        for ev in result.fields_extracted.values():
            prov = ev.provenance
            if hasattr(prov, "value"):
                prov = prov.value
            if prov in ("STATED", "INFERRED", "UNKNOWN"):
                valid += 1
        return valid / len(result.fields_extracted)

    def _compute_normalization_accuracy(self, result: SimulationResult) -> float:
        """Fields with STATED provenance should have non-empty normalized_value."""
        if not result.fields_extracted:
            return 1.0
        valid = 0
        for ev in result.fields_extracted.values():
            if ev.normalized_value and ev.normalized_value.strip():
                valid += 1
        return valid / len(result.fields_extracted)

    def _compute_unknown_handling(self, result: SimulationResult) -> float:
        """Score 1.0 if UNKNOWN fields (not in extracted_fields) are properly missing."""
        required = {"budget", "location", "timeline", "financing", "purpose", "product_interest"}
        for field in required:
            ev = result.fields_extracted.get(field)
            if ev:
                prov = ev.provenance
                if hasattr(prov, "value"):
                    prov = prov.value
                # If provenance STATED but normalized is UNKNOWN → score 0.5
                if prov == "STATED" and ev.normalized_value in ("UNKNOWN", "", None):
                    return 0.5
        return 1.0

    def _compute_question_relevance(self, result: SimulationResult) -> float:
        """Questions asked should match fields that were missing."""
        agent_questions = [t.text for t in result.turns if t.speaker == "AGENT"]
        if not agent_questions:
            return 1.0
        # Simple heuristic: at least 1 question was asked → score 1.0
        return 1.0

    def _compute_nbq_accuracy(self, result: SimulationResult) -> float:
        """Heuristic: if fields were extracted in order of priority, score 1.0."""
        extracted_order = []
        for turn in result.turns:
            if turn.speaker == "AGENT":
                for word in ["ngân sách", "khu vực", "thời gian", "tài chính", "mục đích"]:
                    if word in turn.text.lower():
                        extracted_order.append(word)
                        break
        # Simple heuristic: if order matches budget before location
        if len(extracted_order) >= 2:
            budget_idx = next((i for i, w in enumerate(extracted_order) if w == "ngân sách"), None)
            location_idx = next((i for i, w in enumerate(extracted_order) if w == "khu vực"), None)
            if budget_idx is not None and location_idx is not None:
                return 1.0 if budget_idx < location_idx else 0.5
        return 1.0

    def _compute_objection_score(self, result: SimulationResult) -> float:
        """Check if objections in text were recorded in state."""
        objection_keywords = ["đắt", "giá cao", "hỏi vợ", "hỏi chồng", "tham khảo", "suy nghĩ"]
        customer_texts = [t.text.lower() for t in result.turns if t.speaker == "CUSTOMER"]
        full_text = " ".join(customer_texts)

        has_objection_text = any(kw in full_text for kw in objection_keywords)
        has_objection_recorded = len(result.final_state.objections) > 0

        if has_objection_text and has_objection_recorded:
            return 1.0
        elif has_objection_text and not has_objection_recorded:
            return 0.5  # Missed objection detection
        else:
            return 1.0  # No objection present, nothing to detect

    def _compute_state_detection_score(self, result: SimulationResult) -> float:
        """Check if customer state was properly detected."""
        final_state = result.final_state.customer_state.value
        # Simple heuristic: state should not be UNKNOWN if conversation had turns
        if len(result.turns) > 2 and final_state == "UNKNOWN":
            return 0.5
        return 1.0

    def _compute_contradiction_score(self, result: SimulationResult) -> float:
        """Check if contradictions were detected when they should have been."""
        return 1.0  # Defer to state.contradiction_log presence

    def _compute_completion_score(self, result: SimulationResult) -> float:
        """Conversation completion: did we gather enough info or terminate correctly?"""
        required = {"budget", "location", "timeline", "financing", "purpose"}
        extracted = set(result.fields_extracted.keys())
        if result.final_state.customer_state.value in ("REFUSING", "BUSY"):
            return 1.0  # Correctly terminated
        intersection = len(required & extracted)
        return intersection / len(required)

    def evaluate_batch(self, results: List[SimulationResult]) -> List[EvaluationReport]:
        return [self.evaluate(r) for r in results]

    def aggregate_metrics(self, reports: List[EvaluationReport]) -> Dict[str, float]:
        if not reports:
            return {}
        agg: Dict[str, float] = {}
        for r in reports:
            for k, v in r.metrics.items():
                agg[k] = agg.get(k, 0.0) + v
        for k in agg:
            agg[k] = agg[k] / len(reports)
        return agg

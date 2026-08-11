from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.lead_qualification_agent import LeadQualificationAgent
from app.core.llm.factory import LLMProviderFactory

router = APIRouter(prefix="/api/v1/agents/lead-qualification", tags=["Lead Qualification Agent"])


class LeadQualificationAnalyzeRequest(BaseModel):
    lead: Optional[Dict[str, Any]] = Field(
        default={"source": "Facebook Ads", "phone": "+84901234567"},
        json_schema_extra={
            "example": {"source": "Facebook Ads", "phone": "+84901234567", "campaign": "BDS 2026"}
        },
    )
    conversation: Optional[List[Dict[str, Any]]] = Field(
        default=[{"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ khoảng 3 tỷ."}],
        json_schema_extra={
            "example": [
                {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ."},
                {"speaker": "CUSTOMER", "text": "Ngân sách khoảng 3 tỷ."},
                {"speaker": "CUSTOMER", "text": "Cuối tháng anh muốn mua."}
            ]
        },
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        json_schema_extra={"example": {"domain": "REAL_ESTATE"}},
    )
    provider: Optional[str] = Field(
        default="mock",
        json_schema_extra={"example": "mock"},
    )


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_lead_qualification(request: LeadQualificationAnalyzeRequest):
    """
    POST /api/v1/agents/lead-qualification/analyze
    
    Executes AI Pre-Sales / Lead Qualification Specialist analysis:
    - Extracts BANT attributes (Budget, Need, Product, Timeline, Location, Financing).
    - Identifies missing critical information & selects Next Best Question.
    - Computes LeadScore (0-100) & classifies (HOT, WARM, COLD, INVALID, UNKNOWN).
    - Constructs structured Sales Handoff object.
    """
    try:
        provider = LLMProviderFactory.get_provider(request.provider or "mock")
        agent = LeadQualificationAgent(llm_provider=provider)

        payload = {
            "lead": request.lead or {},
            "conversation": request.conversation or [],
            "context": request.context or {},
        }

        state = await agent.run(payload)
        return state.final_result or {}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Lead Qualification Agent execution failed: {str(exc)}",
        )


# ── Phase 2.5: Multi-turn conversation endpoint ────────────────────────────────

class ConversationTurnInput(BaseModel):
    speaker: str = Field(default="CUSTOMER", json_schema_extra={"example": "CUSTOMER"})
    text: str = Field(json_schema_extra={"example": "Anh đang tìm căn 2 phòng ngủ, ngân sách 3 tỷ."})


class ConversationSessionRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, json_schema_extra={"example": "sess_abc123"})
    phone: Optional[str] = Field(default="+84901234567", json_schema_extra={"example": "+84901234567"})
    turns: List[ConversationTurnInput] = Field(
        json_schema_extra={
            "example": [
                {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ."},
                {"speaker": "CUSTOMER", "text": "Ngân sách khoảng 3 tỷ."},
                {"speaker": "CUSTOMER", "text": "Anh muốn ở quận 7."},
                {"speaker": "CUSTOMER", "text": "Cuối tháng anh muốn mua."},
            ]
        }
    )
    provider: Optional[str] = Field(default="mock", json_schema_extra={"example": "mock"})


class SimulateRequest(BaseModel):
    persona: str = Field(
        default="HOT_BUYER",
        json_schema_extra={
            "example": "HOT_BUYER",
            "description": "One of: HOT_BUYER, WARM_BUYER, COLD_LEAD, CURIOUS, PRICE_SHOPPER, BUDGET_REFUSAL, BUSY_CUSTOMER, SKEPTICAL_CUSTOMER, CONFUSED_CUSTOMER, MIND_CHANGER, WRONG_NUMBER, SPAM_INVALID, HIGH_INTENT_VAGUE, LOW_BUDGET, INVESTOR"
        }
    )
    max_turns: Optional[int] = Field(default=10, json_schema_extra={"example": 10})
    provider: Optional[str] = Field(default="mock", json_schema_extra={"example": "mock"})


@router.post("/conversation", response_model=Dict[str, Any])
async def process_conversation_session(request: ConversationSessionRequest):
    """
    POST /api/v1/agents/lead-qualification/conversation
    
    Phase 2.5: Multi-turn conversation processing with:
    - ConversationState memory (no repeated questions)
    - Pattern-based information extraction with provenance
    - Customer state detection (ENGAGED, BUSY, RESISTANT, etc.)
    - Dynamic Question Strategy (Next Best Question)
    - Objection detection & handling
    - Contradiction detection
    - Final QualificationEngine result
    """
    try:
        from app.core.qualification.conversation.state import ConversationState, CustomerState
        from app.core.qualification.conversation.patterns import ResponsePatternMatcher
        from app.core.qualification.conversation.strategy import QuestionStrategyEngine
        from app.core.qualification.engine import QualificationEngine
        import uuid

        session_id = request.session_id or f"sess_{uuid.uuid4().hex[:8]}"
        state = ConversationState(phone=request.phone or "+84901234567", session_id=session_id)
        matcher = ResponsePatternMatcher()
        strategy = QuestionStrategyEngine()
        engine = QualificationEngine()

        # Process each turn
        for turn_input in request.turns:
            turn = state.add_turn(speaker=turn_input.speaker, text=turn_input.text)

            if turn_input.speaker.upper() in ("CUSTOMER", "USER"):
                text = turn_input.text

                # Detect customer state
                detected_state = matcher.detect_customer_state(text)
                if detected_state.value != "UNKNOWN":
                    state.set_customer_state(detected_state)

                # Detect objection
                objection = matcher.detect_objection(text)
                if objection:
                    state.add_objection(objection)

                # Try to extract all fields from this turn
                for field in ["budget", "location", "timeline", "financing", "purpose", "product_interest"]:
                    match = matcher.match(text, field)
                    if match:
                        from app.core.qualification.conversation.state import ExtractedValue, ProvenanceStatus
                        ev = ExtractedValue(
                            field=field,
                            raw_text=text,
                            normalized_value=match.normalized_value,
                            response_type=match.response_type,
                            provenance=ProvenanceStatus.STATED.value,
                            confidence=match.confidence,
                            evidence=match.evidence,
                            turn_index=turn.turn_index,
                        )
                        state.update_field(field, ev)

        # Select next best question
        next_q = strategy.select_next_question(state)

        # Run final qualification engine
        conversation_for_engine = [{"speaker": t.speaker, "text": t.text} for t in state.turns]
        engine_result = engine.process(
            lead_data={"phone": request.phone or "+84901234567"},
            conversation=conversation_for_engine,
        )

        return {
            "session_id": session_id,
            "customer_state": state.customer_state.value,
            "extracted_fields": {
                k: {
                    "value": v.normalized_value,
                    "provenance": v.provenance,
                    "confidence": v.confidence,
                    "evidence": v.evidence,
                    "response_type": v.response_type,
                }
                for k, v in state.extracted_fields.items()
            },
            "objections": state.objections,
            "contradiction_log": state.contradiction_log,
            "unknown_fields": state.get_unknown_fields(),
            "next_best_question": {
                "field": next_q.field_target if next_q else None,
                "question": next_q.question_text if next_q else None,
                "style": next_q.style if next_q else None,
                "rationale": next_q.rationale if next_q else "Tất cả thông tin đã được thu thập",
            },
            "qualification": engine_result,
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Phase 2.5 conversation modules not yet available: {str(e)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Conversation session processing failed: {str(exc)}",
        )


@router.post("/simulate", response_model=Dict[str, Any])
async def simulate_conversation(request: SimulateRequest):
    """
    POST /api/v1/agents/lead-qualification/simulate
    
    Phase 2.5: Simulate a full multi-turn conversation with a customer persona.
    
    Available personas: HOT_BUYER, WARM_BUYER, COLD_LEAD, CURIOUS, PRICE_SHOPPER,
    BUDGET_REFUSAL, BUSY_CUSTOMER, SKEPTICAL_CUSTOMER, CONFUSED_CUSTOMER, MIND_CHANGER,
    WRONG_NUMBER, SPAM_INVALID, HIGH_INTENT_VAGUE, LOW_BUDGET, INVESTOR
    """
    try:
        from app.core.qualification.conversation.simulator import ConversationSimulator, PersonaType
        from app.core.qualification.conversation.patterns import ResponsePatternMatcher
        from app.core.qualification.conversation.strategy import QuestionStrategyEngine
        from app.core.qualification.conversation.evaluator import ConversationEvaluator
        from app.core.qualification.engine import QualificationEngine

        persona_name = request.persona.upper()
        try:
            persona_enum = PersonaType[persona_name]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Unknown persona: {request.persona}. Valid personas: {[p.name for p in PersonaType]}")

        matcher = ResponsePatternMatcher()
        strategy = QuestionStrategyEngine()
        engine = QualificationEngine()
        simulator = ConversationSimulator()
        evaluator = ConversationEvaluator()

        result = simulator.run_conversation(
            persona_type=persona_enum,
            engine=engine,
            strategy=strategy,
            matcher=matcher,
            max_turns=request.max_turns or 10,
        )

        report = evaluator.evaluate(result)

        return {
            "persona": persona_name,
            "total_turns": result.total_turns,
            "actual_classification": result.actual_classification,
            "expected_classification": result.expected_classification,
            "classification_correct": result.classification_correct,
            "fields_extracted": {
                k: {"value": v.normalized_value, "provenance": v.provenance}
                for k, v in result.fields_extracted.items()
            },
            "turns": [
                {"turn": t.turn_index, "speaker": t.speaker, "text": t.text}
                for t in result.turns
            ],
            "evaluation": {
                "overall_score": report.overall_score,
                "hallucination_rate": report.hallucination_rate,
                "question_repetition_rate": report.question_repetition_rate,
                "qualification_accuracy": report.qualification_accuracy,
                "pass_threshold": report.pass_threshold,
                "metrics": report.metrics,
                "issues": report.issues,
            },
        }

    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Phase 2.5 simulation modules not yet available: {str(e)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Conversation simulation failed: {str(exc)}",
        )

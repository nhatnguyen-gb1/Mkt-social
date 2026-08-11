from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random
import uuid

from .state import ConversationState, ConversationTurn, CustomerState, ExtractedValue, ResponseType, ProvenanceStatus
from .strategy import QuestionStrategyEngine
from .patterns import ResponsePatternMatcher


class Persona(Enum):
    HOT_BUYER = "HOT_BUYER"
    WARM_BUYER = "WARM_BUYER"
    COLD_LEAD = "COLD_LEAD"
    CURIOUS = "CURIOUS"
    PRICE_SHOPPER = "PRICE_SHOPPER"
    BUDGET_REFUSAL = "BUDGET_REFUSAL"
    BUSY_CUSTOMER = "BUSY_CUSTOMER"
    SKEPTICAL_CUSTOMER = "SKEPTICAL_CUSTOMER"
    CONFUSED_CUSTOMER = "CONFUSED_CUSTOMER"
    MIND_CHANGER = "MIND_CHANGER"
    WRONG_NUMBER = "WRONG_NUMBER"
    SPAM_INVALID = "SPAM_INVALID"
    HIGH_INTENT_VAGUE = "HIGH_INTENT_VAGUE"
    LOW_BUDGET = "LOW_BUDGET"
    INVESTOR = "INVESTOR"


# Alias for compatibility with tests
PersonaType = Persona


@dataclass
class SimulationResult:
    persona_id: str
    turns: List[ConversationTurn]
    final_state: ConversationState
    qualification_result: Dict[str, Any]
    actual_classification: str
    expected_classification: str
    classification_correct: bool
    total_turns: int
    fields_extracted: Dict[str, ExtractedValue]


class ConversationSimulator:
    def __init__(self):
        self.personas = self._init_personas()

    def _init_personas(self) -> Dict[str, Any]:
        return {
            Persona.HOT_BUYER.value: {
                "initial_state": CustomerState.HIGH_INTENT,
                "expected_classification": "HOT",
                "responses": {
                    "budget": ["Tầm 3 tỷ em nhé", "Khoảng 3 tỷ", "Tối đa 3 tỷ rưỡi"],
                    "location": ["Quận 7 em", "Anh kiếm khu Quận 7", "Quận 2 hoặc Quận 7"],
                    "timeline": ["Mua ngay trong tháng này", "Cuối tháng anh cần", "Cần gấp"],
                    "financing": ["Anh mua tiền mặt", "Tiền mặt nha em", "Không vay"],
                    "purpose": ["Mua để ở", "Ở thực", "Cho gia đình ở"],
                    "product_interest": ["Căn 2 phòng ngủ", "2 phòng ngủ", "Căn hộ 2PN"],
                }
            },
            Persona.WARM_BUYER.value: {
                "initial_state": CustomerState.ENGAGED,
                "expected_classification": "WARM",
                "responses": {
                    "budget": ["khoảng 2-3 tỷ", "tầm 2 tới 3 tỉ"],
                    "location": ["Gò Vấp", "Khu Gò Vấp", "Tân Bình"],
                    "timeline": ["Trong vòng 3 tháng tới", "Tầm 2-3 tháng nữa"],
                    "financing": ["Chắc phải vay thêm ngân hàng", "Vay 50%"],
                    "purpose": ["Mua ở"],
                    "product_interest": ["Căn hộ 2 phòng ngủ"],
                }
            },
            Persona.COLD_LEAD.value: {
                "initial_state": CustomerState.UNCERTAIN,
                "expected_classification": "COLD",
                "responses": {
                    "budget": ["Chưa biết em ơi", "Tùy tình hình", "Để xem đã"],
                    "location": ["Đâu cũng được", "Chưa chốt"],
                    "timeline": ["Chưa vội", "Sang năm tính"],
                    "financing": ["Chưa biết"],
                    "purpose": ["Chưa rõ"],
                    "product_interest": ["Xem thôi"],
                }
            },
            Persona.CURIOUS.value: {
                "initial_state": CustomerState.CURIOUS,
                "expected_classification": "COLD",
                "responses": {
                    "budget": ["Tầm 2 tỷ"],
                    "location": ["Quận 2"],
                    "timeline": ["Xem thôi", "Tham khảo"],
                    "financing": ["Chưa biết"],
                    "purpose": ["Chưa biết"],
                    "product_interest": ["Căn hộ nhỏ thôi"],
                }
            },
            Persona.PRICE_SHOPPER.value: {
                "initial_state": CustomerState.CURIOUS,
                "expected_classification": "WARM",
                "responses": {
                    "budget": ["khoảng 1 tỷ 5", "tầm 1.5 tỷ"],
                    "location": ["Chưa biết", "Gần trung tâm"],
                    "timeline": ["từ từ", "chưa vội"],
                    "financing": ["vay ngân hàng"],
                    "purpose": ["để ở"],
                    "product_interest": ["Căn nhỏ thôi, 1PN hoặc 2PN"],
                }
            },
            Persona.BUDGET_REFUSAL.value: {
                "initial_state": CustomerState.RESISTANT,
                "expected_classification": "COLD",
                "responses": {
                    "budget": ["Không muốn nói", "Riêng tư", "Hỏi nhiều vậy"],
                    "location": ["Q7"],
                    "timeline": ["Chưa biết"],
                    "financing": ["Tiền mặt"],
                    "purpose": ["Mua ở"],
                    "product_interest": ["Căn 2 phòng ngủ"],
                }
            },
            Persona.BUSY_CUSTOMER.value: {
                "initial_state": CustomerState.BUSY,
                "expected_classification": "WARM",
                "responses": {
                    "budget": ["Đang bận em ơi", "Gọi lại sau"],
                    "location": ["Đang họp nha"],
                    "timeline": ["Bận rồi"],
                    "financing": ["Lúc khác gọi"],
                    "purpose": ["Đang chạy xe"],
                    "product_interest": ["Đang bận"],
                }
            },
            Persona.SKEPTICAL_CUSTOMER.value: {
                "initial_state": CustomerState.RESISTANT,
                "expected_classification": "WARM",
                "responses": {
                    "budget": ["Khoảng 2 tỷ", "2 tỷ"],
                    "location": ["Q9", "Quận 9"],
                    "timeline": ["Để xem", "Chưa tin tưởng lắm"],
                    "financing": ["Chưa biết"],
                    "purpose": ["Ở"],
                    "product_interest": ["Căn hộ 2PN"],
                }
            },
            Persona.CONFUSED_CUSTOMER.value: {
                "initial_state": CustomerState.CONFUSED,
                "expected_classification": "COLD",
                "responses": {
                    "budget": ["À", "Không rõ", "Chưa rành"],
                    "location": ["Đâu cũng được"],
                    "timeline": ["Tùy"],
                    "financing": ["Không rõ"],
                    "purpose": ["Tùy"],
                    "product_interest": ["Chưa biết"],
                }
            },
            Persona.MIND_CHANGER.value: {
                "initial_state": CustomerState.ENGAGED,
                "expected_classification": "WARM",
                "responses": {
                    "budget": ["3 tỷ", "À thực ra 1.5 tỷ thôi"],  # contradiction test
                    "location": ["Quận 7", "Q7"],
                    "timeline": ["Tháng sau"],
                    "financing": ["Vay"],
                    "purpose": ["Ở"],
                    "product_interest": ["Căn 2 phòng ngủ"],
                }
            },
            Persona.WRONG_NUMBER.value: {
                "initial_state": CustomerState.REFUSING,
                "expected_classification": "INVALID",
                "responses": {
                    "budget": ["Nhầm số rồi", "Không phải tôi", "Sai số"],
                    "location": ["Nhầm số"],
                    "timeline": ["Nhầm số"],
                    "financing": ["Nhầm số"],
                    "purpose": ["Nhầm số"],
                    "product_interest": ["Nhầm số"],
                }
            },
            Persona.SPAM_INVALID.value: {
                "initial_state": CustomerState.REFUSING,
                "expected_classification": "INVALID",
                "responses": {
                    "budget": ["Đừng gọi nữa", "Không cần"],
                    "location": ["Thôi khỏi"],
                    "timeline": ["Không"],
                    "financing": ["Không"],
                    "purpose": ["Không"],
                    "product_interest": ["Không"],
                }
            },
            Persona.HIGH_INTENT_VAGUE.value: {
                "initial_state": CustomerState.HIGH_INTENT,
                "expected_classification": "WARM",
                "responses": {
                    "budget": ["Tầm đó", "Vừa vừa"],
                    "location": ["Chỗ nào tiện", "Gần trung tâm"],
                    "timeline": ["Cần gấp", "Sắp tới"],
                    "financing": ["Tùy"],
                    "purpose": ["Mua ở"],
                    "product_interest": ["Căn 2PN"],
                }
            },
            Persona.LOW_BUDGET.value: {
                "initial_state": CustomerState.ENGAGED,
                "expected_classification": "COLD",
                "responses": {
                    "budget": ["Khoảng 500 triệu", "Dưới 1 tỷ"],
                    "location": ["Xa xíu cũng được"],
                    "timeline": ["Sang năm"],
                    "financing": ["Vay tối đa"],
                    "purpose": ["Ở"],
                    "product_interest": ["Căn nhỏ"],
                }
            },
            Persona.INVESTOR.value: {
                "initial_state": CustomerState.HIGH_INTENT,
                "expected_classification": "HOT",
                "responses": {
                    "budget": ["Tầm 5 tỷ", "Khoảng 5 tỷ"],
                    "location": ["Quận 2", "Thủ Đức"],
                    "timeline": ["Mua ngay", "Tuần này chốt"],
                    "financing": ["Tiền mặt"],
                    "purpose": ["Đầu tư", "Cho thuê"],
                    "product_interest": ["Căn 2-3 phòng ngủ"],
                }
            },
        }

    def run_conversation(
        self,
        persona_type: Persona,
        engine,  # QualificationEngine or QuestionStrategyEngine
        strategy: QuestionStrategyEngine = None,
        matcher: ResponsePatternMatcher = None,
        max_turns: int = 10,
    ) -> SimulationResult:
        """
        Run a simulated multi-turn conversation.
        
        Accepts either:
        - (persona_type, qualification_engine, strategy, matcher) — preferred
        - (persona_type, strategy_engine, matcher) — backward compat (old subagent signature)
        """
        # Handle both calling conventions
        if strategy is None and matcher is None:
            # Old signature: run_conversation(persona, strategy_engine, matcher)
            # engine was actually the strategy, nothing else provided
            raise ValueError("Must provide strategy and matcher separately.")
        
        # If engine is a QuestionStrategyEngine, it was passed as strategy
        if isinstance(engine, QuestionStrategyEngine):
            strategy = engine
            engine = None

        # Create fresh state for this simulation
        session_id = f"sim_{uuid.uuid4().hex[:8]}"
        state = ConversationState(phone="+84901234567", session_id=session_id)
        persona_data = self.personas[persona_type.value]
        state.set_customer_state(persona_data["initial_state"])

        # Shuffled response pool to avoid determinism
        responses_pool: Dict[str, List[str]] = {}
        for field_name, options in persona_data["responses"].items():
            responses_pool[field_name] = list(options)  # copy
            random.shuffle(responses_pool[field_name])

        # Opening agent turn
        state.add_turn("AGENT", "Dạ chào anh/chị, em gọi từ AIMOS. Anh/chị đang tìm mua bất động sản đúng không ạ?")

        field_response_index: Dict[str, int] = {}  # rotate through responses

        turn_count = 1
        while turn_count < max_turns:
            # Termination: BUSY or REFUSING
            if state.customer_state in (CustomerState.BUSY, CustomerState.REFUSING):
                break

            # Get next best question from strategy
            next_q = strategy.select_next_question(state)
            if not next_q:
                break  # All extracted or qualification complete

            # Agent asks
            state.add_turn("AGENT", next_q.question_text)
            state.mark_asked(next_q.field_target)

            # Customer responds (rotate through options)
            field_key = next_q.field_target
            pool = responses_pool.get(field_key, ["Ừ", "Chưa biết"])
            idx = field_response_index.get(field_key, 0)
            cust_resp = pool[idx % len(pool)]
            field_response_index[field_key] = idx + 1

            state.add_turn("CUSTOMER", cust_resp)

            # Extract field from customer response
            if matcher:
                match_res = matcher.match(cust_resp, field_key)
                if match_res:
                    ext_val = ExtractedValue(
                        field=field_key,
                        raw_text=cust_resp,
                        normalized_value=match_res.normalized_value,
                        response_type=match_res.response_type,
                        provenance=ProvenanceStatus.STATED.value,
                        confidence=match_res.confidence,
                        evidence=cust_resp,
                        turn_index=turn_count * 2,
                    )
                    state.update_field(field_key, ext_val)

                # Re-evaluate customer state from latest response
                detected = matcher.detect_customer_state(cust_resp)
                if detected not in (CustomerState.UNKNOWN, CustomerState.ENGAGED):
                    state.set_customer_state(detected)

            turn_count += 1

        # Run QualificationEngine on final conversation
        conv_list = [{"speaker": t.speaker, "text": t.text} for t in state.turns]
        if engine is not None:
            try:
                qual_result = engine.process(
                    lead_data={"phone": "+84901234567"},
                    conversation=conv_list,
                )
                actual_classification = qual_result.get("classification", "UNKNOWN")
            except Exception:
                actual_classification = self._fallback_classification(state)
                qual_result = {"classification": actual_classification}
        else:
            actual_classification = self._fallback_classification(state)
            qual_result = {"classification": actual_classification}

        expected = persona_data["expected_classification"]

        return SimulationResult(
            persona_id=persona_type.value,
            turns=state.turns,
            final_state=state,
            qualification_result=qual_result,
            actual_classification=actual_classification,
            expected_classification=expected,
            classification_correct=(actual_classification == expected),
            total_turns=len(state.turns),
            fields_extracted=state.extracted_fields,
        )

    def _fallback_classification(self, state: ConversationState) -> str:
        """Fallback classification when QualificationEngine is unavailable."""
        if state.customer_state == CustomerState.REFUSING:
            return "INVALID"
        elif state.customer_state == CustomerState.BUSY:
            return "WARM"
        elif len(state.extracted_fields) >= 3:
            return "HOT"
        elif len(state.extracted_fields) >= 1:
            return "WARM"
        else:
            return "COLD"

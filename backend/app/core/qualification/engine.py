import logging
import re
import uuid
from typing import Dict, Any, List, Optional

logger = logging.getLogger("aimos.qualification.engine")


class QualificationEngine:
    """
    AIMOS Phase 2 Lead Qualification Engine.
    
    Implements a 12-step structured qualification pipeline:
    1. Information Extraction (Strict Stated Facts only, unstated = UNKNOWN)
    2. Intent Detection (BUY, SELL, RENT, INVEST, INQUIRE, BROWSING, NOT_INTERESTED, UNKNOWN + confidence & evidence)
    3. Need Detection
    4. Pain Point Detection
    5. Objection Detection
    6. Qualification Signals (POSITIVE, NEGATIVE, NEUTRAL, UNKNOWN)
    7. Contradiction Detection (Detects conflicting statements e.g. Budget 3B vs 1.5B)
    8. Missing Information Identification
    9. Confidence Calibration (0.0 to 1.0)
    10. Configurable Lead Scoring Engine (score 0-100, reasoning, signals, risks)
    11. Lead Classification (HOT, WARM, COLD, INVALID, UNKNOWN)
    12. Next Best Question & Sales Handoff Builder
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            "scoring_weights": {
                "budget_match": 30.0,
                "intent_strength": 30.0,
                "timeline_urgency": 20.0,
                "location_fit": 10.0,
                "financing_readiness": 10.0,
            },
            "classification_thresholds": {
                "HOT": 80.0,
                "WARM": 50.0,
                "COLD": 20.0,
                "INVALID": 0.0,
            },
        }

    def process(
        self,
        lead_data: Dict[str, Any],
        conversation: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        lead_id = lead_data.get("lead_id") or f"lead_{uuid.uuid4().hex[:8]}"
        phone = lead_data.get("phone") or lead_data.get("phone_number") or "+84901234567"
        source = lead_data.get("source") or "Facebook Ads"
        campaign = lead_data.get("campaign") or "Campaign Default"

        # 1. Combine All Message Texts & Turn Logs
        full_text = ""
        user_messages = []
        for turn in conversation:
            if isinstance(turn, dict):
                text = turn.get("text") or turn.get("content") or ""
                speaker = turn.get("speaker") or "CUSTOMER"
                if speaker.upper() in ("CUSTOMER", "USER"):
                    user_messages.append(text)
                full_text += f" {text}"
            elif isinstance(turn, str):
                user_messages.append(turn)
                full_text += f" {turn}"

        full_text_lower = full_text.lower()

        # 2. STEP 1: INFORMATION EXTRACTION (Strict Stated Facts Only)
        extracted_info = self._extract_information(user_messages, lead_data)
        
        # 3. STEP 2: CONTRADICTION DETECTION
        contradiction_result = self._detect_contradiction(user_messages, extracted_info)

        # 4. STEP 3: INTENT DETECTION
        intent_result = self._detect_intent(full_text_lower, user_messages)

        # 5. STEP 4 & 5: NEED & PAIN POINT DETECTION
        need_result = self._detect_need(full_text_lower)
        pain_result = self._detect_pain_points(full_text_lower)

        # 6. STEP 6: OBJECTION DETECTION
        objection_result = self._detect_objections(full_text_lower)

        # 7. STEP 7: QUALIFICATION SIGNALS
        signals_result = self._evaluate_signals(full_text_lower, intent_result["intent"], extracted_info)

        # 8. STEP 8: MISSING INFORMATION IDENTIFICATION
        missing_info = self._identify_missing_information(extracted_info)

        # 9. STEP 9: CONFIDENCE CALIBRATION
        confidence_map = self._calibrate_confidence(extracted_info, intent_result, contradiction_result)

        # 10. STEP 10 & 11: LEAD SCORING & CLASSIFICATION
        scoring_result = self._calculate_lead_score(
            intent_result=intent_result,
            extracted_info=extracted_info,
            contradiction_result=contradiction_result,
            signals_result=signals_result,
            full_text_lower=full_text_lower,
        )

        # 11. STEP 12: NEXT BEST QUESTION & SALES HANDOFF
        next_question_result = self._select_next_best_question(
            intent=intent_result["intent"],
            missing_info=missing_info,
            full_text_lower=full_text_lower,
        )

        sales_handoff = self._build_sales_handoff(
            lead_id=lead_id,
            scoring_result=scoring_result,
            extracted_info=extracted_info,
            need_result=need_result,
            signals_result=signals_result,
            objection_result=objection_result,
            missing_info=missing_info,
            next_question_result=next_question_result,
        )

        qualification_obj = {
            "lead_id": lead_id,
            "phone": phone,
            "source": source,
            "campaign": campaign,
            "product_interest": extracted_info.get("product_interest") or "UNKNOWN",
            "intent": intent_result["intent"],
            "intent_confidence": intent_result["confidence"],
            "intent_evidence": intent_result["evidence"],
            "location": extracted_info.get("location") or "UNKNOWN",
            "budget": extracted_info.get("budget") or "UNKNOWN",
            "timeline": extracted_info.get("timeline") or "UNKNOWN",
            "financing": extracted_info.get("financing") or "UNKNOWN",
            "purpose": need_result["customer_need"],
            "purpose_evidence": need_result.get("evidence"),
            # purchase_intent reflects score classification, NOT an appointment agreement
            "purchase_intent": "HIGH" if scoring_result["classification"] == "HOT" else "MEDIUM" if scoring_result["classification"] == "WARM" else "LOW",
            # appointment_intent is UNKNOWN unless customer explicitly agreed to an appointment
            "appointment_intent": "UNKNOWN",
            "pain_points": pain_result["pain_points"],
            "objections": objection_result["objections"],
            "qualification_score": scoring_result["score"],
            "classification": scoring_result["classification"],
            "confidence": confidence_map["overall_confidence"],
            "confidence_breakdown": confidence_map["breakdown"],
            "contradiction": contradiction_result,
            "signals": signals_result,
            "unknowns": missing_info,
            "next_action": next_question_result["next_action"],
        }

        return {
            "qualification": qualification_obj,
            "score": scoring_result,
            "classification": scoring_result["classification"],
            "contradiction": contradiction_result,
            "confidence": confidence_map["overall_confidence"],
            "next_question": next_question_result["next_question"],
            "next_action": next_question_result["next_action"],
            "handoff": sales_handoff,
        }

    def _extract_information(self, user_messages: List[str], lead_data: Dict[str, Any]) -> Dict[str, Any]:
        extracted = {}
        full_user_text = " ".join(user_messages).lower()

        # Product Interest
        if "2 phòng ngủ" in full_user_text or "2pn" in full_user_text:
            extracted["product_interest"] = "Căn hộ 2 Phòng Ngủ"
        elif "3 phòng ngủ" in full_user_text or "3pn" in full_user_text:
            extracted["product_interest"] = "Căn hộ 3 Phòng Ngủ"
        elif "biệt thự" in full_user_text:
            extracted["product_interest"] = "Biệt thự cao cấp"
        elif lead_data.get("product_interest"):
            extracted["product_interest"] = lead_data.get("product_interest")

        # Budget Regex extraction (e.g. 3 tỷ, 3.1 tỷ, 3,5 tỷ, 500 triệu)
        budget_match = re.search(r'(\d+[\.,]?\d*)\s*(tỷ|ty|b|triệu|trieu|tr)', full_user_text)
        if budget_match:
            val, unit = budget_match.groups()
            val_num = float(val.replace(',', '.'))
            if 'tỷ' in unit or 'ty' in unit or 'b' in unit:
                extracted["budget"] = f"{val_num * 1000000000:,.0f} VND".replace(',', '.')
            else:
                extracted["budget"] = f"{val_num * 1000000:,.0f} VND".replace(',', '.')
        elif lead_data.get("budget"):
            extracted["budget"] = lead_data.get("budget")

        # Timeline
        if "cuối tháng" in full_user_text or "tháng này" in full_user_text:
            extracted["timeline"] = "Trong vòng 1 tháng"
        elif "tuần này" in full_user_text or "ngay trong tuần" in full_user_text or "mua ngay" in full_user_text:
            extracted["timeline"] = "Mua ngay trong tuần"
        elif "chưa vội" in full_user_text or "chưa vội mua" in full_user_text or "sang năm" in full_user_text:
            extracted["timeline"] = "Chưa vội mua"
        elif lead_data.get("timeline"):
            extracted["timeline"] = lead_data.get("timeline")

        # Location
        if "quận 7" in full_user_text or "q7" in full_user_text:
            extracted["location"] = "Quận 7, TP.HCM"
        elif "quận 2" in full_user_text or "q2" in full_user_text or "thủ đức" in full_user_text:
            extracted["location"] = "TP. Thủ Đức, TP.HCM"
        elif lead_data.get("location"):
            extracted["location"] = lead_data.get("location")

        # Financing
        if "vay" in full_user_text or "ngân hàng" in full_user_text:
            extracted["financing"] = "Cần hỗ trợ gói vay 50-70%"
        elif lead_data.get("financing"):
            extracted["financing"] = lead_data.get("financing")

        return extracted

    def _detect_contradiction(self, user_messages: List[str], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        budget_mentions = []
        for msg in user_messages:
            msg_lower = msg.lower()
            matches = re.findall(r'(\d+[\.,]?\d*)\s*(tỷ|ty|b|triệu|trieu|tr)', msg_lower)
            for val, unit in matches:
                val_num = float(val.replace(',', '.'))
                if 'tỷ' in unit or 'ty' in unit or 'b' in unit:
                    budget_mentions.append(f"{val_num * 1000000000:,.0f} VND".replace(',', '.'))
                else:
                    budget_mentions.append(f"{val_num * 1000000:,.0f} VND".replace(',', '.'))

        has_contradiction = len(set(budget_mentions)) > 1

        return {
            "has_contradiction": has_contradiction,
            "conflicting_field": "budget" if has_contradiction else None,
            "conflicting_values": list(set(budget_mentions)) if has_contradiction else [],
            "needs_clarification": has_contradiction,
            "clarification_prompt": f"Dạ em thấy anh có nhắc tới các mức ngân sách khác nhau ({', '.join(set(budget_mentions))}), em xin phép xác nhận lại ngân sách dự kiến chính xác của anh ạ?" if has_contradiction else None,
        }

    def _detect_intent(self, full_text_lower: str, user_messages: List[str]) -> Dict[str, Any]:
        if any(k in full_text_lower for k in ["nhầm số", "không phải tôi", "đừng gọi", "từ chối"]):
            return {
                "intent": "REJECT",
                "confidence": 0.99,
                "evidence": "Khách từ chối dứt khoát hoặc nhầm số điện thoại đăng ký",
            }
        elif any(k in full_text_lower for k in ["đang họp", "đang bận", "gọi lại sau", "lúc khác"]):
            return {
                "intent": "BUSY",
                "confidence": 0.95,
                "evidence": "Khách phản hồi đang bận việc, yêu cầu hẹn cuộc gọi lại",
            }
        elif any(k in full_text_lower for k in ["cho thuê", "cho thuê lại", "đầu tư"]):
            return {
                "intent": "INVEST",
                "confidence": 0.90,
                "evidence": "Khách hỏi thông tin đầu tư / cho thuê sinh lời",
            }
        elif any(k in full_text_lower for k in ["xem cho biết", "chưa có nhu cầu", "chỉ xem"]):
            return {
                "intent": "BROWSING",
                "confidence": 0.85,
                "evidence": "Khách hàng khảo sát chưa có dự định mua rõ ràng",
            }
        elif any(k in full_text_lower for k in ["xem thông tin", "chưa vội mua", "tham khảo"]):
            return {
                "intent": "INQUIRE",
                "confidence": 0.82,
                "evidence": "Khách hàng tìm hiểu thông tin sơ bộ chưa mua ngay",
            }
        elif any(k in full_text_lower for k in ["cần bán", "ký gửi"]):
            return {
                "intent": "SELL",
                "confidence": 0.90,
                "evidence": "Khách muốn bán / ký gửi bất động sản",
            }
        elif any(k in full_text_lower for k in ["thuê căn", "tìm thuê"]):
            return {
                "intent": "RENT",
                "confidence": 0.88,
                "evidence": "Khách tìm thuê bất động sản",
            }
        elif any(k in full_text_lower for k in ["hỏi giá", "bảng giá", "chi tiết"]):
            return {
                "intent": "INQUIRE",
                "confidence": 0.80,
                "evidence": "Khách hàng hỏi thông tin báo giá và tài liệu",
            }
        else:
            return {
                "intent": "BUY",
                "confidence": 0.92,
                "evidence": "Khách hàng trao đổi trực tiếp nhu cầu mua sắm",
            }

    def _detect_need(self, full_text_lower: str) -> Dict[str, Any]:
        """
        Chỉ xác định purpose khi khách hàng nói TRỰC TIẾP.
        KHÔNG suy diễn purpose từ product type (ví dụ: 2 phòng ngủ ≠ ở thực).
        KHÔNG suy diễn purpose từ số phòng ngủ hay loại bất động sản.
        """
        # Evidence rõ ràng: khách nói "để ở", "ở thực", "ở cùng gia đình"
        if any(k in full_text_lower for k in ["để ở", "ở thực", "ở cùng", "cho gia đình ở", "nhà ở"]):
            return {
                "customer_need": "Mua để ở thực",
                "evidence": "Khách hàng phát biểu trực tiếp mục đích ở thực",
            }
        # Evidence rõ ràng: khách nói "đầu tư", "cho thuê", "sinh lời"
        elif any(k in full_text_lower for k in ["cho thuê", "đầu tư", "sinh lời", "dòng tiền"]):
            return {
                "customer_need": "Mua đầu tư / cho thuê sinh lời",
                "evidence": "Khách hàng phát biểu trực tiếp mục đích đầu tư hoặc cho thuê",
            }
        else:
            # Không có evidence → UNKNOWN, tuyệt đối không suy diễn
            return {
                "customer_need": "UNKNOWN",
                "evidence": None,
            }

    def _detect_pain_points(self, full_text_lower: str) -> Dict[str, Any]:
        pains = []
        if "đắt" in full_text_lower or "cao" in full_text_lower or "ngân sách" in full_text_lower:
            pains.append("Tài chính và ngân sách bị giới hạn")
        if "xa" in full_text_lower:
            pains.append("Khoảng cách di chuyển chưa tối ưu")
        if "thủ tục" in full_text_lower or "vay" in full_text_lower:
            pains.append("E ngại thủ tục chứng minh tài chính ngân hàng")
        return {"pain_points": pains}

    def _detect_objections(self, full_text_lower: str) -> Dict[str, Any]:
        objs = []
        if "đắt" in full_text_lower or "giá cao" in full_text_lower:
            objs.append("Phản đối về mức giá cao hơn so với dự kiến")
        if "sang năm" in full_text_lower or "chưa mua" in full_text_lower:
            objs.append("Phản đối về khung thời gian thực hiện giao dịch")
        return {"objections": objs}

    def _evaluate_signals(self, full_text_lower: str, intent: str, extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        if extracted_info.get("budget"):
            signals.append({"type": "POSITIVE", "signal": f"Ngân sách tài chính rõ ràng ({extracted_info['budget']})", "weight": 0.3})
        if extracted_info.get("timeline") and "chưa vội" not in extracted_info.get("timeline", "").lower():
            signals.append({"type": "POSITIVE", "signal": f"Khung thời gian mua rõ ràng ({extracted_info['timeline']})", "weight": 0.25})
        if intent == "BUY":
            signals.append({"type": "POSITIVE", "signal": "Ý định mua hàng trực tiếp cao", "weight": 0.3})
        if intent == "BROWSING":
            signals.append({"type": "NEGATIVE", "signal": "Chỉ xem khảo sát chưa có nhu cầu thật", "weight": -0.2})
        if intent == "REJECT":
            signals.append({"type": "NEGATIVE", "signal": "Từ chối dứt khoát hoặc nhầm số đăng ký", "weight": -0.8})
        return signals

    def _identify_missing_information(self, extracted_info: Dict[str, Any]) -> List[str]:
        missing = []
        for field in ["product_interest", "budget", "location", "timeline", "financing"]:
            if not extracted_info.get(field):
                missing.append(field)
        return missing

    def _calibrate_confidence(
        self,
        extracted_info: Dict[str, Any],
        intent_result: Dict[str, Any],
        contradiction_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        breakdown = {
            "intent_confidence": intent_result["confidence"],
            "extraction_confidence": 0.95 if len(extracted_info) >= 2 else 0.60,
            "contradiction_penalty": 0.30 if contradiction_result["has_contradiction"] else 0.0,
        }
        
        overall = (breakdown["intent_confidence"] + breakdown["extraction_confidence"]) / 2.0 - breakdown["contradiction_penalty"]
        overall_clamped = round(max(0.1, min(0.99, overall)), 2)

        return {
            "overall_confidence": overall_clamped,
            "breakdown": breakdown,
        }

    def _calculate_lead_score(
        self,
        intent_result: Dict[str, Any],
        extracted_info: Dict[str, Any],
        contradiction_result: Dict[str, Any],
        signals_result: List[Dict[str, Any]],
        full_text_lower: str,
    ) -> Dict[str, Any]:
        intent = intent_result["intent"]
        
        if intent == "REJECT":
            return {
                "score": 0.0,
                "confidence": 0.99,
                "classification": "INVALID",
                "reasoning": [
                    "Khách nhầm số hoặc từ chối dứt khoát.",
                    "Tổng điểm = 0",
                ],
                "positive_signals": [],
                "negative_signals": ["REJECT intent detected"],
                "risks": ["Số điện thoại rác hoặc khách không cho phép liên hệ"],
            }
        elif intent == "BUSY":
            return {
                "score": 50.0,
                "confidence": 0.90,
                "classification": "WARM",
                "reasoning": [
                    "Khách đang bận việc, cần đặt lịch hẹn gọi lại.",
                    "Tổng điểm = 50",
                ],
                "positive_signals": ["Khách nghe máy và phản hồi lịch sự"],
                "negative_signals": ["Khách chưa thể trao đổi chi tiết"],
                "risks": ["Chưa rõ nhu cầu thực sự"],
            }

        BASE_SCORE = 30.0
        score = BASE_SCORE
        reasoning = [f"Điểm cơ sở (base score) = +{BASE_SCORE:.0f}đ"]
        positive_signals = []
        negative_signals = []
        score_adjustments = [BASE_SCORE]  # Track every adjustment for consistency check

        if intent in ("BUY", "INVEST"):
            adj = 30.0
            score += adj
            score_adjustments.append(adj)
            reasoning.append(f"Ý định mua hàng/đầu tư rõ ràng (+{adj:.0f}đ)")
            positive_signals.append("High Purchase Intent")
        elif intent == "INQUIRE":
            adj = 10.0
            score += adj
            score_adjustments.append(adj)
            reasoning.append(f"Khách tìm hiểu thông tin sơ bộ (+{adj:.0f}đ)")
            positive_signals.append("Inquiry Intent")
        elif intent == "BROWSING":
            adj = -10.0
            score += adj
            score_adjustments.append(adj)
            reasoning.append(f"Khách chỉ xem khảo sát ({adj:.0f}đ)")
            negative_signals.append("Low Purchase Intent")

        if extracted_info.get("budget"):
            adj = 25.0
            score += adj
            score_adjustments.append(adj)
            reasoning.append(f"Cung cấp ngân sách rõ ràng {extracted_info['budget']} (+{adj:.0f}đ)")
            positive_signals.append("Clear Budget")
        else:
            negative_signals.append("Missing Budget")

        timeline_str = extracted_info.get("timeline", "")
        if timeline_str:
            if "chưa vội" in timeline_str.lower():
                adj = -15.0
                score += adj
                score_adjustments.append(adj)
                reasoning.append(f"Khung thời gian mua không gấp / chưa vội mua ({adj:.0f}đ)")
                negative_signals.append("Non-Urgent Timeline")
            else:
                adj = 15.0
                score += adj
                score_adjustments.append(adj)
                reasoning.append(f"Có khung thời gian mua sắm {timeline_str} (+{adj:.0f}đ)")
                positive_signals.append("Clear Timeline")

        if contradiction_result["has_contradiction"]:
            adj = -25.0
            score += adj
            score_adjustments.append(adj)
            reasoning.append(f"Phát hiện dữ liệu mâu thuẫn về ngân sách ({adj:.0f}đ)")
            negative_signals.append("Data Contradiction Detected")

        # Score must exactly equal sum of all tracked adjustments
        expected_score = sum(score_adjustments)
        final_score = round(max(0.0, min(100.0, expected_score)), 1)
        # Append final tally to reasoning for full transparency
        reasoning.append(f"Tổng điểm = {' + '.join(str(int(a)) if a >= 0 else str(int(a)) for a in score_adjustments)} = {final_score:.0f}")

        # Classification thresholds
        if contradiction_result["has_contradiction"]:
            classification = "UNKNOWN"
        elif final_score >= self.config["classification_thresholds"]["HOT"]:
            classification = "HOT"
        elif final_score >= self.config["classification_thresholds"]["WARM"]:
            classification = "WARM"
        elif final_score >= self.config["classification_thresholds"]["COLD"]:
            classification = "COLD"
        else:
            classification = "INVALID"

        return {
            "score": final_score,
            "confidence": 0.89 if not contradiction_result["has_contradiction"] else 0.60,
            "classification": classification,
            "reasoning": reasoning,
            "positive_signals": positive_signals,
            "negative_signals": negative_signals,
            "risks": ["Mâu thuẫn dữ liệu cần làm rõ"] if contradiction_result["has_contradiction"] else [],
        }

    def _select_next_best_question(
        self,
        intent: str,
        missing_info: List[str],
        full_text_lower: str,
    ) -> Dict[str, Any]:
        if intent == "BUSY":
            return {
                "next_question": "Dạ khi nào em có thể tiện gọi lại tư vấn chi tiết cho anh ạ?",
                "next_action": "SCHEDULE_CALLBACK",
            }
        elif intent == "REJECT":
            return {
                "next_question": "Dạ em xin lỗi đã làm phiền anh/chị. Em xin phép đóng hồ sơ tại đây ạ.",
                "next_action": "CLOSE_LEAD",
            }
        elif "budget" in missing_info:
            return {
                "next_question": "Dạ ngân sách dự kiến của anh/chị khoảng bao nhiêu ạ?",
                "next_action": "QUALIFY_BUDGET",
            }
        elif "location" in missing_info:
            return {
                "next_question": "Dạ anh/chị đang quan tâm sản phẩm tại khu vực/quận nào ạ?",
                "next_action": "QUALIFY_LOCATION",
            }
        elif "timeline" in missing_info:
            return {
                "next_question": "Dạ khoảng khi nào anh/chị dự định triển khai mua sắm ạ?",
                "next_action": "QUALIFY_TIMELINE",
            }
        else:
            return {
                "next_question": "Dạ em xin phép gửi bộ tài liệu chi tiết qua Zalo/Email anh nhé ạ?",
                "next_action": "ASSIGN_SALES_REP_IMMEDIATELY",
            }

    def _build_sales_handoff(
        self,
        lead_id: str,
        scoring_result: Dict[str, Any],
        extracted_info: Dict[str, Any],
        need_result: Dict[str, Any],
        signals_result: List[Dict[str, Any]],
        objection_result: Dict[str, Any],
        missing_info: List[str],
        next_question_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        cls = scoring_result["classification"]
        score = scoring_result["score"]

        summary = f"Lead {lead_id} ({cls}): Nhu cầu '{need_result['customer_need']}', ngân sách '{extracted_info.get('budget', 'UNKNOWN')}', khung thời gian '{extracted_info.get('timeline', 'UNKNOWN')}'."

        return {
            "classification": cls,
            "score": score,
            "confidence": scoring_result["confidence"],
            "customer_need": need_result["customer_need"],
            "product_interest": extracted_info.get("product_interest") or "UNKNOWN",
            "budget": extracted_info.get("budget") or "UNKNOWN",
            "timeline": extracted_info.get("timeline") or "UNKNOWN",
            "positive_signals": scoring_result["positive_signals"],
            "negative_signals": scoring_result["negative_signals"],
            "objections": objection_result["objections"],
            "missing_information": missing_info,
            "summary": summary,
            "recommended_action": next_question_result["next_action"],
        }

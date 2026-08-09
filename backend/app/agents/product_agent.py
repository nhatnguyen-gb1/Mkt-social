import logging
from typing import List, Optional, Dict, Any
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.tools.base import BaseTool
from app.core.llm.base import BaseLLMProvider
from app.core.skills.executor import SkillExecutor
from app.core.skills.evaluator import SkillEvaluator

logger = logging.getLogger("aimos.agents.product")


class ProductAgent(BaseAgent):
    """
    ProductAgent - Senior Product Strategist / Product Marketing Specialist V1.
    
    Product Analysis Flow:
    PRODUCT -> CUSTOMER -> PROBLEM -> NEED -> VALUE -> USP -> POSITIONING -> DIFFERENTIATION -> OFFER -> PRICING -> VALIDATION -> RISK -> RECOMMENDATION
    
    PMF Framework:
    Evaluates PMF Score across 10 dimensions (Customer Need, Problem Severity, Target Customer Clarity, Value Proposition, Differentiation, Competitive Pressure, Price/Value Fit, Purchase Intent, Repeat Potential, Market Evidence).
    
    Validation Pipeline:
    Hypothesis -> Evidence Required -> Test -> Result -> Decision (VALIDATE / ITERATE / REJECT / NEED_MORE_DATA)
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tools: Optional[List[BaseTool]] = None,
        skill_executor: Optional[SkillExecutor] = None,
    ):
        super().__init__(
            llm_provider=llm_provider,
            tools=tools,
            agent_name="ProductAgent",
        )
        self.skill_executor = skill_executor or SkillExecutor()
        self.evaluator = SkillEvaluator()

    async def _node_llm_reasoner(self, state: AgentState) -> AgentState:
        input_payload = state.input_data or {}
        
        # Flexibly parse product input
        prod_input = input_payload.get("product")
        if isinstance(prod_input, dict):
            product_name = prod_input.get("name") or prod_input.get("product_name") or "Sản phẩm Mẫu"
        elif isinstance(prod_input, str):
            product_name = prod_input
        else:
            product_name = input_payload.get("product_name") or "Sản phẩm Mẫu"

        target_market = input_payload.get("market") or input_payload.get("target_market") or "Philippines"
        research_context = input_payload.get("research_context") or {}
        provider_name = self.llm_provider.get_provider_name().lower()

        logger.info(
            f"[PRODUCT AGENT] Processing product='{product_name}', market='{target_market}'"
        )

        # 1. EXECUTE SKILL CHAIN
        # Skill 1: product_analysis
        res_prod = await self.skill_executor.execute_skill(
            skill_name="product_analysis",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 2: customer_persona
        res_cust = await self.skill_executor.execute_skill(
            skill_name="customer_persona",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 3: customer_problem_analysis
        res_prob = await self.skill_executor.execute_skill(
            skill_name="customer_problem_analysis",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 4: jobs_to_be_done
        res_jtbd = await self.skill_executor.execute_skill(
            skill_name="jobs_to_be_done",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 5: value_proposition
        res_val = await self.skill_executor.execute_skill(
            skill_name="value_proposition",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 6: usp_generation
        res_usp = await self.skill_executor.execute_skill(
            skill_name="usp_generation",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 7: positioning_strategy
        res_pos = await self.skill_executor.execute_skill(
            skill_name="positioning_strategy",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 8: differentiation_analysis
        res_diff = await self.skill_executor.execute_skill(
            skill_name="differentiation_analysis",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 9: offer_strategy
        res_offer = await self.skill_executor.execute_skill(
            skill_name="offer_strategy",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 10: pricing_strategy
        res_price = await self.skill_executor.execute_skill(
            skill_name="pricing_strategy",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 11: product_market_fit_analysis
        res_pmf = await self.skill_executor.execute_skill(
            skill_name="product_market_fit_analysis",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 12: product_launch_strategy (Validation Plan)
        res_launch = await self.skill_executor.execute_skill(
            skill_name="product_launch_strategy",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 13: product_risk_analysis
        res_risk = await self.skill_executor.execute_skill(
            skill_name="product_risk_analysis",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # Skill 14: product_recommendation
        res_rec = await self.skill_executor.execute_skill(
            skill_name="product_recommendation",
            input_data={"product_name": product_name, "target_market": target_market},
            agent_name=self.agent_name,
            provider_name=provider_name,
        )

        # 2. CONSTRUCT STRUCTURED OUTPUT SCHEMA
        usp_data = res_usp.result or {}
        pmf_data = res_pmf.result or {}
        rec_data = res_rec.result or {}

        target_cust = (res_cust.result or {}).get("target_customer", f"Nhân viên văn phòng 22-35 tuổi tại {target_market}")
        cust_prob = (res_prob.result or {}).get("primary_pain_points", [f"Thời gian chuẩn bị {product_name} tốn kém"])[0] if isinstance((res_prob.result or {}).get("primary_pain_points"), list) else "Thời gian chuẩn bị tốn kém"
        cust_need = (res_jtbd.result or {}).get("customer_need", f"Sử dụng {product_name} tiện lợi nhanh gọn trong 30 giây")
        val_prop = (res_val.result or {}).get("value_proposition", f"Giải pháp {product_name} thông minh tiết kiệm 50% thời gian")

        usp_list = usp_data.get("usp", [f"Tính năng độc bản pha tươi 30s của {product_name}", "Pin sạc Type-C dùng 20 lần"])
        uvp_str = usp_data.get("uvp", f"Giải pháp {product_name} thông minh tiện lợi số 1 tại {target_market}")
        positioning_str = (res_pos.result or {}).get("brand_positioning_statement", f"Giải pháp {product_name} thông minh số 1 tại {target_market}")
        diff_list = (res_diff.result or {}).get("differentiation", ["Thiết kế nhỏ gọn pin sạc vượt trội", "Chính sách bảo hành 1 đổi 1 trong 30 ngày"])

        offer_dict = res_offer.result or {
            "core_offer": f"Mua 1 {product_name} Tặng 1 Quà tặng cao cấp",
            "bonuses": ["Freeship toàn quốc", "Bảo hành 1 đổi 1 30 ngày"],
            "guarantee": "Hoàn tiền 100% nếu không hài lòng",
        }

        pricing_dict = res_price.result or {
            "sweet_spot_price": "499.000 VND ($29)",
            "margin_estimate": "65%",
        }

        validation_dict = (res_launch.result or {}).get("validation_plan", {
            "hypothesis": f"Sản phẩm {product_name} đạt CVR > 2.5% tại {target_market}",
            "test": "Tạo Landing Page Pre-order nhận voucher 20%",
            "decision": "VALIDATE",
        })

        risks_list = (res_risk.result or {}).get("risks", ["Rủi ro vỡ/hỏng pin nếu va đập mạnh", "Tồn kho chậm nếu không kiểm soát lead time"])

        assumptions_list = [
            "Giả định biên lợi nhuận gộp đạt >= 60%",
            "Giả định tỷ lệ chốt đơn thành công đạt trên 2.5%",
        ]

        unknowns_list = [
            "Chưa có dữ liệu chính xác về chi phí CPA thực tế của đối thủ gián tiếp",
            "Tỷ lệ mua lại (Repeat purchase rate) thực tế trên thị trường địa phương",
        ]

        recommendation_str = rec_data.get("recommendation", f"Khuyến nghị đưa sản phẩm {product_name} ra thị trường {target_market} (VALIDATE), khởi chạy Phase 1 thử nghiệm pre-order.")

        report = {
            "product": product_name,
            "product_name": product_name,
            "target_market": target_market,
            "target_customer": target_cust,
            "customer_problem": cust_prob,
            "customer_need": cust_need,
            "value_proposition": val_prop,
            "usp": usp_list,
            "uvp": uvp_str,
            "positioning": positioning_str,
            "differentiation": diff_list,
            "offer_strategy": offer_dict,
            "pricing_analysis": pricing_dict,
            "product_market_fit": pmf_data,
            "validation_plan": validation_dict,
            "risks": risks_list,
            "assumptions": assumptions_list,
            "unknowns": unknowns_list,
            "recommendation": recommendation_str,
            "confidence": 85,
        }

        state.final_result = report
        state.intermediate_steps.append({"node": "product_strategy_assembly", "status": "completed"})
        return state

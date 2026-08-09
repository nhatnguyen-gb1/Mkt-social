import logging
from typing import List, Optional, Dict, Any
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.tools.base import BaseTool
from app.core.llm.base import BaseLLMProvider
from app.schemas.campaign import AdsAgentResult

logger = logging.getLogger("aimos.agents.ads")


class AdsAgent(BaseAgent):
    """
    Ads AI Agent.
    Transforms marketing strategy and creative assets into campaign parameters, budget allocations,
    and platform-specific targeting criteria (Meta/TikTok).
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tools: Optional[List[BaseTool]] = None,
    ):
        super().__init__(
            llm_provider=llm_provider,
            tools=tools,
            agent_name="AdsAgent",
        )

    async def _node_llm_reasoner(self, state: AgentState) -> AgentState:
        product_name = state.input_data.get("product_name", "Sản phẩm Mới")
        platform = state.input_data.get("target_platform", "META").upper()
        budget = state.input_data.get("total_budget_usd", 200.0)

        prompt = f"""
Bạn là Chuyên gia Tối ưu Quảng cáo Ads Specialist của AIMOS.
Hãy lập thông số cài đặt chiến dịch quảng cáo tối ưu cho:

Sản phẩm: {product_name}
Nền tảng: {platform}
Ngân sách dự kiến: ${budget} USD/ngày

Yêu cầu đầu ra:
1. Tên chiến dịch đề xuất (recommended_campaign_name)
2. Mục tiêu chiến dịch (objective: CONVERSIONS, LEADS, OUTREACH)
3. Ngân sách đề xuất hàng ngày (daily_budget_usd)
4. Tiêu chí nhắm mục tiêu chi tiết (targeting_recommendations: độ tuổi age_range, giới tính gender, sở thích interests, vị trí địa lý locations)
5. Danh sách các Ad Copies mẫu (ad_copy_recommendations: headline, primary_text, call_to_action)
"""

        system_prompt = f"Bạn là Chuyên gia Tối ưu Quảng cáo {platform} Ads chuyên nghiệp cho thương mại điện tử."

        try:
            result_obj: AdsAgentResult = await self.llm_provider.generate_structured(
                prompt=prompt,
                schema_class=AdsAgentResult,
                system_prompt=system_prompt,
            )
            state.final_result = result_obj.model_dump()
        except Exception as e:
            logger.warning(f"LLM structured generation fallback for Ads Agent: {e}")
            fallback_result = AdsAgentResult(
                product_name=product_name,
                target_platform=platform,
                recommended_campaign_name=f"Chiến dịch {product_name} - {platform} Conversions",
                objective="CONVERSIONS",
                daily_budget_usd=budget,
                targeting_recommendations={
                    "age_range": "22-45",
                    "gender": "ALL",
                    "locations": ["Vietnam"],
                    "interests": ["Quà tặng cao cấp", "Mua sắm trực tuyến", "Thực phẩm thượng hạng"],
                },
                ad_copy_recommendations=[
                    {
                        "headline": f"{product_name} - Món Quà Sang Trọng",
                        "primary_text": f"Khám phá bộ sưu tập {product_name} đẳng cấp. Giao hàng tận nơi toàn quốc.",
                        "call_to_action": "SHOP_NOW",
                    }
                ],
            )
            state.final_result = fallback_result.model_dump()

        state.intermediate_steps.append({"node": "llm_reasoner", "status": "completed"})
        return state

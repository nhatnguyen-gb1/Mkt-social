import logging
from typing import List, Optional
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.tools.base import BaseTool
from app.core.llm.base import BaseLLMProvider
from app.schemas.creative import MarketingStrategyResult, AdConcept

logger = logging.getLogger("aimos.agents.strategy")


class MarketingStrategyAgent(BaseAgent):
    """
    Marketing Strategy AI Agent.
    Formulates core brand positioning, target customer segmentation, channel recommendations,
    and distinct advertising concepts (headline, primary text, CTA).
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tools: Optional[List[BaseTool]] = None,
    ):
        super().__init__(
            llm_provider=llm_provider,
            tools=tools,
            agent_name="MarketingStrategyAgent",
        )

    async def _node_llm_reasoner(self, state: AgentState) -> AgentState:
        product_name = state.input_data.get("product_name", "Sản phẩm Mới")
        market_summary = state.input_data.get(
            "market_research_summary", "Thị trường tiềm năng với phân khúc khách hàng đa dạng."
        )

        prompt = f"""
Bạn là Chuyên gia Chiến lược Marketing Senior (Chief Marketing Officer) của AIMOS.
Hãy lập chiến lược marketing và các ý tưởng quảng cáo chi tiết cho sản phẩm:

Tên sản phẩm: {product_name}
Tóm tắt nghiên cứu thị trường: {market_summary}

Yêu cầu đầu ra:
1. Định vị thương hiệu cốt lõi (brand_positioning)
2. Các phân khúc mục tiêu chính (target_segments)
3. Danh sách các Ý tưởng Quảng cáo (ad_concepts: góc độ angle_title, tiêu đề headline, văn bản chính primary_text, câu kêu gọi call_to_action)
4. Các kênh truyền thông đề xuất (recommended_channels)
"""

        system_prompt = "Bạn là Chuyên gia Chiến lược Marketing cấp cao chuyên lập chiến lược quảng cáo thương mại điện tử."

        try:
            result_obj: MarketingStrategyResult = await self.llm_provider.generate_structured(
                prompt=prompt,
                schema_class=MarketingStrategyResult,
                system_prompt=system_prompt,
            )
            state.final_result = result_obj.model_dump()
        except Exception as e:
            logger.warning(f"LLM structured generation fallback for Strategy Agent: {e}")
            fallback_result = MarketingStrategyResult(
                product_name=product_name,
                brand_positioning=f"{product_name} - Sự lựa chọn đẳng cấp và đáng tin cậy hàng đầu thị trường.",
                target_segments=[
                    "Khách hàng cá nhân tìm kiếm chất lượng cao và trải nghiệm độc đáo.",
                    "Khách hàng doanh nghiệp mua làm quà tặng đối tác sang trọng.",
                ],
                ad_concepts=[
                    AdConcept(
                        angle_title="Góc độ Quà tặng Sang Trọng",
                        headline=f"{product_name} - Món Quà Trao Gửi Thành Ý",
                        primary_text=f"Khám phá bộ sưu tập {product_name} thiết kế tinh tế, thể hiện sự trân trọng tuyệt đối dành cho người nhận.",
                        call_to_action="Đặt Hàng Ngay",
                    ),
                    AdConcept(
                        angle_title="Góc độ Chất Lượng Đỉnh Cao",
                        headline=f"Trải Nghiệm {product_name} Chuẩn Thượng Hạng",
                        primary_text=f"Cam kết nguyên liệu tự nhiên cao cấp. {product_name} mang đến hương vị chuẩn vị khó quên.",
                        call_to_action="Tìm Hiểu Thêm",
                    ),
                ],
                recommended_channels=["Facebook Feed", "Instagram Reels", "TikTok Ads"],
            )
            state.final_result = fallback_result.model_dump()

        state.intermediate_steps.append({"node": "llm_reasoner", "status": "completed"})
        return state

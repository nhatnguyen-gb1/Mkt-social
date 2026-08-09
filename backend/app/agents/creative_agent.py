import logging
from typing import List, Optional
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.tools.base import BaseTool
from app.core.llm.base import BaseLLMProvider
from app.schemas.creative import (
    CreativeGenerationResult,
    ImagePromptDetail,
    VideoScriptDetail,
)

logger = logging.getLogger("aimos.agents.creative")


class CreativeAgent(BaseAgent):
    """
    Creative AI Agent.
    Transforms marketing strategy and ad concepts into detailed visual image prompts
    and short-form video scripts (Meta Reels, TikTok).
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tools: Optional[List[BaseTool]] = None,
    ):
        super().__init__(
            llm_provider=llm_provider,
            tools=tools,
            agent_name="CreativeAgent",
        )

    async def _node_llm_reasoner(self, state: AgentState) -> AgentState:
        product_name = state.input_data.get("product_name", "Sản phẩm Mới")
        strategy_summary = state.input_data.get(
            "strategy_summary", "Định vị sản phẩm cao cấp, tập trung vào quà tặng sang trọng."
        )

        prompt = f"""
Bạn là Giám đốc Sáng tạo (Creative Director) của AIMOS.
Hãy thiết kế các Visual Prompts tạo ảnh và Kịch bản Video quảng cáo ngắn cho sản phẩm:

Tên sản phẩm: {product_name}
Chiến lược Marketing: {strategy_summary}

Yêu cầu đầu ra:
1. Danh sách Image Prompts tạo ảnh quảng cáo (image_prompts: tiêu đề title, visual_prompt tiếng Anh chi tiết, phong cách style, tỷ lệ aspect_ratio, bảng màu color_palette)
2. Danh sách Video Scripts kịch bản video ngắn (video_scripts: tiêu đề title, thời lượng target_duration_sec, danh sách các cảnh scene_descriptions, kịch bản lời thoại/phụ đề voiceover_script)
"""

        system_prompt = "Bạn là Giám đốc Sáng tạo nghệ thuật chuyên sản xuất visual ad creatives cho các chiến dịch quảng cáo kỹ thuật số."

        try:
            result_obj: CreativeGenerationResult = await self.llm_provider.generate_structured(
                prompt=prompt,
                schema_class=CreativeGenerationResult,
                system_prompt=system_prompt,
            )
            state.final_result = result_obj.model_dump()
        except Exception as e:
            logger.warning(f"LLM structured generation fallback for Creative Agent: {e}")
            fallback_result = CreativeGenerationResult(
                product_name=product_name,
                image_prompts=[
                    ImagePromptDetail(
                        title="Hero Banner Cao Cấp",
                        visual_prompt=f"Studio photo of luxury {product_name} gift box on warm dark wood table with ambient golden lighting, 8k resolution, cinematic composition, professional commercial photography",
                        style="vivid",
                        aspect_ratio="1:1",
                        color_palette="Gold & Dark Navy",
                    ),
                    ImagePromptDetail(
                        title="Visual LIFESTYLE Sang Trọng",
                        visual_prompt=f"Close up elegant hand opening premium {product_name} package, soft natural sunlight background, warm tones, high aesthetic advertising photography",
                        style="natural",
                        aspect_ratio="9:16",
                        color_palette="Warm Golden Light",
                    ),
                ],
                video_scripts=[
                    VideoScriptDetail(
                        title="Video TikTok 15s - Mở Hộp Quà Tặng",
                        target_duration_sec=15,
                        scene_descriptions=[
                            "Cảnh 1 (0-3s): Góc cận cảnh tay gõ nhẹ lên hộp quà thiết kế tinh xảo.",
                            "Cảnh 2 (3-9s): Mở hộp từ từ, hiệu ứng ánh sáng dịu làm nổi bật sản phẩm.",
                            "Cảnh 3 (9-15s): Thưởng thức sản phẩm và hiển thị thông điệp ưu đãi đặc biệt.",
                        ],
                        voiceover_script=f"Bạn đang tìm món quà hoàn hảo cho dịp đặc biệt? Khám phá ngay {product_name} sang trọng hôm nay!",
                    )
                ],
            )
            state.final_result = fallback_result.model_dump()

        state.intermediate_steps.append({"node": "llm_reasoner", "status": "completed"})
        return state

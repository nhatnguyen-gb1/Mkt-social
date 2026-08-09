import json
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from app.core.llm.base import BaseLLMProvider, LLMUsageRecord

logger = logging.getLogger("aimos.llm.mock")
T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "mock-model-v1"):
        self.model_name = model_name
        self._last_usage = LLMUsageRecord(
            provider="mock",
            model_name=self.model_name,
            prompt_tokens=50,
            completion_tokens=150,
            total_tokens=200,
            estimated_cost_usd=0.0,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        logger.info(f"[MOCK LLM GENERATE] Prompt length: {len(prompt)}")
        return f"[MOCK LLM RESPONSE]: Processed prompt '{prompt[:60]}...' with zero cost."

    async def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> T:
        logger.info(f"[MOCK LLM STRUCTURED] Generating {schema_class.__name__}")

        target_schema = kwargs.get("schema", schema_class)
        schema_name = target_schema.__name__

        if schema_name == "MarketResearchResult":
            data = {
                "product_name": "Sample Product",
                "target_market": "Global",
                "summary": "Mô phỏng phân tích thị trường bằng Mock LLM Provider (Miễn phí 100%). Dữ liệu thể hiện khả năng tạo dữ liệu đầu ra có cấu trúc (Structured JSON Output).",
                "opportunities": [
                    "Nhu cầu mua sắm trực tuyến tăng cao trong phân khúc trẻ.",
                    "Khả năng mở rộng trên các kênh nội dung ngắn (Short-form Video).",
                    "Định vị thương hiệu cao cấp tạo biên lợi nhuận lớn."
                ],
                "risks": [
                    "Cạnh tranh gay gắt từ các thương hiệu nội địa.",
                    "Chi phí quảng cáo (CPM) trên các nền tảng có xu hướng tăng."
                ],
                "target_audience": "Nhóm khách hàng nam/nữ độ tuổi 22-38, quan tâm đến chất lượng và trải nghiệm.",
                "recommended_marketing_angles": [
                    "Góc độ quà tặng sang trọng (Gifting Angle)",
                    "Góc độ trải nghiệm độc bản (Exclusivity Angle)",
                    "Góc độ cam kết chất lượng (Quality Commitment)"
                ]
            }
            for line in prompt.split("\n"):
                if "Sản phẩm:" in line or "Product:" in line:
                    data["product_name"] = line.split(":", 1)[1].strip()
                if "Thị trường:" in line or "Market:" in line:
                    data["target_market"] = line.split(":", 1)[1].strip()
            return target_schema.model_validate(data)

        elif schema_name == "MarketingStrategyResult":
            data = {
                "product_name": "Sample Product",
                "brand_positioning": "Định vị thương hiệu hàng đầu về chất lượng và quà tặng ngoại giao cao cấp.",
                "target_segments": [
                    "Khách hàng cá nhân tìm kiếm quà tặng tinh tế.",
                    "Khách hàng doanh nghiệp mua làm quà tặng đối tác."
                ],
                "ad_concepts": [
                    {
                        "angle_title": "Góc độ Quà Tặng Sang Trọng",
                        "headline": "Món Quà Trao Gửi Thành Ý",
                        "primary_text": "Bộ sưu tập thiết kế tinh tế, thể hiện sự trân trọng tuyệt đối dành cho người nhận.",
                        "call_to_action": "Đặt Hàng Ngay"
                    },
                    {
                        "angle_title": "Góc độ Chất Lượng Đỉnh Cao",
                        "headline": "Trải Nghiệm Thượng Hạng",
                        "primary_text": "Cam kết nguyên liệu tự nhiên cao cấp, chuẩn vị khó quên.",
                        "call_to_action": "Tìm Hiểu Thêm"
                    }
                ],
                "recommended_channels": ["Facebook Feed", "Instagram Reels", "TikTok Ads"]
            }
            for line in prompt.split("\n"):
                if "Tên sản phẩm:" in line:
                    data["product_name"] = line.split(":", 1)[1].strip()
            return target_schema.model_validate(data)

        elif schema_name == "CreativeGenerationResult":
            data = {
                "product_name": "Sample Product",
                "image_prompts": [
                    {
                        "title": "Hero Visual Cao Cấp",
                        "visual_prompt": "Studio photo of luxury gift box on warm dark wood table with ambient golden lighting, 8k resolution, cinematic commercial photography",
                        "style": "vivid",
                        "aspect_ratio": "1:1",
                        "color_palette": "Gold & Navy"
                    },
                    {
                        "title": "Lifestyle Visual Thượng Hạng",
                        "visual_prompt": "Close up hands opening premium product package with soft natural sunlight background, warm aesthetic",
                        "style": "natural",
                        "aspect_ratio": "9:16",
                        "color_palette": "Warm Golden Light"
                    }
                ],
                "video_scripts": [
                    {
                        "title": "Video TikTok 15s - Mở Hộp Quà Tặng",
                        "target_duration_sec": 15,
                        "scene_descriptions": [
                            "Cảnh 1 (0-3s): Tay gõ nhẹ lên hộp quà thiết kế tinh xảo.",
                            "Cảnh 2 (3-9s): Mở hộp từ từ, ánh sáng dịu làm nổi bật sản phẩm.",
                            "Cảnh 3 (9-15s): Thưởng thức sản phẩm và hiển thị thông điệp ưu đãi."
                        ],
                        "voiceover_script": "Bạn đang tìm món quà hoàn hảo cho dịp đặc biệt? Khám phá ngay hôm nay!"
                    }
                ]
            }
            for line in prompt.split("\n"):
                if "Tên sản phẩm:" in line:
                    data["product_name"] = line.split(":", 1)[1].strip()
            return target_schema.model_validate(data)

        elif schema_name == "AdsAgentResult":
            data = {
                "product_name": "Sample Product",
                "target_platform": "META",
                "recommended_campaign_name": "Chiến dịch Mới - Conversions",
                "objective": "CONVERSIONS",
                "daily_budget_usd": 150.0,
                "targeting_recommendations": {
                    "age_range": "22-45",
                    "gender": "ALL",
                    "locations": ["Vietnam"],
                    "interests": ["Quà tặng cao cấp", "Mua sắm trực tuyến", "Thực phẩm thượng hạng"],
                },
                "ad_copy_recommendations": [
                    {
                        "headline": "Món Quà Sang Trọng",
                        "primary_text": "Khám phá bộ sưu tập quà tặng đẳng cấp. Giao hàng toàn quốc.",
                        "call_to_action": "SHOP_NOW",
                    }
                ],
            }
            for line in prompt.split("\n"):
                if "Sản phẩm:" in line:
                    data["product_name"] = line.split(":", 1)[1].strip()
                if "Nền tảng:" in line:
                    data["target_platform"] = line.split(":", 1)[1].strip().upper()
            return target_schema.model_validate(data)

        elif schema_name == "OptimizationAgentResult":
            data = {
                "campaign_id": "00000000-0000-0000-0000-000000000000",
                "performance_assessment": "Chiến dịch đạt hiệu năng xuất sắc với CTR 3.6% và CPA $2.5 USD.",
                "overall_health": "HEALTHY",
                "recommendations": [
                    {
                        "action_type": "SCALE_BUDGET",
                        "target_entity": "Chiến dịch Hiện Tại",
                        "reasoning": "CPA thực tế $2.5 thấp hơn Target CPA $5.0. Đề xuất tăng ngân sách 20%.",
                        "recommended_change": {"increase_budget_percent": 20.0},
                        "requires_human_approval": True,
                    }
                ],
            }
            return target_schema.model_validate(data)

        # Generic fallback
        dummy_dict = {}
        for field_name, field_info in target_schema.model_fields.items():
            if field_info.annotation == str:
                dummy_dict[field_name] = f"Mock {field_name}"
            elif field_info.annotation == list or getattr(field_info.annotation, "__origin__", None) == list:
                dummy_dict[field_name] = [f"Mock item 1 for {field_name}"]
            elif field_info.annotation == int:
                dummy_dict[field_name] = 100
            elif field_info.annotation == float:
                dummy_dict[field_name] = 99.9
            else:
                dummy_dict[field_name] = None
        return target_schema.model_validate(dummy_dict)

    def get_provider_name(self) -> str:
        return "mock"

    def get_last_usage(self) -> LLMUsageRecord:
        return self._last_usage

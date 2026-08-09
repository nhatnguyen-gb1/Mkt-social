from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ----------------------------------------------------
# Marketing Strategy Schemas
# ----------------------------------------------------

class AdConcept(BaseModel):
    angle_title: str = Field(..., description="Name of marketing hook/angle")
    headline: str = Field(..., description="Ad Headline text")
    primary_text: str = Field(..., description="Main caption/copy for ad placement")
    call_to_action: str = Field(..., description="CTA text, e.g. Shop Now, Learn More")


class MarketingStrategyResult(BaseModel):
    product_name: str = Field(..., description="Product title")
    brand_positioning: str = Field(..., description="Core brand positioning statement")
    target_segments: List[str] = Field(default_factory=list, description="Target customer segments")
    ad_concepts: List[AdConcept] = Field(default_factory=list, description="List of generated ad concepts")
    recommended_channels: List[str] = Field(default_factory=list, description="Top channels (Meta, TikTok, etc.)")


class StrategyRequest(BaseModel):
    product_name: str = Field("Bánh Trung Thu", min_length=1, max_length=255)
    market_research_summary: Optional[str] = Field(
        None, description="Summary from Phase 3 Research Agent or manual input"
    )
    provider: Optional[str] = Field("mock", description="LLM provider: mock, openai, anthropic, gemini")


# ----------------------------------------------------
# Creative Generation Schemas
# ----------------------------------------------------

class ImagePromptDetail(BaseModel):
    title: str = Field(..., description="Title of the creative visual concept")
    visual_prompt: str = Field(..., description="Detailed AI image generation prompt")
    style: str = Field("vivid", description="Style, e.g. vivid, natural, cinematic, photo")
    aspect_ratio: str = Field("1:1", description="Aspect ratio, e.g. 1:1, 9:16, 16:9")
    color_palette: str = Field("Warm & Modern", description="Dominant color scheme")


class VideoScriptDetail(BaseModel):
    title: str = Field(..., description="Title of the video concept")
    target_duration_sec: int = Field(15, description="Target video length in seconds")
    scene_descriptions: List[str] = Field(default_factory=list, description="Scene visual breakdown")
    voiceover_script: str = Field(..., description="Spoken voiceover or text overlay script")


class CreativeGenerationResult(BaseModel):
    product_name: str = Field(..., description="Product title")
    image_prompts: List[ImagePromptDetail] = Field(default_factory=list)
    video_scripts: List[VideoScriptDetail] = Field(default_factory=list)


class CreativeRequest(BaseModel):
    product_name: str = Field("Bánh Trung Thu", min_length=1, max_length=255)
    strategy_summary: Optional[str] = Field(None, description="Marketing strategy details")
    provider: Optional[str] = Field("mock", description="LLM provider: mock, openai, anthropic, gemini")


# ----------------------------------------------------
# Asset Management Schemas
# ----------------------------------------------------

class ImageGenerateRequest(BaseModel):
    product_id: Optional[UUID] = Field(None, description="Associated product ID")
    title: str = Field("Quảng cáo Bánh Trung Thu - Visual 1", max_length=255)
    prompt: str = Field("High resolution premium mooncake gift box with golden lighting, cinematic 8k", min_length=5)
    size: str = Field("1024x1024", description="Image resolution size")
    style: str = Field("vivid", description="Image style")
    provider: Optional[str] = Field("mock", description="Media generator provider: mock, openai")


class AssetCreate(BaseModel):
    product_id: Optional[UUID] = None
    agent_run_id: Optional[UUID] = None
    asset_type: str = "IMAGE"
    title: str
    file_url: Optional[str] = None
    prompt: Optional[str] = None
    asset_metadata: Optional[Dict[str, Any]] = None
    status: str = "DRAFT"


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: Optional[UUID] = None
    agent_run_id: Optional[UUID] = None
    asset_type: str
    title: str
    file_url: Optional[str] = None
    prompt: Optional[str] = None
    asset_metadata: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime


class AssetListResponse(BaseModel):
    total: int
    items: List[AssetResponse]

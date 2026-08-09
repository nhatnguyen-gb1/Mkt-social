from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ----------------------------------------------------
# Ad Schemas
# ----------------------------------------------------

class AdCreate(BaseModel):
    name: str = Field(..., max_length=255)
    asset_id: Optional[UUID] = None
    headline: Optional[str] = Field(None, max_length=255)
    primary_text: Optional[str] = None
    call_to_action: Optional[str] = Field("SHOP_NOW", max_length=50)


class AdResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ad_set_id: UUID
    asset_id: Optional[UUID] = None
    name: str
    headline: Optional[str] = None
    primary_text: Optional[str] = None
    call_to_action: Optional[str] = None
    status: str
    external_ad_id: Optional[str] = None
    created_at: datetime


# ----------------------------------------------------
# AdSet Schemas
# ----------------------------------------------------

class AdSetCreate(BaseModel):
    name: str = Field(..., max_length=255)
    targeting: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Targeting criteria (age, location, interests)")
    daily_budget: float = Field(50.0, ge=1.0)
    ads: List[AdCreate] = Field(default_factory=list)


class AdSetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    name: str
    targeting: Optional[Dict[str, Any]] = None
    daily_budget: float
    status: str
    external_adset_id: Optional[str] = None
    ads: List[AdResponse] = Field(default_factory=list)
    created_at: datetime


# ----------------------------------------------------
# Campaign Schemas
# ----------------------------------------------------

class CampaignCreate(BaseModel):
    product_id: Optional[UUID] = None
    name: str = Field("Chiến dịch Bánh Trung Thu - Meta Ads", max_length=255)
    platform: str = Field("META", description="Target ad platform: META, TIKTOK")
    objective: str = Field("CONVERSIONS", description="Campaign objective: OUTREACH, CONVERSIONS, LEADS")
    daily_budget: float = Field(100.0, ge=1.0, description="Total daily campaign budget in USD")
    ad_sets: List[AdSetCreate] = Field(default_factory=list)


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: Optional[UUID] = None
    name: str
    platform: str
    objective: str
    daily_budget: float
    status: str
    external_campaign_id: Optional[str] = None
    campaign_metadata: Optional[Dict[str, Any]] = None
    ad_sets: List[AdSetResponse] = Field(default_factory=list)
    created_at: datetime


class CampaignListResponse(BaseModel):
    total: int
    items: List[CampaignResponse]


class PublishResponse(BaseModel):
    campaign_id: UUID
    platform: str
    status: str
    external_campaign_id: str
    is_mock: bool
    message: str


# ----------------------------------------------------
# AdsAgent Schemas
# ----------------------------------------------------

class AdsAgentRequest(BaseModel):
    product_name: str = Field("Bánh Trung Thu", min_length=1)
    target_platform: str = Field("META", description="Target platform: META or TIKTOK")
    total_budget_usd: float = Field(200.0, ge=10.0)
    provider: Optional[str] = Field("mock", description="LLM provider: mock, openai, anthropic, gemini")


class AdsAgentResult(BaseModel):
    product_name: str
    target_platform: str
    recommended_campaign_name: str
    objective: str
    daily_budget_usd: float
    targeting_recommendations: Dict[str, Any]
    ad_copy_recommendations: List[Dict[str, str]]

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CampaignMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    platform: str
    recorded_at: datetime
    impressions: int
    clicks: int
    spend_usd: float
    conversions: int
    ctr: float
    cpa_usd: float
    roas: float


class CampaignAnalyticsSummaryResponse(BaseModel):
    campaign_id: UUID
    platform: str
    total_impressions: int
    total_clicks: int
    total_spend_usd: float
    total_conversions: int
    average_ctr: float
    average_cpa_usd: float
    average_roas: float
    metrics_history: List[CampaignMetricResponse]


class OptimizationRecommendation(BaseModel):
    action_type: str = Field(..., description="Action type: PAUSE_AD, SCALE_BUDGET, REDUCE_BUDGET, REFRESH_CREATIVE")
    target_entity: str = Field(..., description="Target campaign or ad set name/ID")
    reasoning: str = Field(..., description="Justification based on metrics analysis")
    recommended_change: Dict[str, Any] = Field(default_factory=dict, description="Proposed parameter updates")
    requires_human_approval: bool = Field(True, description="Whether human approval is required before execution")


class OptimizationAgentRequest(BaseModel):
    campaign_id: UUID
    target_cpa_usd: Optional[float] = Field(5.0, ge=0.5, description="Target CPA limit in USD")
    min_ctr_percent: Optional[float] = Field(2.0, ge=0.1, description="Minimum acceptable CTR percentage")
    provider: Optional[str] = Field("mock", description="LLM provider: mock, openai, anthropic, gemini")


class OptimizationAgentResult(BaseModel):
    campaign_id: UUID
    performance_assessment: str
    overall_health: str = Field(..., description="Health rating: HEALTHY, WARNING, CRITICAL")
    recommendations: List[OptimizationRecommendation]

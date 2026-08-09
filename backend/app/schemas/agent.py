from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class MarketResearchResult(BaseModel):
    product_name: str = Field(..., description="Name of the analyzed product")
    target_market: str = Field(..., description="Target geographical or demographic market")
    summary: str = Field(..., description="Executive summary of market opportunity")
    opportunities: List[str] = Field(default_factory=list, description="Key growth opportunities")
    risks: List[str] = Field(default_factory=list, description="Market risks and entry barriers")
    target_audience: str = Field(..., description="Customer persona definition")
    recommended_marketing_angles: List[str] = Field(
        default_factory=list, description="Top marketing hooks/angles for ad creatives"
    )


class AgentResearchRequest(BaseModel):
    product_name: str = Field("Bánh Trung Thu", min_length=1, max_length=255, description="Product or brand title")
    target_market: str = Field("Vietnam", max_length=100, description="Target market country or region")
    provider: Optional[str] = Field("mock", description="LLM provider choice: mock, openai, anthropic, gemini")


class AgentRunResponse(BaseModel):
    run_id: UUID
    agent_name: str
    status: str
    provider_used: str
    input_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime

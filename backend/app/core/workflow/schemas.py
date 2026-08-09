from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class WorkflowExecutionStep(BaseModel):
    step_number: int
    step_name: str
    agent_or_service: str
    status: str  # COMPLETED, PENDING_APPROVAL, SKIPPED, FAILED
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0


class WorkflowPipelineRequest(BaseModel):
    product_name: str = Field("Bánh Trung Thu Thượng Hạng", min_length=1)
    target_market: str = Field("Vietnam", min_length=1)
    platform: str = Field("META", description="Target ad platform: META, TIKTOK")
    daily_budget_usd: float = Field(150.0, ge=10.0)
    provider: Optional[str] = Field("mock", description="LLM Provider: mock, openai, anthropic, gemini")
    auto_publish: bool = Field(False, description="Attempt auto-publish (will route through Safety Engine)")


class WorkflowPipelineResponse(BaseModel):
    workflow_id: UUID
    product_name: str
    status: str  # COMPLETED, PENDING_APPROVAL, FAILED
    steps_executed: List[WorkflowExecutionStep]
    final_campaign_id: Optional[UUID] = None
    approval_request_id: Optional[UUID] = None
    summary: str
    created_at: datetime

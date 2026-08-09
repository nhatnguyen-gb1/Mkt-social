from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PolicyRuleCreate(BaseModel):
    name: str = Field(..., max_length=255)
    rule_type: str = Field(..., description="Rule type: MAX_DAILY_BUDGET, RESTRICTED_KEYWORDS, REQUIRE_APPROVAL_FOR_PUBLISH")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Rule evaluation parameters")
    is_active: bool = Field(True, description="Active status")


class PolicyRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    rule_type: str
    parameters: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime


class PolicyRuleListResponse(BaseModel):
    total: int
    items: List[PolicyRuleResponse]


class ApprovalRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: Optional[UUID] = None
    requested_action: str
    requested_by: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime


class ApprovalRequestListResponse(BaseModel):
    total: int
    items: List[ApprovalRequestResponse]


class ActionReviewRequest(BaseModel):
    reviewer_id: Optional[str] = Field("human_marketer", description="Identifier of the human reviewer")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejecting request")

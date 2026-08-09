from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.lead_qualification_agent import LeadQualificationAgent
from app.core.llm.factory import LLMProviderFactory

router = APIRouter(prefix="/api/v1/agents/lead-qualification", tags=["Lead Qualification Agent"])


class LeadQualificationAnalyzeRequest(BaseModel):
    lead: Optional[Dict[str, Any]] = Field(
        default={"source": "Facebook Ads", "phone": "+84901234567"},
        json_schema_extra={
            "example": {"source": "Facebook Ads", "phone": "+84901234567", "campaign": "BDS 2026"}
        },
    )
    conversation: Optional[List[Dict[str, Any]]] = Field(
        default=[{"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ khoảng 3 tỷ."}],
        json_schema_extra={
            "example": [
                {"speaker": "CUSTOMER", "text": "Anh đang tìm căn hộ 2 phòng ngủ."},
                {"speaker": "CUSTOMER", "text": "Ngân sách khoảng 3 tỷ."},
                {"speaker": "CUSTOMER", "text": "Cuối tháng anh muốn mua."}
            ]
        },
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        json_schema_extra={"example": {"domain": "REAL_ESTATE"}},
    )
    provider: Optional[str] = Field(
        default="mock",
        json_schema_extra={"example": "mock"},
    )


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_lead_qualification(request: LeadQualificationAnalyzeRequest):
    """
    POST /api/v1/agents/lead-qualification/analyze
    
    Executes AI Pre-Sales / Lead Qualification Specialist analysis:
    - Extracts BANT attributes (Budget, Need, Product, Timeline, Location, Financing).
    - Identifies missing critical information & selects Next Best Question.
    - Computes LeadScore (0-100) & classifies (HOT, WARM, COLD, INVALID, UNKNOWN).
    - Constructs structured Sales Handoff object.
    """
    try:
        provider = LLMProviderFactory.get_provider(request.provider or "mock")
        agent = LeadQualificationAgent(llm_provider=provider)

        payload = {
            "lead": request.lead or {},
            "conversation": request.conversation or [],
            "context": request.context or {},
        }

        state = await agent.run(payload)
        return state.final_result or {}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Lead Qualification Agent execution failed: {str(exc)}",
        )

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.agents.market_research_agent import MarketResearchAgent
from app.core.llm.factory import LLMProviderFactory

router = APIRouter(prefix="/api/v1/agents/market-research", tags=["Market Research Agent"])


class ResearchAnalyzeRequest(BaseModel):
    research_question: str = Field(
        ...,
        json_schema_extra={
            "example": "Đánh giá cơ hội bán một sản phẩm mới trên TikTok Shop Philippines."
        },
    )
    market: Optional[str] = Field(
        default="Philippines",
        json_schema_extra={"example": "Philippines"},
    )
    product: Optional[str] = Field(
        default="Sản phẩm Mẫu",
        json_schema_extra={"example": "Máy pha cà phê mini"},
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default={},
        json_schema_extra={"example": {"budget": 500}},
    )
    provider: Optional[str] = Field(
        default="mock",
        json_schema_extra={"example": "mock"},
    )


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_market_research(request: ResearchAnalyzeRequest):
    """
    POST /api/v1/agents/market-research/analyze
    
    Executes Senior Market Research Agent analysis following 10-step methodology,
    Evidence Classification System (Fact/Evidence/Inference/Assumption/Unknown),
    and Configurable Opportunity Scoring Framework.
    """
    try:
        provider = LLMProviderFactory.get_provider(request.provider or "mock")
        agent = MarketResearchAgent(llm_provider=provider)

        payload = {
            "research_question": request.research_question,
            "market": request.market,
            "product": request.product,
            "constraints": request.constraints or {},
        }

        state = await agent.run(payload)
        return state.final_result or {}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Market Research Agent execution failed: {str(exc)}",
        )

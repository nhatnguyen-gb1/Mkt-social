from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.product_agent import ProductAgent
from app.core.llm.factory import LLMProviderFactory

router = APIRouter(prefix="/api/v1/agents/product", tags=["Product Agent"])


class ProductAnalyzeRequest(BaseModel):
    product: Optional[Any] = Field(
        default="Máy pha cà phê mini cá nhân",
        json_schema_extra={
            "example": {"name": "Máy pha cà phê mini cá nhân", "category": "Gia dụng thông minh"}
        },
    )
    market: Optional[str] = Field(
        default="Philippines",
        json_schema_extra={"example": "Philippines"},
    )
    customer_context: Optional[Dict[str, Any]] = Field(
        default={},
        json_schema_extra={"example": {"target_age": "22-35"}},
    )
    research_context: Optional[Dict[str, Any]] = Field(
        default={},
        json_schema_extra={"example": {"demand_level": "HIGH"}},
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
async def analyze_product_strategy(request: ProductAnalyzeRequest):
    """
    POST /api/v1/agents/product/analyze
    
    Executes Senior Product Strategist analysis following 15-step Product Analysis Process,
    Configurable PMF Framework (10 dimensions), Offer Design, Pricing Framework, and Validation Pipeline.
    """
    try:
        provider = LLMProviderFactory.get_provider(request.provider or "mock")
        agent = ProductAgent(llm_provider=provider)

        payload = {
            "product": request.product,
            "market": request.market,
            "customer_context": request.customer_context or {},
            "research_context": request.research_context or {},
            "constraints": request.constraints or {},
        }

        state = await agent.run(payload)
        return state.final_result or {}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Product Agent execution failed: {str(exc)}",
        )

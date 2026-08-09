import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.agents.marketing_lead_agent import MarketingLeadAgent
from app.core.llm.factory import LLMProviderFactory

logger = logging.getLogger("aimos.routes.marketing_lead")
router = APIRouter(prefix="/agents/marketing-lead", tags=["Marketing Lead Agent V1"])


class MarketingLeadAnalyzeRequest(BaseModel):
    objective: str = Field(
        default="Tôi muốn bán một sản phẩm mới trên TikTok Shop Philippines với ngân sách 500 USD.",
        min_length=1,
        description="Mục tiêu kinh doanh hoặc tiếp thị của thương hiệu",
    )
    context: Optional[str] = Field(
        default="E-commerce social commerce launch",
        description="Bối cảnh doanh nghiệp, sản phẩm hoặc nguồn lực hiện có",
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Rào cản ngân sách, thời gian hoặc kênh tiếp thị",
    )
    provider: str = Field(default="mock", description="LLM Provider (mock, openai, anthropic, gemini)")


class SelectedAgentItem(BaseModel):
    task: str
    agent: str
    status: str


class MarketingLeadAnalyzeResponse(BaseModel):
    objective: str
    analysis: str
    strategy: str
    task_plan: List[str]
    selected_agents: List[SelectedAgentItem]
    facts: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    review_summary: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: int = 0


@router.post("/analyze", response_model=MarketingLeadAnalyzeResponse)
async def analyze_marketing_objective(req: MarketingLeadAnalyzeRequest):
    """
    Kích hoạt AI Head of Marketing (Marketing Lead Agent V1) để:
    - Phân tích bài toán kinh doanh
    - Lập Task Plan phân rã công việc
    - Điều phối Sub-agents (MarketResearch, Strategy, Creative, Ads, Optimization)
    - Thực thi Output Review Framework thẩm định chất lượng Sub-agents
    - Đưa ra báo cáo phân tách Fact, Assumption, Unknown & Recommendations cuối cùng.
    """
    try:
        provider = LLMProviderFactory.get_provider(req.provider)
        agent = MarketingLeadAgent(llm_provider=provider)

        input_data = {
            "objective": req.objective,
            "context": req.context,
            "constraints": req.constraints,
        }

        agent_state = await agent.run(input_data)
        if agent_state.status == "FAILED":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Marketing Lead Agent failed execution: {agent_state.error_message}",
            )

        res = agent_state.final_result or {}

        return MarketingLeadAnalyzeResponse(
            objective=res.get("objective", req.objective),
            analysis=res.get("analysis", ""),
            strategy=res.get("strategy", ""),
            task_plan=res.get("task_plan", []),
            selected_agents=[
                SelectedAgentItem(task=item.get("task", ""), agent=item.get("agent", ""), status=item.get("status", ""))
                for item in res.get("selected_agents", [])
            ],
            facts=res.get("facts", []),
            assumptions=res.get("assumptions", []),
            unknowns=res.get("unknowns", []),
            recommendations=res.get("recommendations", []),
            review_summary=res.get("review_summary", {}),
            execution_time_ms=getattr(agent_state, "execution_time_ms", 0),
        )

    except Exception as exc:
        logger.exception(f"Error running Marketing Lead Agent: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running Marketing Lead Agent: {str(exc)}",
        )

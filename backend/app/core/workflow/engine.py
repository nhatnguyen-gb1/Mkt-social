import time
import uuid
import logging
from typing import List, Optional
from app.models.base import utc_now
from app.services.agent_service import AgentService
from app.services.campaign_service import CampaignService
from app.services.analytics_service import AnalyticsService
from app.schemas.agent import AgentResearchRequest
from app.schemas.creative import StrategyRequest, CreativeRequest
from app.schemas.campaign import AdsAgentRequest, CampaignCreate, AdSetCreate, AdCreate
from app.schemas.analytics import OptimizationAgentRequest
from app.core.workflow.schemas import (
    WorkflowPipelineRequest,
    WorkflowPipelineResponse,
    WorkflowExecutionStep,
)

logger = logging.getLogger("aimos.workflow.engine")


class WorkflowEngine:
    """
    Core Workflow Orchestration Engine for AIMOS.
    Executes the End-to-End AI Marketing Lifecycle Pipeline:
    Input -> Market Research -> Strategy -> Creative -> Ads Setup -> Safety Check -> Approval Gate.
    """

    def __init__(
        self,
        agent_service: AgentService,
        campaign_service: CampaignService,
        analytics_service: AnalyticsService,
    ):
        self.agent_service = agent_service
        self.campaign_service = campaign_service
        self.analytics_service = analytics_service

    async def execute_full_marketing_pipeline(
        self, request: WorkflowPipelineRequest, actor_id: Optional[str] = None
    ) -> WorkflowPipelineResponse:
        workflow_id = uuid.uuid4()
        logger.info(f"Executing AIMOS Master Workflow '{workflow_id}' for product '{request.product_name}'...")
        
        steps: List[WorkflowExecutionStep] = []
        step_idx = 1
        provider = request.provider or "mock"

        # ----------------------------------------------------
        # Step 1: Market Research Agent
        # ----------------------------------------------------
        s1_start = time.time()
        res_run = await self.agent_service.run_market_research(
            AgentResearchRequest(
                product_name=request.product_name,
                target_market=request.target_market,
                provider=provider,
            ),
            actor_id=actor_id,
        )
        steps.append(
            WorkflowExecutionStep(
                step_number=step_idx,
                step_name="Market Research Analysis",
                agent_or_service="MarketResearchAgent",
                status=res_run.status,
                input_payload={"product_name": request.product_name, "market": request.target_market},
                output_payload=res_run.result,
                execution_time_ms=int((time.time() - s1_start) * 1000),
            )
        )
        step_idx += 1

        # ----------------------------------------------------
        # Step 2: Marketing Strategy Agent
        # ----------------------------------------------------
        s2_start = time.time()
        strat_run = await self.agent_service.run_marketing_strategy(
            StrategyRequest(product_name=request.product_name, provider=provider),
            actor_id=actor_id,
        )
        steps.append(
            WorkflowExecutionStep(
                step_number=step_idx,
                step_name="Marketing Strategy & Positioning",
                agent_or_service="MarketingStrategyAgent",
                status=strat_run.status,
                input_payload={"product_name": request.product_name},
                output_payload=strat_run.result,
                execution_time_ms=int((time.time() - s2_start) * 1000),
            )
        )
        step_idx += 1

        # ----------------------------------------------------
        # Step 3: Creative Generation Agent
        # ----------------------------------------------------
        s3_start = time.time()
        creative_run = await self.agent_service.run_creative_generation(
            CreativeRequest(product_name=request.product_name, provider=provider),
            actor_id=actor_id,
        )
        steps.append(
            WorkflowExecutionStep(
                step_number=step_idx,
                step_name="Creative Visual & Script Production",
                agent_or_service="CreativeAgent",
                status=creative_run.status,
                input_payload={"product_name": request.product_name},
                output_payload=creative_run.result,
                execution_time_ms=int((time.time() - s3_start) * 1000),
            )
        )
        step_idx += 1

        # ----------------------------------------------------
        # Step 4: Ads Structuring Agent
        # ----------------------------------------------------
        s4_start = time.time()
        ads_run = await self.agent_service.run_ads_agent(
            AdsAgentRequest(
                product_name=request.product_name,
                target_platform=request.platform,
                total_budget_usd=request.daily_budget_usd,
                provider=provider,
            ),
            actor_id=actor_id,
        )
        steps.append(
            WorkflowExecutionStep(
                step_number=step_idx,
                step_name="Ads Campaign Structuring",
                agent_or_service="AdsAgent",
                status=ads_run.status,
                input_payload={"platform": request.platform, "budget": request.daily_budget_usd},
                output_payload=ads_run.result,
                execution_time_ms=int((time.time() - s4_start) * 1000),
            )
        )
        step_idx += 1

        # ----------------------------------------------------
        # Step 5: Campaign Persistence in Database
        # ----------------------------------------------------
        s5_start = time.time()
        ads_res = ads_run.result or {}
        cmp_name = ads_res.get("recommended_campaign_name", f"Chiến dịch {request.product_name} - {request.platform}")
        
        cmp_create_req = CampaignCreate(
            name=cmp_name,
            platform=request.platform.upper(),
            objective=ads_res.get("objective", "CONVERSIONS"),
            daily_budget=request.daily_budget_usd,
            ad_sets=[
                AdSetCreate(
                    name=f"Nhóm Ads - {request.target_market}",
                    daily_budget=request.daily_budget_usd,
                    targeting=ads_res.get("targeting_recommendations", {}),
                    ads=[
                        AdCreate(
                            name=f"Ad Creative 1 - {request.product_name}",
                            headline=f"Khám phá {request.product_name}",
                            primary_text=f"Bộ sưu tập {request.product_name} cao cấp.",
                            call_to_action="SHOP_NOW",
                        )
                    ],
                )
            ],
        )
        campaign = await self.campaign_service.create_campaign(cmp_create_req, actor_id=actor_id)
        steps.append(
            WorkflowExecutionStep(
                step_number=step_idx,
                step_name="Campaign Persistence",
                agent_or_service="CampaignService",
                status="COMPLETED",
                input_payload={"campaign_name": campaign.name},
                output_payload={"campaign_id": str(campaign.id), "status": campaign.status},
                execution_time_ms=int((time.time() - s5_start) * 1000),
            )
        )
        step_idx += 1

        # ----------------------------------------------------
        # Step 6: Safety Engine Check & Human Approval Gate
        # ----------------------------------------------------
        s6_start = time.time()
        pub_res = await self.campaign_service.publish_campaign(campaign.id, actor_id=actor_id)
        steps.append(
            WorkflowExecutionStep(
                step_number=step_idx,
                step_name="Safety Policy Check & Approval Gate",
                agent_or_service="PolicyEngine",
                status=pub_res.status,
                input_payload={"campaign_id": str(campaign.id)},
                output_payload={"publish_status": pub_res.status, "message": pub_res.message},
                execution_time_ms=int((time.time() - s6_start) * 1000),
            )
        )

        return WorkflowPipelineResponse(
            workflow_id=workflow_id,
            product_name=request.product_name,
            status=pub_res.status,
            steps_executed=steps,
            final_campaign_id=campaign.id,
            approval_request_id=None,
            summary=f"Full AIMOS Workflow executed 6 steps. Campaign status: '{pub_res.status}'.",
            created_at=utc_now(),
        )

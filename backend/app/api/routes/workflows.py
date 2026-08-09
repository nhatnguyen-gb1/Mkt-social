from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_workflow_engine
from app.core.workflow.engine import WorkflowEngine
from app.core.workflow.schemas import WorkflowPipelineRequest, WorkflowPipelineResponse

router = APIRouter(prefix="/workflows", tags=["Workflow & Orchestration Engine"])


@router.post(
    "/run",
    response_model=WorkflowPipelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Run End-to-End AI Marketing Lifecycle Pipeline",
)
async def run_master_workflow(
    request: WorkflowPipelineRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine),
):
    """
    Executes the complete AIMOS multi-agent marketing pipeline:
    Input -> Research -> Strategy -> Creative -> Ads Setup -> Safety Gate -> Approval Request.
    """
    return await engine.execute_full_marketing_pipeline(request)


@router.get(
    "/definitions",
    status_code=status.HTTP_200_OK,
    summary="List Registered Workflow Templates",
)
async def list_workflow_definitions():
    """
    Retrieves all available master workflow definitions and pipeline templates.
    """
    return {
        "workflows": [
            {
                "name": "E2E_PRODUCT_LAUNCH",
                "description": "Full marketing pipeline from Product Intake to Ad Campaign Setup and Safety Approval.",
                "steps_count": 6,
                "status": "REAL",
            },
            {
                "name": "CREATIVE_REFRESH_CYCLE",
                "description": "Automated ad creative refresh when ad fatigue is detected by OptimizationAgent.",
                "steps_count": 4,
                "status": "SKELETON",
            },
            {
                "name": "ECOMMERCE_CATALOG_SYNC",
                "description": "Inventory and catalog sync pipeline for Shopify & TikTok Shop.",
                "steps_count": 3,
                "status": "SKELETON",
            },
        ]
    }

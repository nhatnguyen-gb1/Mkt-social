from typing import List
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_safety_service
from app.services.safety_service import SafetyService
from app.schemas.safety import PolicyRuleCreate, PolicyRuleResponse, PolicyRuleListResponse

router = APIRouter(prefix="/safety", tags=["Safety & Policy Engine"])


@router.post(
    "/rules",
    response_model=PolicyRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Safety Policy Rule",
)
async def create_policy_rule(
    request: PolicyRuleCreate,
    service: SafetyService = Depends(get_safety_service),
):
    """
    Creates a new safety policy rule (e.g. MAX_DAILY_BUDGET, RESTRICTED_KEYWORDS).
    """
    return await service.create_policy_rule(request)


@router.get(
    "/rules",
    response_model=PolicyRuleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Safety Policy Rules",
)
async def list_policy_rules(
    skip: int = 0,
    limit: int = 100,
    service: SafetyService = Depends(get_safety_service),
):
    """
    Retrieves all configured Safety Policy Rules.
    """
    items = await service.list_policy_rules(skip=skip, limit=limit)
    return PolicyRuleListResponse(total=len(items), items=items)

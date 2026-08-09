import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_approval_service, get_campaign_service
from app.services.approval_service import ApprovalService
from app.services.campaign_service import CampaignService
from app.schemas.safety import (
    ApprovalRequestResponse,
    ApprovalRequestListResponse,
    ActionReviewRequest,
)

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])


@router.get(
    "",
    response_model=ApprovalRequestListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Pending Approval Requests",
)
async def list_pending_approvals(
    skip: int = 0,
    limit: int = 100,
    service: ApprovalService = Depends(get_approval_service),
):
    """
    Retrieves all pending human approval requests requiring marketer intervention.
    """
    items = await service.list_pending_approvals(skip=skip, limit=limit)
    return ApprovalRequestListResponse(total=len(items), items=items)


@router.post(
    "/{req_id}/approve",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Human Approve Action",
)
async def approve_request(
    req_id: uuid.UUID,
    review: ActionReviewRequest,
    approval_service: ApprovalService = Depends(get_approval_service),
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    """
    Human marketer approves a pending action (e.g. campaign publish).
    Triggers automated platform publishing upon successful approval.
    """
    approved_req = await approval_service.approve_request(req_id, review)

    # If action was PUBLISH_CAMPAIGN and campaign_id is set, execute publish bypassing policy gate
    if approved_req.campaign_id and approved_req.requested_action == "PUBLISH_CAMPAIGN":
        try:
            await campaign_service.publish_campaign(
                approved_req.campaign_id, actor_id=review.reviewer_id, bypass_safety=True
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Approved action succeeded, but campaign execution failed: {str(exc)}",
            )

    return approved_req


@router.post(
    "/{req_id}/reject",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Human Reject Action",
)
async def reject_request(
    req_id: uuid.UUID,
    review: ActionReviewRequest,
    service: ApprovalService = Depends(get_approval_service),
):
    """
    Human marketer rejects a pending action with an optional rejection reason.
    """
    return await service.reject_request(req_id, review)

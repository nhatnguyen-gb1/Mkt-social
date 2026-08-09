import logging
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.safety import ApprovalRequest
from app.models.base import utc_now
from app.repositories.safety_repository import SafetyRepository
from app.services.audit_service import AuditService
from app.schemas.safety import ApprovalRequestResponse, ActionReviewRequest

logger = logging.getLogger("aimos.services.approval")


class ApprovalService:
    """
    Domain service for Human-in-the-Loop Approval Workflow.
    Allows human marketers to review, approve, or reject pending financial/campaign actions.
    """

    def __init__(self, safety_repo: SafetyRepository, audit_service: AuditService):
        self.safety_repo = safety_repo
        self.audit_service = audit_service

    async def list_pending_approvals(self, skip: int = 0, limit: int = 100) -> List[ApprovalRequestResponse]:
        reqs = await self.safety_repo.list_pending_approval_requests(skip=skip, limit=limit)
        return [ApprovalRequestResponse.model_validate(r) for r in reqs]

    async def approve_request(
        self, req_id: uuid.UUID, review: ActionReviewRequest
    ) -> ApprovalRequestResponse:
        logger.info(f"Human marketer '{review.reviewer_id}' approving request '{req_id}'...")
        
        req = await self.safety_repo.get_approval_request_by_id(req_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ApprovalRequest with id '{req_id}' not found",
            )
        if req.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ApprovalRequest '{req_id}' is already {req.status}",
            )

        updated_req = await self.safety_repo.update_approval_request(
            req,
            {
                "status": "APPROVED",
                "reviewed_by": review.reviewer_id,
                "reviewed_at": utc_now(),
            },
        )

        # Audit Log: HUMAN_APPROVED
        await self.audit_service.log_action(
            actor_type="USER",
            actor_id=review.reviewer_id,
            action="HUMAN_APPROVED",
            entity_type="ApprovalRequest",
            entity_id=req.id,
            output_data={"action": req.requested_action, "campaign_id": str(req.campaign_id)},
            status="SUCCESS",
        )

        return ApprovalRequestResponse.model_validate(updated_req)

    async def reject_request(
        self, req_id: uuid.UUID, review: ActionReviewRequest
    ) -> ApprovalRequestResponse:
        logger.info(f"Human marketer '{review.reviewer_id}' rejecting request '{req_id}'...")

        req = await self.safety_repo.get_approval_request_by_id(req_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ApprovalRequest with id '{req_id}' not found",
            )

        updated_req = await self.safety_repo.update_approval_request(
            req,
            {
                "status": "REJECTED",
                "rejection_reason": review.rejection_reason or "Rejected by human marketer",
                "reviewed_by": review.reviewer_id,
                "reviewed_at": utc_now(),
            },
        )

        # Audit Log: HUMAN_REJECTED
        await self.audit_service.log_action(
            actor_type="USER",
            actor_id=review.reviewer_id,
            action="HUMAN_REJECTED",
            entity_type="ApprovalRequest",
            entity_id=req.id,
            output_data={"reason": updated_req.rejection_reason},
            status="FAILURE",
        )

        return ApprovalRequestResponse.model_validate(updated_req)

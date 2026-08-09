import logging
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.safety_repository import SafetyRepository
from app.services.audit_service import AuditService
from app.services.safety_service import SafetyService
from app.schemas.campaign import CampaignCreate, CampaignResponse, PublishResponse
from app.core.adapters.factory import PlatformAdapterFactory

logger = logging.getLogger("aimos.services.campaign")


class CampaignService:
    """
    Domain service for managing marketing ad campaigns and executing platform publishing with Safety Checks.
    """

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        audit_service: AuditService,
        safety_service: Optional[SafetyService] = None,
        safety_repo: Optional[SafetyRepository] = None,
    ):
        self.campaign_repo = campaign_repo
        self.audit_service = audit_service
        self.safety_service = safety_service or (SafetyService(safety_repo) if safety_repo else None)

    async def create_campaign(
        self, request: CampaignCreate, actor_id: Optional[str] = None
    ) -> CampaignResponse:
        logger.info(f"Creating campaign '{request.name}' for platform '{request.platform}'...")
        
        campaign_dict = request.model_dump()
        campaign = await self.campaign_repo.create_campaign_with_structure(campaign_dict)

        await self.audit_service.log_action(
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            action="CAMPAIGN_CREATED",
            entity_type="Campaign",
            entity_id=campaign.id,
            input_data=request.model_dump(mode="json"),
            output_data={"campaign_id": str(campaign.id), "status": campaign.status},
            status="SUCCESS",
        )

        return CampaignResponse.model_validate(campaign)

    async def publish_campaign(
        self, campaign_id: uuid.UUID, actor_id: Optional[str] = None, bypass_safety: bool = False
    ) -> PublishResponse:
        logger.info(f"Evaluating and publishing campaign '{campaign_id}'...")
        
        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with id '{campaign_id}' not found",
            )

        # 1. Safety Engine Policy Evaluation
        if self.safety_service and not bypass_safety:
            policy_result = await self.safety_service.evaluate_campaign_safety(campaign)
            
            # If Policy violations exist (e.g. daily budget cap exceeded or restricted keywords found)
            if not policy_result.is_allowed:
                violations_text = "; ".join(policy_result.policy_violations)
                logger.warning(f"Campaign '{campaign_id}' blocked by Policy Engine: {violations_text}")
                
                await self.audit_service.log_action(
                    actor_type="SYSTEM",
                    action="CAMPAIGN_BLOCKED_BY_POLICY",
                    entity_type="Campaign",
                    entity_id=campaign.id,
                    output_data={"violations": policy_result.policy_violations},
                    status="FAILURE",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campaign publish blocked by Policy Engine: {violations_text}",
                )

            # If Human Approval is required (Human-in-the-Loop Gate)
            if policy_result.requires_human_approval and campaign.status != "APPROVED":
                # Create ApprovalRequest in DB
                approval_req = await self.safety_service.safety_repo.create_approval_request(
                    {
                        "campaign_id": campaign.id,
                        "requested_action": "PUBLISH_CAMPAIGN",
                        "requested_by": actor_id or "AI_AGENT",
                        "status": "PENDING",
                    }
                )
                
                # Update Campaign status to PENDING_APPROVAL
                await self.campaign_repo.update(campaign, {"status": "PENDING_APPROVAL"})

                await self.audit_service.log_action(
                    actor_type="SYSTEM",
                    action="CAMPAIGN_APPROVAL_REQUESTED",
                    entity_type="Campaign",
                    entity_id=campaign.id,
                    output_data={"approval_request_id": str(approval_req.id)},
                    status="SUCCESS",
                )

                return PublishResponse(
                    campaign_id=campaign.id,
                    platform=campaign.platform,
                    status="PENDING_APPROVAL",
                    external_campaign_id="pending_approval",
                    is_mock=True,
                    message=f"Campaign requires Human Approval before publishing. Created ApprovalRequest '{approval_req.id}'.",
                )

        # 2. Push campaign to platform API (Meta / TikTok / Mock Sandbox)
        adapter = PlatformAdapterFactory.get_adapter(campaign.platform)
        pub_result = await adapter.create_campaign(
            {
                "name": campaign.name,
                "objective": campaign.objective,
                "daily_budget": campaign.daily_budget,
            }
        )

        # 3. Update campaign status in DB
        ext_id = pub_result.get("external_campaign_id")
        updated_campaign = await self.campaign_repo.update(
            campaign,
            {
                "status": pub_result.get("status", "ACTIVE"),
                "external_campaign_id": ext_id,
            },
        )

        # 4. Audit Logging
        await self.audit_service.log_action(
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            action="CAMPAIGN_PUBLISHED",
            entity_type="Campaign",
            entity_id=campaign.id,
            output_data={"external_campaign_id": ext_id, "is_mock": pub_result.get("is_mock", True)},
            status="SUCCESS",
        )

        return PublishResponse(
            campaign_id=updated_campaign.id,
            platform=updated_campaign.platform,
            status=updated_campaign.status,
            external_campaign_id=ext_id,
            is_mock=pub_result.get("is_mock", True),
            message=pub_result.get("message", f"Campaign successfully published to {updated_campaign.platform}."),
        )

    async def get_campaign(self, campaign_id: uuid.UUID) -> Optional[CampaignResponse]:
        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            return None
        return CampaignResponse.model_validate(campaign)

    async def list_campaigns(
        self, product_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100
    ) -> List[CampaignResponse]:
        if product_id:
            campaigns = await self.campaign_repo.get_by_product_id(product_id, skip=skip, limit=limit)
        else:
            campaigns = await self.campaign_repo.get_multi(skip=skip, limit=limit)
        return [CampaignResponse.model_validate(c) for c in campaigns]

import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_campaign_service
from app.services.campaign_service import CampaignService
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignListResponse,
    PublishResponse,
)

router = APIRouter(prefix="/campaigns", tags=["Ad Campaigns & Platforms"])


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Ad Campaign (Draft)",
)
async def create_campaign(
    request: CampaignCreate,
    service: CampaignService = Depends(get_campaign_service),
):
    """
    Creates an ad campaign in DRAFT status with ad sets and ad copies.
    """
    return await service.create_campaign(request)


@router.post(
    "/{campaign_id}/publish",
    response_model=PublishResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish Campaign to Ad Platform",
)
async def publish_campaign(
    campaign_id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
):
    """
    Publishes a campaign to Meta Ads or TikTok Ads via Platform Adapters (Meta Graph API / Sandbox).
    """
    return await service.publish_campaign(campaign_id)


@router.get(
    "",
    response_model=CampaignListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Ad Campaigns",
)
async def list_campaigns(
    product_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    service: CampaignService = Depends(get_campaign_service),
):
    """
    Retrieves all ad campaigns, optionally filtered by product_id.
    """
    items = await service.list_campaigns(product_id=product_id, skip=skip, limit=limit)
    return CampaignListResponse(total=len(items), items=items)


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Campaign Details by ID",
)
async def get_campaign(
    campaign_id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
):
    """
    Retrieves complete campaign details including associated ad sets and ad creatives.
    """
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with id '{campaign_id}' not found",
        )
    return campaign

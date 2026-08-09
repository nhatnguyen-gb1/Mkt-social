import uuid
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_analytics_service
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    CampaignMetricResponse,
    CampaignAnalyticsSummaryResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics & Performance Metrics"])


@router.post(
    "/sync/{campaign_id}",
    response_model=CampaignMetricResponse,
    status_code=status.HTTP_200_OK,
    summary="Sync Campaign Performance Metrics from Platform",
)
async def sync_campaign_metrics(
    campaign_id: uuid.UUID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Fetches raw performance metrics from Meta Graph API, TikTok Marketing API, or Mock Sandbox,
    records a timestamped CampaignMetric snapshot, and calculates CTR, CPA, and ROAS.
    """
    return await service.sync_campaign_metrics(campaign_id)


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignAnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Campaign Analytics Summary & History",
)
async def get_campaign_analytics_summary(
    campaign_id: uuid.UUID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Retrieves aggregated performance metrics (total impressions, clicks, spend, conversions, avg CTR, avg CPA, avg ROAS)
    and full metric snapshot history for a given campaign.
    """
    return await service.get_campaign_analytics_summary(campaign_id)

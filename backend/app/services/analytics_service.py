import logging
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.analytics import CampaignMetric
from app.models.base import utc_now
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.campaign_repository import CampaignRepository
from app.services.audit_service import AuditService
from app.schemas.analytics import (
    CampaignMetricResponse,
    CampaignAnalyticsSummaryResponse,
)
from app.core.adapters.factory import PlatformAdapterFactory

logger = logging.getLogger("aimos.services.analytics")


class AnalyticsService:
    """
    Domain service for fetching, syncing, and aggregating performance metrics from Ad Platforms.
    """

    def __init__(
        self,
        analytics_repo: AnalyticsRepository,
        campaign_repo: CampaignRepository,
        audit_service: AuditService,
    ):
        self.analytics_repo = analytics_repo
        self.campaign_repo = campaign_repo
        self.audit_service = audit_service

    async def sync_campaign_metrics(
        self, campaign_id: uuid.UUID, actor_id: Optional[str] = None
    ) -> CampaignMetricResponse:
        logger.info(f"Syncing platform metrics for campaign '{campaign_id}'...")

        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with id '{campaign_id}' not found",
            )

        # 1. Resolve Platform Adapter (Meta / TikTok / Mock Sandbox)
        adapter = PlatformAdapterFactory.get_adapter(campaign.platform)
        ext_id = campaign.external_campaign_id or f"mock_{campaign.platform.lower()}_cmp_default"

        # 2. Fetch raw metric payload from platform API
        raw_metrics = await adapter.sync_campaign_metrics(ext_id)

        impressions = int(raw_metrics.get("impressions", 10000))
        clicks = int(raw_metrics.get("clicks", 350))
        spend_usd = float(raw_metrics.get("spend_usd", 50.0))
        conversions = int(raw_metrics.get("conversions", 15))

        # Calculate derived KPIs
        ctr = round((clicks / impressions * 100.0) if impressions > 0 else 0.0, 2)
        cpa_usd = round((spend_usd / conversions) if conversions > 0 else 0.0, 2)
        roas = round(((conversions * 25.0) / spend_usd) if spend_usd > 0 else 0.0, 2)

        # 3. Create CampaignMetric record in DB
        metric = await self.analytics_repo.create(
            {
                "campaign_id": campaign.id,
                "platform": campaign.platform,
                "recorded_at": utc_now(),
                "impressions": impressions,
                "clicks": clicks,
                "spend_usd": spend_usd,
                "conversions": conversions,
                "ctr": ctr,
                "cpa_usd": cpa_usd,
                "roas": roas,
            }
        )

        # 4. Audit Log
        await self.audit_service.log_action(
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            action="METRICS_SYNCED",
            entity_type="CampaignMetric",
            entity_id=metric.id,
            output_data={
                "campaign_id": str(campaign.id),
                "impressions": impressions,
                "clicks": clicks,
                "spend_usd": spend_usd,
                "conversions": conversions,
            },
            status="SUCCESS",
        )

        return CampaignMetricResponse.model_validate(metric)

    async def get_campaign_analytics_summary(
        self, campaign_id: uuid.UUID
    ) -> CampaignAnalyticsSummaryResponse:
        campaign = await self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with id '{campaign_id}' not found",
            )

        metrics = await self.analytics_repo.get_metrics_by_campaign_id(campaign_id)
        if not metrics:
            # Sync at least one metric snapshot if none exist
            first_metric = await self.sync_campaign_metrics(campaign_id)
            metrics = [await self.analytics_repo.get_by_id(first_metric.id)]

        total_imp = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_spend = sum(m.spend_usd for m in metrics)
        total_conv = sum(m.conversions for m in metrics)

        avg_ctr = round(sum(m.ctr for m in metrics) / len(metrics), 2)
        avg_cpa = round(sum(m.cpa_usd for m in metrics) / len(metrics), 2)
        avg_roas = round(sum(m.roas for m in metrics) / len(metrics), 2)

        return CampaignAnalyticsSummaryResponse(
            campaign_id=campaign_id,
            platform=campaign.platform,
            total_impressions=total_imp,
            total_clicks=total_clicks,
            total_spend_usd=round(total_spend, 2),
            total_conversions=total_conv,
            average_ctr=avg_ctr,
            average_cpa_usd=avg_cpa,
            average_roas=avg_roas,
            metrics_history=[CampaignMetricResponse.model_validate(m) for m in metrics],
        )

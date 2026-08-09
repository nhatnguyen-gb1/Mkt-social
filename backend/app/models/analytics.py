import uuid
from typing import Optional, Any
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class CampaignMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "campaign_metrics"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_set_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    ad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, default="META", index=True
    )
    recorded_at: Mapped[Any] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spend_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ctr: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # Click-Through Rate %
    cpa_usd: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # Cost Per Acquisition $
    roas: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # Return On Ad Spend x

    def __repr__(self) -> str:
        return f"<CampaignMetric {self.platform} (spend=${self.spend_usd}, conversions={self.conversions})>"

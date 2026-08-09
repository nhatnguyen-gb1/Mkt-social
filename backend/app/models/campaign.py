import uuid
from typing import Optional, List, Any
from sqlalchemy import String, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Campaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "campaigns"

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, default="META", index=True
    )  # META, TIKTOK
    objective: Mapped[str] = mapped_column(
        String(100), nullable=False, default="CONVERSIONS"
    )
    daily_budget: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="DRAFT", index=True
    )  # DRAFT, PENDING_APPROVAL, ACTIVE, PAUSED
    external_campaign_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    campaign_metadata: Mapped[Optional[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    ad_sets: Mapped[List["AdSet"]] = relationship(
        "AdSet", back_populates="campaign", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Campaign {self.name} (platform={self.platform}, status={self.status})>"


class AdSet(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ad_sets"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    targeting: Mapped[Optional[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    daily_budget: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    external_adset_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="ad_sets")
    ads: Mapped[List["Ad"]] = relationship(
        "Ad", back_populates="ad_set", cascade="all, delete-orphan", lazy="selectin"
    )


class Ad(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ads"

    ad_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    primary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    call_to_action: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default="SHOP_NOW"
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    external_ad_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    ad_set: Mapped["AdSet"] = relationship("AdSet", back_populates="ads")

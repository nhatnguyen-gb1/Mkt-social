import uuid
from typing import Optional, Any
from sqlalchemy import String, Boolean, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class PolicyRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "policy_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # MAX_DAILY_BUDGET, RESTRICTED_KEYWORDS, REQUIRE_APPROVAL_FOR_PUBLISH
    parameters: Mapped[Optional[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    def __repr__(self) -> str:
        return f"<PolicyRule {self.name} (type={self.rule_type}, active={self.is_active})>"


class ApprovalRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "approval_requests"

    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    requested_action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # PUBLISH_CAMPAIGN, INCREASE_BUDGET, APPROVE_CREATIVE
    requested_by: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING", index=True
    )  # PENDING, APPROVED, REJECTED
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    reviewed_at: Mapped[Optional[Any]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<ApprovalRequest {self.requested_action} (status={self.status}, id={self.id})>"

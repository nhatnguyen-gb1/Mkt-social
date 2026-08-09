import uuid
from typing import Optional, Any
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Asset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assets"

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    agent_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="IMAGE", index=True
    )  # IMAGE, VIDEO_SCRIPT, CREATIVE_TEXT
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    asset_metadata: Mapped[Optional[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="DRAFT", index=True
    )  # DRAFT, APPROVED, REJECTED

    def __repr__(self) -> str:
        return f"<Asset {self.title} (type={self.asset_type}, id={self.id})>"

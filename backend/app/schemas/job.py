from datetime import datetime
from typing import Optional, Any, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    job_type: str = Field(..., min_length=1, max_length=100, description="Type of background execution task")
    status: str = Field("PENDING", description="Job execution status: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED")
    entity_type: Optional[str] = Field(None, max_length=100)
    entity_id: Optional[UUID] = None
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None

    # Phase 2 additions
    retry_count: int = Field(0, description="Current retry attempts")
    max_retries: int = Field(3, description="Maximum retry limit")
    created_by_telegram_id: Optional[str] = Field(None, max_length=100)


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    size: int

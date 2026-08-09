import uuid
from fastapi import APIRouter, Depends, Query, status
from app.schemas.job import JobResponse, JobListResponse
from app.services.job_service import JobService
from app.api.dependencies import get_job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "",
    response_model=JobListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Jobs",
)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: JobService = Depends(get_job_service),
):
    return await service.list_jobs(page=page, size=size)


@router.get(
    "/{id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Job by ID",
)
async def get_job(
    id: uuid.UUID,
    service: JobService = Depends(get_job_service),
):
    return await service.get_job(id)

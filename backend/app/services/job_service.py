import uuid
from typing import Optional
from fastapi import HTTPException, status
from app.repositories.job_repository import JobRepository
from app.services.audit_service import AuditService
from app.schemas.job import JobCreate, JobResponse, JobListResponse


class JobService:
    def __init__(self, job_repo: JobRepository, audit_service: AuditService):
        self.job_repo = job_repo
        self.audit_service = audit_service

    async def create_job(
        self, job_in: JobCreate, actor_id: Optional[str] = None
    ) -> JobResponse:
        data = job_in.model_dump()
        if data.get("entity_id"):
            data["entity_id"] = data["entity_id"]

        job = await self.job_repo.create(data)

        # Audit Log hook
        await self.audit_service.log_action(
            action="JOB_CREATED",
            entity_type="Job",
            entity_id=job.id,
            actor_type="USER" if actor_id else "SYSTEM",
            actor_id=actor_id,
            input_data={"job_type": job.job_type, "entity_type": job.entity_type},
            output_data={"id": str(job.id), "status": job.status},
        )

        return JobResponse.model_validate(job)

    async def get_job(self, job_id: uuid.UUID) -> JobResponse:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with id '{job_id}' not found",
            )
        return JobResponse.model_validate(job)

    async def list_jobs(
        self, page: int = 1, size: int = 50
    ) -> JobListResponse:
        skip = (page - 1) * size
        jobs = await self.job_repo.get_multi_ordered(skip=skip, limit=size)
        total = await self.job_repo.count()
        return JobListResponse(
            items=[JobResponse.model_validate(j) for j in jobs],
            total=total,
            page=page,
            size=size,
        )

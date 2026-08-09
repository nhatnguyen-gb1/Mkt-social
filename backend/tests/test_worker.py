import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.job_repository import JobRepository
from app.services.worker_service import WorkerService


@pytest.mark.asyncio
async def test_worker_successful_job_execution(db_session: AsyncSession):
    repo = JobRepository(db_session)
    job = await repo.create(
        {
            "job_type": "MARKET_RESEARCH",
            "status": "PENDING",
            "input_data": {"category": "Tech"},
        }
    )
    await db_session.commit()

    worker = WorkerService()
    processed = await worker.process_next_pending_job(session=db_session)
    assert processed is True

    # Refresh job state
    updated_job = await repo.get_by_id(job.id)
    assert updated_job.status == "COMPLETED"
    assert updated_job.started_at is not None
    assert updated_job.completed_at is not None
    assert updated_job.output_data is not None
    assert "result" in updated_job.output_data


@pytest.mark.asyncio
async def test_worker_retry_strategy_and_failure(db_session: AsyncSession):
    repo = JobRepository(db_session)
    # Create job configured to simulate failure with max_retries = 2
    job = await repo.create(
        {
            "job_type": "FAILING_TASK",
            "status": "PENDING",
            "max_retries": 2,
            "input_data": {"simulate_fail": True},
        }
    )
    await db_session.commit()

    worker = WorkerService()

    # Attempt 1: Fails, retry_count becomes 1, re-queued to PENDING
    await worker.process_next_pending_job(session=db_session)
    j1 = await repo.get_by_id(job.id)
    assert j1.retry_count == 1
    assert j1.status == "PENDING"

    # Attempt 2: Fails again, retry_count reaches max_retries 2, state becomes FAILED
    await worker.process_next_pending_job(session=db_session)
    j2 = await repo.get_by_id(job.id)
    assert j2.retry_count == 2
    assert j2.status == "FAILED"
    assert j2.error_message is not None
    assert "Simulated job failure" in j2.error_message

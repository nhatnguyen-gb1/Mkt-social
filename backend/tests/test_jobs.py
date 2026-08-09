import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.job_repository import JobRepository


@pytest.mark.asyncio
async def test_list_and_get_jobs(client: AsyncClient, db_session: AsyncSession):
    # Insert a dummy job into DB directly via repository
    repo = JobRepository(db_session)
    job = await repo.create(
        {
            "job_type": "MARKET_RESEARCH",
            "status": "COMPLETED",
            "input_data": {"query": "SaaS competitors"},
            "output_data": {"findings": ["Competitor A", "Competitor B"]},
        }
    )
    await db_session.commit()

    # Test GET /api/v1/jobs
    list_res = await client.get("/api/v1/jobs")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert list_data["items"][0]["job_type"] == "MARKET_RESEARCH"

    # Test GET /api/v1/jobs/{id}
    job_id = str(job.id)
    get_res = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["id"] == job_id
    assert get_data["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_get_nonexistent_job(client: AsyncClient):
    random_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/jobs/{random_id}")
    assert response.status_code == 404

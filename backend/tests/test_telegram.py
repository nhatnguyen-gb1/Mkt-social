import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService
from app.services.telegram_auth_service import TelegramAuthService


@pytest.mark.asyncio
async def test_telegram_auth_allowed(db_session: AsyncSession):
    audit_repo = AuditRepository(db_session)
    audit_service = AuditService(audit_repo)
    auth_service = TelegramAuthService(audit_service)

    # Configure allowed user ID
    settings.TELEGRAM_ALLOWED_USERS = "12345,67890"

    assert await auth_service.is_authorized("12345") is True
    assert await auth_service.is_authorized("67890") is True


@pytest.mark.asyncio
async def test_telegram_auth_unauthorized_blocks_and_audits(
    db_session: AsyncSession, client: AsyncClient
):
    settings.TELEGRAM_ALLOWED_USERS = "99999"

    # Send webhook from unauthorized user 11111
    webhook_payload = {
        "update_id": 1,
        "message": {
            "message_id": 100,
            "from": {"id": 11111, "first_name": "Attacker"},
            "chat": {"id": 11111},
            "text": "/create_product Unauthorized Product",
        },
    }

    response = await client.post("/api/v1/telegram/webhook", json=webhook_payload)
    assert response.status_code == 200
    data = response.json()
    assert "Bạn không có quyền" in data["response"]

    # Verify security audit log recorded
    audit_res = await client.get("/api/v1/audit-logs")
    assert audit_res.status_code == 200
    actions = [log["action"] for log in audit_res.json()["items"]]
    assert "UNAUTHORIZED_TELEGRAM_ACCESS" in actions


@pytest.mark.asyncio
async def test_telegram_create_product_command(client: AsyncClient):
    settings.TELEGRAM_ALLOWED_USERS = "12345"

    webhook_payload = {
        "update_id": 2,
        "message": {
            "message_id": 101,
            "from": {"id": 12345, "first_name": "Admin"},
            "chat": {"id": 12345},
            "text": "/create_product Telegram Coffee Brand",
        },
    }

    response = await client.post("/api/v1/telegram/webhook", json=webhook_payload)
    assert response.status_code == 200
    assert "Đã tạo sản phẩm thành công" in response.json()["response"]

    # Verify product listing command
    list_payload = {
        "update_id": 3,
        "message": {
            "message_id": 102,
            "from": {"id": 12345},
            "chat": {"id": 12345},
            "text": "/list_products",
        },
    }
    list_res = await client.post("/api/v1/telegram/webhook", json=list_payload)
    assert "Telegram Coffee Brand" in list_res.json()["response"]


@pytest.mark.asyncio
async def test_telegram_run_job_command(client: AsyncClient):
    settings.TELEGRAM_ALLOWED_USERS = "12345"

    webhook_payload = {
        "update_id": 4,
        "message": {
            "message_id": 103,
            "from": {"id": 12345},
            "chat": {"id": 12345},
            "text": "/run_job CREATIVE_STRATEGY",
        },
    }

    response = await client.post("/api/v1/telegram/webhook", json=webhook_payload)
    assert response.status_code == 200
    assert "Đã tạo nhiệm vụ ngầm" in response.json()["response"]

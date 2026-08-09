import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.telegram import TelegramClient
from app.core.telegram_formatter import TelegramFormatter
from app.services.telegram_auth_service import TelegramAuthService
from app.services.telegram_adapter import TelegramAdapter
from app.services.product_service import ProductService
from app.services.job_service import JobService
from app.services.agent_service import AgentService
from app.services.audit_service import AuditService
from app.repositories.audit_repository import AuditRepository
from app.schemas.agent import AgentRunResponse
from app.models.base import utc_now


@pytest.fixture
def mock_telegram_client():
    client = MagicMock(spec=TelegramClient)
    client.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 100}})
    return client


@pytest.fixture
def mock_audit_service(db_session):
    repo = AuditRepository(db_session)
    return AuditService(repo)


@pytest.fixture
def mock_product_service():
    service = AsyncMock(spec=ProductService)
    service.list_products.return_value = []
    return service


@pytest.fixture
def mock_job_service():
    return AsyncMock(spec=JobService)


@pytest.fixture
def mock_agent_service():
    service = AsyncMock(spec=AgentService)
    service.run_market_research.return_value = AgentRunResponse(
        run_id=uuid.uuid4(),
        agent_name="MarketResearchAgent",
        status="COMPLETED",
        provider_used="mock",
        input_data={"product_name": "Bánh Trung Thu", "target_market": "Vietnam"},
        result={
            "product_name": "Bánh Trung Thu",
            "target_market": "Vietnam",
            "summary": "Thị trường bánh trung thu Việt Nam phát triển mạnh mùa lễ hội.",
            "opportunities": ["Hộp quà sang trọng"],
            "risks": ["Cạnh tranh mùa vụ ngắn"],
            "recommended_marketing_angles": ["Quà tặng doanh nghiệp xa xỉ"],
        },
        execution_time_ms=120,
        created_at=utc_now(),
    )
    return service


@pytest.mark.asyncio
async def test_telegram_formatter_outputs():
    welcome = TelegramFormatter.format_welcome()
    assert "AIMOS" in welcome

    help_msg = TelegramFormatter.format_help()
    assert "/research" in help_msg

    res_msg = TelegramFormatter.format_research_result(
        result={
            "product_name": "Bánh Trung Thu",
            "target_market": "Vietnam",
            "summary": "Tóm tắt phân tích...",
            "opportunities": ["Cơ hội 1"],
        },
        provider_name="mock",
        execution_time_ms=150,
        request_id="req_test_123",
    )
    assert "Bánh Trung Thu" in res_msg
    assert "req_test_123" in res_msg
    assert "MOCK" in res_msg


@pytest.mark.asyncio
async def test_telegram_adapter_commands(
    mock_telegram_client, mock_audit_service, mock_product_service, mock_job_service, mock_agent_service
):
    auth_service = TelegramAuthService(mock_audit_service)

    adapter = TelegramAdapter(
        telegram_client=mock_telegram_client,
        auth_service=auth_service,
        product_service=mock_product_service,
        job_service=mock_job_service,
        audit_service=mock_audit_service,
        agent_service=mock_agent_service,
    )

    user_id = 12345

    # 1. Test /start
    update_start = {"message": {"chat": {"id": 999}, "from": {"id": user_id}, "text": "/start"}}
    res_start = await adapter.process_update(update_start)
    assert res_start["status"] == "success"
    mock_telegram_client.send_message.assert_called()

    # 2. Test /agents
    update_agents = {"message": {"chat": {"id": 999}, "from": {"id": user_id}, "text": "/agents"}}
    res_agents = await adapter.process_update(update_agents)
    assert res_agents["status"] == "success"


@pytest.mark.asyncio
async def test_telegram_adapter_interactive_research_flow(
    mock_telegram_client, mock_audit_service, mock_product_service, mock_job_service, mock_agent_service
):
    auth_service = TelegramAuthService(mock_audit_service)

    adapter = TelegramAdapter(
        telegram_client=mock_telegram_client,
        auth_service=auth_service,
        product_service=mock_product_service,
        job_service=mock_job_service,
        audit_service=mock_audit_service,
        agent_service=mock_agent_service,
    )

    user_id = 12345
    chat_id = 888

    # Step 1: Send /research
    res1 = await adapter.process_update(
        {"message": {"chat": {"id": chat_id}, "from": {"id": user_id}, "text": "/research"}}
    )
    assert res1["status"] == "success"
    assert res1["state"] == "AWAITING_PRODUCT"

    # Step 2: Provide Product Name "Xe máy điện"
    res2 = await adapter.process_update(
        {"message": {"chat": {"id": chat_id}, "from": {"id": user_id}, "text": "Xe máy điện"}}
    )
    assert res2["status"] == "in_progress"
    assert res2["state"] == "AWAITING_MARKET"

    # Step 3: Provide Market "Vietnam" -> Triggers Research Agent
    res3 = await adapter.process_update(
        {"message": {"chat": {"id": chat_id}, "from": {"id": user_id}, "text": "Vietnam"}}
    )
    assert res3["status"] == "success"
    assert res3["action"] == "research_completed"

    mock_agent_service.run_market_research.assert_called()


@pytest.mark.asyncio
async def test_telegram_adapter_oneshot_natural_language_prompt(
    mock_telegram_client, mock_audit_service, mock_product_service, mock_job_service, mock_agent_service
):
    auth_service = TelegramAuthService(mock_audit_service)

    adapter = TelegramAdapter(
        telegram_client=mock_telegram_client,
        auth_service=auth_service,
        product_service=mock_product_service,
        job_service=mock_job_service,
        audit_service=mock_audit_service,
        agent_service=mock_agent_service,
    )

    user_id = 12345
    chat_id = 888

    # Send one-shot natural language prompt
    prompt = "Nghiên cứu sản phẩm bánh trung thu tại thị trường Việt Nam. Phân tích cơ hội, khách hàng mục tiêu và đối thủ."
    res = await adapter.process_update(
        {"message": {"chat": {"id": chat_id}, "from": {"id": user_id}, "text": prompt}}
    )
    assert res["status"] == "success"
    assert res["action"] == "research_completed"
    mock_agent_service.run_market_research.assert_called()


@pytest.mark.asyncio
async def test_telegram_adapter_unauthorized_user(
    mock_telegram_client, mock_audit_service, mock_product_service, mock_job_service, mock_agent_service
):
    auth_service = TelegramAuthService(mock_audit_service)

    adapter = TelegramAdapter(
        telegram_client=mock_telegram_client,
        auth_service=auth_service,
        product_service=mock_product_service,
        job_service=mock_job_service,
        audit_service=mock_audit_service,
        agent_service=mock_agent_service,
    )

    unauth_user_id = 99999999
    update_unauth = {
        "message": {"chat": {"id": 777}, "from": {"id": unauth_user_id}, "text": "/research"}
    }
    res = await adapter.process_update(update_unauth)
    assert res["status"] == "unauthorized"
    assert res["user_id"] == unauth_user_id


@pytest.mark.asyncio
async def test_telegram_adapter_backend_exception_handling(
    mock_telegram_client, mock_audit_service, mock_product_service, mock_job_service
):
    auth_service = TelegramAuthService(mock_audit_service)
    failing_agent_service = AsyncMock(spec=AgentService)
    failing_agent_service.run_market_research.side_effect = RuntimeError("Internal Database Failure")

    adapter = TelegramAdapter(
        telegram_client=mock_telegram_client,
        auth_service=auth_service,
        product_service=mock_product_service,
        job_service=mock_job_service,
        audit_service=mock_audit_service,
        agent_service=failing_agent_service,
    )

    user_id = 12345
    chat_id = 888

    res = await adapter.process_update(
        {"message": {"chat": {"id": chat_id}, "from": {"id": user_id}, "text": "Nghiên cứu sản phẩm bánh trung thu tại Việt Nam"}}
    )
    assert res["status"] == "error"
    assert "request_id" in res
    mock_telegram_client.send_message.assert_called()

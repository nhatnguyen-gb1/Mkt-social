from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.telegram import TelegramClient
from app.repositories.product_repository import ProductRepository
from app.repositories.job_repository import JobRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.agent_repository import AgentRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.safety_repository import SafetyRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.audit_service import AuditService
from app.services.product_service import ProductService
from app.services.job_service import JobService
from app.services.telegram_auth_service import TelegramAuthService
from app.services.telegram_adapter import TelegramAdapter
from app.services.worker_service import WorkerService
from app.services.agent_service import AgentService
from app.services.asset_service import AssetService
from app.services.campaign_service import CampaignService
from app.services.safety_service import SafetyService
from app.services.approval_service import ApprovalService
from app.services.analytics_service import AnalyticsService
from app.core.workflow.engine import WorkflowEngine


def get_audit_repository(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    return AuditRepository(db)


def get_product_repository(db: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_job_repository(db: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(db)


def get_agent_repository(db: AsyncSession = Depends(get_db)) -> AgentRepository:
    return AgentRepository(db)


def get_asset_repository(db: AsyncSession = Depends(get_db)) -> AssetRepository:
    return AssetRepository(db)


def get_campaign_repository(db: AsyncSession = Depends(get_db)) -> CampaignRepository:
    return CampaignRepository(db)


def get_safety_repository(db: AsyncSession = Depends(get_db)) -> SafetyRepository:
    return SafetyRepository(db)


def get_analytics_repository(db: AsyncSession = Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(db)


def get_audit_service(
    audit_repo: AuditRepository = Depends(get_audit_repository),
) -> AuditService:
    return AuditService(audit_repo)


def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> ProductService:
    return ProductService(product_repo, audit_service)


def get_job_service(
    job_repo: JobRepository = Depends(get_job_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> JobService:
    return JobService(job_repo, audit_service)


def get_agent_service(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> AgentService:
    return AgentService(agent_repo, audit_service)


def get_asset_service(
    asset_repo: AssetRepository = Depends(get_asset_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> AssetService:
    return AssetService(asset_repo, audit_service)


def get_safety_service(
    safety_repo: SafetyRepository = Depends(get_safety_repository),
) -> SafetyService:
    return SafetyService(safety_repo)


def get_approval_service(
    safety_repo: SafetyRepository = Depends(get_safety_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> ApprovalService:
    return ApprovalService(safety_repo, audit_service)


def get_campaign_service(
    campaign_repo: CampaignRepository = Depends(get_campaign_repository),
    audit_service: AuditService = Depends(get_audit_service),
    safety_repo: SafetyRepository = Depends(get_safety_repository),
) -> CampaignService:
    return CampaignService(
        campaign_repo=campaign_repo,
        audit_service=audit_service,
        safety_repo=safety_repo,
    )


def get_analytics_service(
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository),
    campaign_repo: CampaignRepository = Depends(get_campaign_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> AnalyticsService:
    return AnalyticsService(
        analytics_repo=analytics_repo,
        campaign_repo=campaign_repo,
        audit_service=audit_service,
    )


def get_workflow_engine(
    agent_service: AgentService = Depends(get_agent_service),
    campaign_service: CampaignService = Depends(get_campaign_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> WorkflowEngine:
    return WorkflowEngine(
        agent_service=agent_service,
        campaign_service=campaign_service,
        analytics_service=analytics_service,
    )


def get_telegram_client() -> TelegramClient:
    return TelegramClient()


def get_telegram_auth_service(
    audit_service: AuditService = Depends(get_audit_service),
) -> TelegramAuthService:
    return TelegramAuthService(audit_service)


def get_telegram_adapter(
    telegram_client: TelegramClient = Depends(get_telegram_client),
    auth_service: TelegramAuthService = Depends(get_telegram_auth_service),
    product_service: ProductService = Depends(get_product_service),
    job_service: JobService = Depends(get_job_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> TelegramAdapter:
    return TelegramAdapter(
        telegram_client=telegram_client,
        auth_service=auth_service,
        product_service=product_service,
        job_service=job_service,
        audit_service=audit_service,
    )


def get_worker_service(
    telegram_client: TelegramClient = Depends(get_telegram_client),
) -> WorkerService:
    return WorkerService(telegram_client)

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.routes import (
    health,
    products,
    jobs,
    audit_logs,
    telegram,
    agents,
    assets,
    campaigns,
    safety,
    approvals,
    analytics,
    workflows,
    providers,
    ecommerce,
    skills,
    marketing_lead,
    market_research,
    product_strategy,
    lead_qualification,
    calls,
)
from app.services.worker_service import WorkerService
from app.services.telegram_polling_service import TelegramPollingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} ({settings.APP_ENV})")

    stop_event = asyncio.Event()

    # 1. Start Background Worker loop
    worker_service = WorkerService()
    worker_task = asyncio.create_task(
        worker_service.run_worker_loop(
            poll_interval=settings.JOB_WORKER_POLL_INTERVAL, stop_event=stop_event
        )
    )

    # 2. Start Telegram Bot Long Polling loop if configured
    polling_task = None
    if settings.is_telegram_enabled():
        logger.info("[STARTUP] Telegram Bot Token detected. Starting Telegram Long Polling Service...")
        polling_service = TelegramPollingService()
        polling_task = asyncio.create_task(
            polling_service.start_polling(stop_event=stop_event)
        )
    else:
        logger.warning(
            "[STARTUP] TELEGRAM_BOT_TOKEN is not set or empty in backend/.env! "
            "Telegram Polling is DISABLED. (Set TELEGRAM_BOT_TOKEN in .env to activate)."
        )

    yield

    logger.info("Shutting down background tasks...")
    stop_event.set()
    worker_task.cancel()
    if polling_task:
        polling_task.cancel()
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-oriented AI Marketing Operating System API - Lead Qualification Agent V1 Integrated",
    version="0.9.6",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(audit_logs.router, prefix=settings.API_V1_STR)
app.include_router(telegram.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(assets.router, prefix=settings.API_V1_STR)
app.include_router(campaigns.router, prefix=settings.API_V1_STR)
app.include_router(safety.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(workflows.router, prefix=settings.API_V1_STR)
app.include_router(providers.router, prefix=settings.API_V1_STR)
app.include_router(providers.system_router, prefix=settings.API_V1_STR)
app.include_router(ecommerce.router, prefix=settings.API_V1_STR)
app.include_router(skills.router, prefix=settings.API_V1_STR)
app.include_router(marketing_lead.router, prefix=settings.API_V1_STR)
app.include_router(market_research.router)
app.include_router(product_strategy.router)
app.include_router(lead_qualification.router)
app.include_router(calls.router, prefix=settings.API_V1_STR)


from fastapi.responses import FileResponse
import os


@app.get("/call-test")
async def call_test_ui():
    html_path = os.path.join(os.path.dirname(__file__), "static", "call_test.html")
    return FileResponse(html_path)


@app.get("/")
async def root():
    return {
        "system": settings.APP_NAME,
        "version": "0.9.6",
        "docs": "/docs",
        "health": "/health",
        "web_voice_call_ui": "/call-test",
        "telegram_bot_enabled": settings.is_telegram_enabled(),
    }

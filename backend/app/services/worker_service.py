import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import httpx
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.job import Job
from app.models.base import utc_now
from app.repositories.job_repository import JobRepository
from app.services.audit_service import AuditService
from app.repositories.audit_repository import AuditRepository
from app.core.telegram import TelegramClient

logger = logging.getLogger("aimos.worker")


class WorkerService:
    def __init__(self, telegram_client: Optional[TelegramClient] = None):
        self.telegram_client = telegram_client or TelegramClient()

    async def process_next_pending_job(self, session: Optional[AsyncSession] = None) -> bool:
        """Processes the next PENDING job. Accepts an optional explicit AsyncSession for testing/isolation."""
        if session is not None:
            return await self._process_job_with_session(session)
        else:
            async with AsyncSessionLocal() as db_session:
                return await self._process_job_with_session(db_session)

    async def _process_job_with_session(self, session: AsyncSession) -> bool:
        try:
            # 1. Fetch next PENDING job
            result = await session.execute(
                select(Job)
                .where(Job.status == "PENDING")
                .order_by(Job.created_at.asc())
                .limit(1)
            )
            job = result.scalars().first()
            if not job:
                return False

            # 2. Transition state: PENDING -> RUNNING
            job.status = "RUNNING"
            job.started_at = utc_now()
            await session.commit()
            await session.refresh(job)

            logger.info(f"Worker picked up Job ID {job.id} (type={job.job_type})")

            # 3. Execute Job logic
            audit_repo = AuditRepository(session)
            audit_service = AuditService(audit_repo)
            
            output_data, error = await self._execute_job_logic(job)

            if error is None:
                # Success path: RUNNING -> COMPLETED
                job.status = "COMPLETED"
                job.output_data = output_data
                job.completed_at = utc_now()
                await session.commit()

                await audit_service.log_action(
                    action="JOB_COMPLETED",
                    entity_type="Job",
                    entity_id=job.id,
                    output_data=output_data,
                )
                logger.info(f"Job ID {job.id} completed successfully.")
                await self._notify_completion(job, success=True)
            else:
                # Error path: Retry or FAILED
                job.retry_count += 1
                if job.retry_count < job.max_retries:
                    job.status = "PENDING"  # Re-queue for retry
                    logger.warning(
                        f"Job ID {job.id} failed attempt {job.retry_count}/{job.max_retries}. Re-queued."
                    )
                else:
                    job.status = "FAILED"
                    job.error_message = error
                    job.completed_at = utc_now()
                    logger.error(f"Job ID {job.id} failed permanently after {job.retry_count} retries: {error}")

                await session.commit()

                await audit_service.log_action(
                    action="JOB_FAILED" if job.status == "FAILED" else "JOB_RETRY",
                    entity_type="Job",
                    entity_id=job.id,
                    status="FAILURE",
                    output_data={"error": error, "retry_count": job.retry_count},
                )
                
                if job.status == "FAILED":
                    await self._notify_completion(job, success=False, error=error)

            return True

        except Exception as e:
            logger.error(f"Unexpected worker exception: {str(e)}")
            await session.rollback()
            return False

    async def _execute_job_logic(self, job: Job) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Simulates domain execution for Phase 2 tasks (Market research, Strategy, etc.)"""
        try:
            # Check if test failure simulation requested in input_data
            if job.input_data and isinstance(job.input_data, dict) and job.input_data.get("simulate_fail"):
                raise RuntimeError("Simulated job failure for retry strategy testing.")

            # Simulated execution payload
            output = {
                "result": f"Job {job.job_type} executed successfully.",
                "timestamp": utc_now().isoformat(),
                "summary": "Phase 2 Orchestration task processed by background worker.",
            }
            return output, None
        except Exception as ex:
            return None, str(ex)

    async def _notify_completion(self, job: Job, success: bool, error: Optional[str] = None):
        """Sends Telegram notification to creator if telegram details present in job"""
        chat_id = None
        if job.input_data and isinstance(job.input_data, dict):
            chat_id = job.input_data.get("chat_id")
        if not chat_id and job.created_by_telegram_id:
            chat_id = job.created_by_telegram_id

        if chat_id:
            if success:
                msg = (
                    f"🎉 *Nhiệm vụ #{str(job.id)[:8]} đã hoàn thành!*\n\n"
                    f"• **Loại**: `{job.job_type}`\n"
                    f"• **Trạng thái**: `COMPLETED`\n"
                    f"• **Thời gian**: {job.completed_at}\n"
                )
            else:
                msg = (
                    f"❌ *Nhiệm vụ #{str(job.id)[:8]} thất bại!*\n\n"
                    f"• **Loại**: `{job.job_type}`\n"
                    f"• **Trạng thái**: `FAILED`\n"
                    f"• **Lỗi**: `{error}`\n"
                )
            await self.telegram_client.send_message(str(chat_id), msg)

    async def run_worker_loop(self, poll_interval: float = 2.0, stop_event: Optional[asyncio.Event] = None):
        """Main worker loop running in background"""
        logger.info("Starting AIMOS Async Background Worker loop...")
        while stop_event is None or not stop_event.is_set():
            processed = await self.process_next_pending_job()
            if not processed:
                await asyncio.sleep(poll_interval)

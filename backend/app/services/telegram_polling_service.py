import asyncio
import logging
import httpx
from typing import Optional
from app.core.config import settings
from app.api.dependencies import (
    get_telegram_client,
    get_audit_service,
    get_product_service,
    get_job_service,
    get_agent_service,
    get_telegram_auth_service,
    get_audit_repository,
    get_product_repository,
    get_job_repository,
    get_agent_repository,
)
from app.services.telegram_adapter import TelegramAdapter
from app.core.database import AsyncSessionLocal

logger = logging.getLogger("aimos.telegram.polling")


class TelegramPollingService:
    """
    Background Long Polling Service for Telegram Bot.
    Enables local development testing without HTTPS or ngrok proxies.
    """

    def __init__(self):
        self.is_running = False
        self.last_update_id = 0

    async def start_polling(self, stop_event: asyncio.Event):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not settings.is_telegram_enabled():
            logger.warning("[TELEGRAM POLLING] Telegram Bot Token is not configured. Polling disabled.")
            return

        token_masked = f"...{bot_token[-6:]}" if len(bot_token) > 6 else "***"
        logger.info(f"[TELEGRAM POLLING] Starting Long Polling loop for Bot Token ({token_masked})...")
        self.is_running = True

        async with httpx.AsyncClient(timeout=35.0) as http_client:
            # 1. Clear any existing webhook to ensure getUpdates is not blocked with HTTP 409
            try:
                del_res = await http_client.get(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
                if del_res.status_code == 200 and del_res.json().get("ok"):
                    logger.info("[TELEGRAM POLLING] Successfully cleared Webhook to enable Long Polling.")
            except Exception as e:
                logger.warning(f"[TELEGRAM POLLING] Failed to clear webhook: {str(e)}")

            # 2. Polling loop
            while not stop_event.is_set():
                try:
                    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                    params = {"offset": self.last_update_id + 1, "timeout": 20}

                    response = await http_client.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("ok"):
                            updates = data.get("result", [])
                            for update in updates:
                                self.last_update_id = max(self.last_update_id, update.get("update_id", 0))
                                await self._dispatch_update(update)

                    elif response.status_code == 409:
                        logger.warning("[TELEGRAM POLLING 409] Conflict: Webhook is active. Clearing webhook again...")
                        await http_client.get(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
                        await asyncio.sleep(2)

                    elif response.status_code in (401, 404):
                        logger.error(f"[TELEGRAM POLLING ERROR] Invalid Bot Token ({response.status_code}). Stopping polling.")
                        break

                    else:
                        logger.warning(f"[TELEGRAM POLLING WARN] HTTP {response.status_code}: {response.text}")

                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    logger.error(f"[TELEGRAM POLLING EXCEPTION] {exc}")
                    await asyncio.sleep(5)

        self.is_running = False
        logger.info("[TELEGRAM POLLING] Telegram Polling loop stopped.")

    async def _dispatch_update(self, update: dict):
        message = update.get("message") or update.get("edited_message") or {}
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        text = message.get("text", "")

        logger.info(
            f"[TELEGRAM UPDATE RECEIVED] update_id={update.get('update_id')}, "
            f"chat_id={chat_id}, user_id={user_id}, text='{text}'"
        )

        async with AsyncSessionLocal() as db:
            audit_service = get_audit_service(get_audit_repository(db))
            product_service = get_product_service(get_product_repository(db), audit_service)
            job_service = get_job_service(get_job_repository(db), audit_service)
            agent_service = get_agent_service(get_agent_repository(db), audit_service)
            auth_service = get_telegram_auth_service(audit_service)
            telegram_client = get_telegram_client()

            adapter = TelegramAdapter(
                telegram_client=telegram_client,
                auth_service=auth_service,
                product_service=product_service,
                job_service=job_service,
                audit_service=audit_service,
                agent_service=agent_service,
            )

            await adapter.process_update(update)

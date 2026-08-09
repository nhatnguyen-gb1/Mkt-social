import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger("aimos.telegram")


class TelegramClient:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.base_url = (
            f"https://api.telegram.org/bot{self.bot_token}"
            if self.bot_token
            else None
        )

    async def send_message(
        self, chat_id: str, text: str, parse_mode: Optional[str] = "Markdown"
    ) -> bool:
        bot_token = self.bot_token or settings.TELEGRAM_BOT_TOKEN
        base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None

        if not base_url:
            logger.warning(
                f"[MOCK TELEGRAM SEND] To chat_id={chat_id}: {text[:100]}... (TELEGRAM_BOT_TOKEN not configured)"
            )
            return True

        url = f"{base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    logger.info(f"Telegram message sent to {chat_id}")
                    return True
                elif parse_mode and response.status_code == 400:
                    # Fallback to plain text if Markdown entity parsing fails
                    logger.warning(
                        f"Telegram Markdown parse failed ({response.text}). Retrying plain text send to {chat_id}..."
                    )
                    payload.pop("parse_mode", None)
                    retry_res = await client.post(url, json=payload)
                    return retry_res.status_code == 200
                else:
                    logger.error(
                        f"Failed to send Telegram message: {response.status_code} - {response.text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram message to {chat_id}: {str(e)}")
            return False

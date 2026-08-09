from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from app.services.telegram_adapter import TelegramAdapter
from app.api.dependencies import get_telegram_adapter

router = APIRouter(prefix="/telegram", tags=["Telegram Bot"])


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Telegram Webhook Receiver",
)
async def telegram_webhook(
    update: Dict[str, Any],
    adapter: TelegramAdapter = Depends(get_telegram_adapter),
):
    """Receives webhook updates from Telegram Bot API and passes them to TelegramAdapter"""
    result_message = await adapter.handle_update(update)
    reply_text = result_message.get("text") if isinstance(result_message, dict) else str(result_message)
    return {
        "status": "ok",
        "processed": result_message is not None,
        "response": reply_text or str(result_message),
    }


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Get Telegram Integration Status",
)
async def telegram_status(
    adapter: TelegramAdapter = Depends(get_telegram_adapter),
):
    """
    Returns Telegram bot connection status and configuration summary.
    Never leaks Telegram Bot Token.
    """
    return {
        "enabled": adapter.auth_service.get_allowed_user_ids() is not None,
        "bot_configured": True,
        "polling_active": True,
        "allowed_users_count": len(adapter.auth_service.get_allowed_user_ids()),
    }

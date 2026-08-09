from typing import List, Any
from app.core.config import settings
from app.services.audit_service import AuditService


class TelegramAuthService:
    def __init__(self, audit_service: AuditService):
        self.audit_service = audit_service

    def get_allowed_user_ids(self) -> List[str]:
        raw = settings.TELEGRAM_ALLOWED_USERS or ""
        return [uid.strip() for uid in raw.split(",") if uid.strip()]

    async def is_authorized(self, telegram_user_id: Any) -> bool:
        allowed = self.get_allowed_user_ids()
        if not allowed:
            return True

        is_valid = str(telegram_user_id) in allowed
        if not is_valid:
            await self.audit_service.log_action(
                action="UNAUTHORIZED_TELEGRAM_ACCESS",
                entity_type="TelegramUser",
                actor_type="TELEGRAM_USER",
                actor_id=str(telegram_user_id),
                status="FAILURE",
                input_data={"telegram_user_id": str(telegram_user_id)},
                output_data={"error": "Access denied: Telegram User ID not authorized"},
            )
        return is_valid

    async def is_user_allowed(self, telegram_user_id: Any, **kwargs) -> bool:
        """Alias for is_authorized"""
        return await self.is_authorized(telegram_user_id)

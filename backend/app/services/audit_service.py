import uuid
from typing import Optional, Any, Union, List
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse


class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def log_action(
        self,
        *,
        action: str,
        entity_type: str,
        actor_type: str = "SYSTEM",
        actor_id: Optional[str] = None,
        entity_id: Optional[Union[uuid.UUID, str]] = None,
        input_data: Optional[Any] = None,
        output_data: Optional[Any] = None,
        status: str = "SUCCESS",
    ) -> AuditLogResponse:
        parsed_entity_id = entity_id
        if isinstance(entity_id, str):
            try:
                parsed_entity_id = uuid.UUID(entity_id)
            except ValueError:
                parsed_entity_id = None

        log_entry = await self.audit_repo.create(
            {
                "actor_type": actor_type,
                "actor_id": actor_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": parsed_entity_id,
                "input_data": input_data,
                "output_data": output_data,
                "status": status,
            }
        )
        return AuditLogResponse.model_validate(log_entry)

    async def get_audit_logs(
        self, page: int = 1, size: int = 50
    ) -> AuditLogListResponse:
        skip = (page - 1) * size
        items = await self.audit_repo.get_multi_ordered(skip=skip, limit=size)
        total = await self.audit_repo.count()
        return AuditLogListResponse(
            items=[AuditLogResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
        )

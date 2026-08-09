from fastapi import APIRouter, Depends, Query, status
from app.schemas.audit_log import AuditLogListResponse
from app.services.audit_service import AuditService
from app.api.dependencies import get_audit_service

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Audit Logs",
)
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_audit_logs(page=page, size=size)

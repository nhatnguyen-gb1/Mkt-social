"""
callback.py — Phase 3 Callback Management System
Creates and tracks scheduled mock callbacks when customer requests a callback.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class CallbackTask:
    callback_id: str
    lead_id: str
    session_id: str
    call_id: str
    phone: str
    scheduled_at: str
    reason: str
    status: str  # SCHEDULED, COMPLETED, CANCELLED
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "callback_id": self.callback_id,
            "lead_id": self.lead_id,
            "session_id": self.session_id,
            "call_id": self.call_id,
            "phone": self.phone,
            "scheduled_at": self.scheduled_at,
            "reason": self.reason,
            "status": self.status,
            "created_at": self.created_at,
        }


class CallbackManager:
    """Mock callback manager for Phase 3."""

    def __init__(self):
        self._callbacks: Dict[str, CallbackTask] = {}

    def schedule_callback(
        self,
        lead_id: str,
        session_id: str,
        call_id: str,
        phone: str,
        scheduled_at: Optional[str] = None,
        reason: str = "CUSTOMER_BUSY",
    ) -> CallbackTask:
        scheduled_time = scheduled_at or datetime.now(timezone.utc).isoformat()
        cb = CallbackTask(
            callback_id=f"cb_{uuid.uuid4().hex[:10]}",
            lead_id=lead_id,
            session_id=session_id,
            call_id=call_id,
            phone=phone,
            scheduled_at=scheduled_time,
            reason=reason,
            status="SCHEDULED",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._callbacks[cb.callback_id] = cb
        return cb

    def get_callback(self, callback_id: str) -> Optional[CallbackTask]:
        return self._callbacks.get(callback_id)

    def list_callbacks(self) -> List[CallbackTask]:
        return list(self._callbacks.values())

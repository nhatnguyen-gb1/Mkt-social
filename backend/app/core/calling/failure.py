"""
failure.py — Phase 3 Failure Handling Module
Categorizes and handles errors gracefully without crashing the call pipeline.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(str, Enum):
    NO_ANSWER = "NO_ANSWER"
    BUSY = "BUSY"
    CALL_REJECTED = "CALL_REJECTED"
    NETWORK_ERROR = "NETWORK_ERROR"
    STT_ERROR = "STT_ERROR"
    TTS_ERROR = "TTS_ERROR"
    AI_TIMEOUT = "AI_TIMEOUT"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    CUSTOMER_HANGUP = "CUSTOMER_HANGUP"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class CallError:
    error_code: ErrorCode
    message: str
    retryable: bool
    retry_count: int
    fallback_action: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code.value if isinstance(self.error_code, Enum) else self.error_code,
            "message": self.message,
            "retryable": self.retryable,
            "retry_count": self.retry_count,
            "fallback_action": self.fallback_action,
            "timestamp": self.timestamp,
        }


class FailureHandler:
    """Manages failure recovery policies and fallback actions."""

    FALLBACK_POLICIES = {
        ErrorCode.NO_ANSWER: {"retryable": True, "max_retries": 3, "fallback": "SCHEDULE_RETRY_CALL"},
        ErrorCode.BUSY: {"retryable": True, "max_retries": 2, "fallback": "SCHEDULE_CALLBACK"},
        ErrorCode.CALL_REJECTED: {"retryable": False, "max_retries": 0, "fallback": "SEND_SMS_FALLBACK"},
        ErrorCode.NETWORK_ERROR: {"retryable": True, "max_retries": 2, "fallback": "RECONNECT_CALL"},
        ErrorCode.STT_ERROR: {"retryable": True, "max_retries": 1, "fallback": "ASK_REPEAT_QUESTION"},
        ErrorCode.TTS_ERROR: {"retryable": True, "max_retries": 1, "fallback": "FALLBACK_TEXT_RESPONSE"},
        ErrorCode.AI_TIMEOUT: {"retryable": True, "max_retries": 1, "fallback": "USE_FALLBACK_DEFAULT_QUESTION"},
        ErrorCode.PROVIDER_ERROR: {"retryable": True, "max_retries": 2, "fallback": "SWITCH_MOCK_PROVIDER"},
        ErrorCode.CUSTOMER_HANGUP: {"retryable": False, "max_retries": 0, "fallback": "SAVE_QUALIFICATION_STATE"},
    }

    def handle_failure(self, error_code: ErrorCode, message: str, current_retries: int = 0) -> CallError:
        policy = self.FALLBACK_POLICIES.get(
            error_code, {"retryable": False, "max_retries": 0, "fallback": "LOG_AND_TERMINATE"}
        )
        retryable = policy["retryable"] and current_retries < policy["max_retries"]

        return CallError(
            error_code=error_code,
            message=message,
            retryable=retryable,
            retry_count=current_retries,
            fallback_action=policy["fallback"],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

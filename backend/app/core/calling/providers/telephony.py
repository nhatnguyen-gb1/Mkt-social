"""
telephony.py — Phase 3 Telephony Abstraction Layer
Interface & Mock implementation for telephony operations.
Includes contract stubs for future live providers (Twilio, Telnyx, SIP, Android).
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
import uuid


class TelephonyStatus(str, Enum):
    IDLE = "IDLE"
    DIALING = "DIALING"
    RINGING = "RINGING"
    CONNECTED = "CONNECTED"
    BUSY = "BUSY"
    NO_ANSWER = "NO_ANSWER"
    REJECTED = "REJECTED"
    DISCONNECTED = "DISCONNECTED"
    FAILED = "FAILED"


class TelephonyProvider(ABC):
    """Abstract base class for all telephony integrations."""

    @abstractmethod
    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def answer(self, call_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        pass

    @abstractmethod
    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_call_status(self, call_id: str) -> TelephonyStatus:
        pass


class MockTelephonyProvider(TelephonyProvider):
    """Mock Telephony Provider for zero-cost E2E simulation."""

    def __init__(self):
        self._calls: Dict[str, Dict[str, Any]] = {}

    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        call_id = f"call_{uuid.uuid4().hex[:10]}"
        record = {
            "call_id": call_id,
            "phone": phone,
            "status": TelephonyStatus.DIALING,
            "metadata": metadata or {},
            "audio_sent_count": 0,
            "audio_received_count": 0,
            "history": [TelephonyStatus.DIALING.value],
        }
        self._calls[call_id] = record
        # Simulate quick transition to CONNECTED for mock test efficiency
        record["status"] = TelephonyStatus.CONNECTED
        record["history"].append(TelephonyStatus.CONNECTED.value)
        return record

    def answer(self, call_id: str) -> Dict[str, Any]:
        if call_id not in self._calls:
            raise KeyError(f"Call {call_id} not found")
        call = self._calls[call_id]
        call["status"] = TelephonyStatus.CONNECTED
        call["history"].append(TelephonyStatus.CONNECTED.value)
        return call

    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        if call_id not in self._calls:
            return {"call_id": call_id, "status": TelephonyStatus.DISCONNECTED, "reason": reason}
        call = self._calls[call_id]
        call["status"] = TelephonyStatus.DISCONNECTED
        call["reason"] = reason
        call["history"].append(TelephonyStatus.DISCONNECTED.value)
        return call

    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        if call_id in self._calls:
            self._calls[call_id]["audio_sent_count"] += 1
        return {"call_id": call_id, "status": "sent", "bytes": 1024}

    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        if call_id in self._calls:
            self._calls[call_id]["audio_received_count"] += 1
        return {"call_id": call_id, "status": "received", "mock_audio_frame": True}

    def get_call_status(self, call_id: str) -> TelephonyStatus:
        call = self._calls.get(call_id)
        if not call:
            return TelephonyStatus.IDLE
        return call["status"]


class RealTelephonyProvider(TelephonyProvider):
    """
    Real Telephony Provider Adapter (Twilio/Telnyx/SIP).
    Enforces safety gate: dial is rejected unless LIVE_MODE=true AND phone is in allowlist.
    """

    def __init__(self, http_client: Optional[Any] = None):
        from app.core.config import settings
        self.settings = settings
        self.http_client = http_client
        self._calls: Dict[str, Dict[str, Any]] = {}

    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Live Call Safety Check
        if not self.settings.is_live_call_allowed(phone):
            return {
                "call_id": f"call_rejected_{uuid.uuid4().hex[:8]}",
                "phone": phone,
                "status": TelephonyStatus.REJECTED,
                "reason": "LIVE_CALL_NOT_ALLOWED_BY_SAFETY_GATE",
                "message": f"Live calling to '{phone}' is blocked. Set LIVE_MODE=true and add phone to ALLOWED_TEST_NUMBERS.",
            }

        call_id = f"real_call_{uuid.uuid4().hex[:10]}"
        record = {
            "call_id": call_id,
            "phone": phone,
            "status": TelephonyStatus.CONNECTED,
            "provider": self.settings.CALLING_PROVIDER,
            "account_sid": self.settings.TWILIO_ACCOUNT_SID or "real_sid_stub",
            "metadata": metadata or {},
        }
        self._calls[call_id] = record
        return record

    def answer(self, call_id: str) -> Dict[str, Any]:
        call = self._calls.get(call_id, {"call_id": call_id, "status": TelephonyStatus.CONNECTED})
        call["status"] = TelephonyStatus.CONNECTED
        return call

    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        call = self._calls.get(call_id, {"call_id": call_id})
        call["status"] = TelephonyStatus.DISCONNECTED
        call["reason"] = reason
        return call

    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        return {"call_id": call_id, "status": "sent", "bytes": 1024, "provider": "real"}

    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        return {"call_id": call_id, "status": "received", "provider": "real"}

    def get_call_status(self, call_id: str) -> TelephonyStatus:
        call = self._calls.get(call_id)
        if not call:
            return TelephonyStatus.IDLE
        return call["status"]


# ── LIVE PROVIDER CONTRACT STUBS (Phase 3 Interface Only — NO LIVE EXECUTION) ─

class TwilioProvider(TelephonyProvider):
    """Twilio Telephony Provider Contract (Interface stub for Phase 4+)."""
    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("TwilioProvider live execution is disabled in Phase 3.")

    def answer(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("TwilioProvider live execution is disabled in Phase 3.")

    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        raise NotImplementedError("TwilioProvider live execution is disabled in Phase 3.")

    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        raise NotImplementedError("TwilioProvider live execution is disabled in Phase 3.")

    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("TwilioProvider live execution is disabled in Phase 3.")

    def get_call_status(self, call_id: str) -> TelephonyStatus:
        raise NotImplementedError("TwilioProvider live execution is disabled in Phase 3.")


class TelnyxProvider(TelephonyProvider):
    """Telnyx Telephony Provider Contract (Interface stub for Phase 4+)."""
    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("TelnyxProvider live execution is disabled in Phase 3.")

    def answer(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("TelnyxProvider live execution is disabled in Phase 3.")

    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        raise NotImplementedError("TelnyxProvider live execution is disabled in Phase 3.")

    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        raise NotImplementedError("TelnyxProvider live execution is disabled in Phase 3.")

    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("TelnyxProvider live execution is disabled in Phase 3.")

    def get_call_status(self, call_id: str) -> TelephonyStatus:
        raise NotImplementedError("TelnyxProvider live execution is disabled in Phase 3.")


class SIPProvider(TelephonyProvider):
    """SIP/Trunking Provider Contract (Interface stub for Phase 4+)."""
    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("SIPProvider live execution is disabled in Phase 3.")

    def answer(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("SIPProvider live execution is disabled in Phase 3.")

    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        raise NotImplementedError("SIPProvider live execution is disabled in Phase 3.")

    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        raise NotImplementedError("SIPProvider live execution is disabled in Phase 3.")

    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("SIPProvider live execution is disabled in Phase 3.")

    def get_call_status(self, call_id: str) -> TelephonyStatus:
        raise NotImplementedError("SIPProvider live execution is disabled in Phase 3.")


class AndroidProvider(TelephonyProvider):
    """Android Automation Telephony Provider Contract (Interface stub for Phase 4+)."""
    def dial(self, phone: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("AndroidProvider live execution is disabled in Phase 3.")

    def answer(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("AndroidProvider live execution is disabled in Phase 3.")

    def hangup(self, call_id: str, reason: str = "normal") -> Dict[str, Any]:
        raise NotImplementedError("AndroidProvider live execution is disabled in Phase 3.")

    def send_audio(self, call_id: str, audio_payload: Any) -> Dict[str, Any]:
        raise NotImplementedError("AndroidProvider live execution is disabled in Phase 3.")

    def receive_audio(self, call_id: str) -> Dict[str, Any]:
        raise NotImplementedError("AndroidProvider live execution is disabled in Phase 3.")

    def get_call_status(self, call_id: str) -> TelephonyStatus:
        raise NotImplementedError("AndroidProvider live execution is disabled in Phase 3.")

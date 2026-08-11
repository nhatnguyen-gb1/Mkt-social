"""
stt.py — Phase 3 Speech-To-Text Abstraction Layer
Interface & Mock STT provider.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class STTProvider(ABC):
    """Abstract interface for Speech-to-Text conversion."""

    @abstractmethod
    def transcribe(self, audio_data: Any, language: str = "vi-VN") -> Dict[str, Any]:
        """Transcribe audio into text payload."""
        pass


class MockSTTProvider(STTProvider):
    """Mock STT provider that converts audio payload or raw text into structured STT result."""

    def transcribe(self, audio_data: Any, language: str = "vi-VN") -> Dict[str, Any]:
        if isinstance(audio_data, str):
            text = audio_data
        elif isinstance(audio_data, dict) and "text" in audio_data:
            text = audio_data["text"]
        else:
            text = "Anh đang tìm mua căn hộ."

        return {
            "transcript": text,
            "confidence": 0.98,
            "language": language,
            "duration_seconds": round(len(text) * 0.15, 2),
            "is_final": True,
        }


class RealSTTProvider(STTProvider):
    """Contract stub for live external STT API (Deepgram/Whisper/Google STT). Disabled in Phase 3."""

    def transcribe(self, audio_data: Any, language: str = "vi-VN") -> Dict[str, Any]:
        raise NotImplementedError("RealSTTProvider live execution is disabled in Phase 3.")

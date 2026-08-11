"""
tts.py — Phase 3 Text-To-Speech Abstraction Layer
Interface & Mock TTS provider.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class TTSProvider(ABC):
    """Abstract interface for Text-to-Speech synthesis."""

    @abstractmethod
    def synthesize(self, text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        """Synthesize text into speech audio payload."""
        pass


class MockTTSProvider(TTSProvider):
    """Mock TTS provider that returns mock audio payload without external network calls."""

    def synthesize(self, text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        voice = voice_id or "vi_female_southern_v1"
        return {
            "text": text,
            "voice_id": voice,
            "audio_format": "wav",
            "sample_rate": 16000,
            "audio_bytes_length": len(text) * 320,
            "duration_seconds": round(len(text) * 0.12, 2),
            "mock_audio_stream": f"data:audio/wav;base64,MOCK_AUDIO_{len(text)}",
        }


class RealTTSProvider(TTSProvider):
    """Contract stub for live external TTS API (ElevenLabs/Google TTS/VNAV). Disabled in Phase 3."""

    def synthesize(self, text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError("RealTTSProvider live execution is disabled in Phase 3.")

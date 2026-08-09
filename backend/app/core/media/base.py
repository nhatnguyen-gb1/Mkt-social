from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MediaUsageRecord(BaseModel):
    provider: str
    media_type: str  # IMAGE, VIDEO
    prompt: str
    cost_usd: float = 0.0


class BaseImageGenerator(ABC):
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "vivid",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generates an image from a visual text prompt.
        Returns dictionary containing:
        - file_url: URL to the generated image
        - prompt: The prompt used
        - provider: Name of the generator provider
        - metadata: Additional data (size, style, model, etc.)
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the identifier name of the media provider."""
        pass

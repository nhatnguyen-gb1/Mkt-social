import hashlib
import logging
from typing import Dict, Any
from app.core.media.base import BaseImageGenerator

logger = logging.getLogger("aimos.media.mock")


class MockImageGenerator(BaseImageGenerator):
    """
    Mock Image Generator for standalone local development and automated testing.
    Generates deterministic SVG / placeholder URLs with zero API cost.
    """

    def get_provider_name(self) -> str:
        return "mock"

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "vivid",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        logger.info(f"[MOCK IMAGE GENERATOR] Generating image for prompt: '{prompt[:50]}...'")
        
        # Create deterministic hash based on prompt for consistent URL generation
        prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]
        placeholder_url = f"https://placehold.co/1024x1024/2b2d42/8d99ae?text=AIMOS+Ad+Creative+{prompt_hash}"

        return {
            "file_url": placeholder_url,
            "prompt": prompt,
            "provider": self.get_provider_name(),
            "metadata": {
                "size": size,
                "style": style,
                "model": "mock-dall-e-3",
                "estimated_cost_usd": 0.0,
                "is_mock": True,
            },
        }

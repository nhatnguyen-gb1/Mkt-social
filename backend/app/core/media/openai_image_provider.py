import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.core.media.base import BaseImageGenerator

logger = logging.getLogger("aimos.media.openai")


class OpenAIImageGenerator(BaseImageGenerator):
    """
    OpenAI DALL-E 3 Image Generator.
    Requires OPENAI_API_KEY to be set in environment settings.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIImageGenerator")

    def get_provider_name(self) -> str:
        return "openai"

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "vivid",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        logger.info(f"[OPENAI DALL-E 3] Requesting image generation for prompt: '{prompt[:50]}...'")
        
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "style": style,
            "quality": kwargs.get("quality", "standard"),
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"[OPENAI DALL-E 3 API ERROR] {response.status_code}: {response.text}")
                raise RuntimeError(f"OpenAI Image API failed with status {response.status_code}: {response.text}")

            data = response.json()
            image_url = data["data"][0]["url"]
            revised_prompt = data["data"][0].get("revised_prompt", prompt)

            return {
                "file_url": image_url,
                "prompt": revised_prompt,
                "provider": self.get_provider_name(),
                "metadata": {
                    "size": size,
                    "style": style,
                    "model": "dall-e-3",
                    "original_prompt": prompt,
                    "estimated_cost_usd": 0.04,  # Standard DALL-E 3 1024x1024 image cost
                    "is_mock": False,
                },
            }

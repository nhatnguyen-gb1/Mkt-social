import logging
from app.core.config import settings
from app.core.media.base import BaseImageGenerator
from app.core.media.mock_media_provider import MockImageGenerator
from app.core.media.openai_image_provider import OpenAIImageGenerator

logger = logging.getLogger("aimos.media.factory")


class MediaGeneratorFactory:
    """
    Factory for resolving Image & Media Generation Providers.
    Falls back safely to MockImageGenerator if API key is not configured or mock is specified.
    """

    @staticmethod
    def get_image_generator(provider_name: str = None) -> BaseImageGenerator:
        target = (provider_name or "mock").lower()

        if target in ["openai", "dall-e", "dall-e-3"]:
            if settings.OPENAI_API_KEY:
                try:
                    return OpenAIImageGenerator()
                except Exception as exc:
                    logger.warning(
                        f"Failed to initialize OpenAIImageGenerator ({exc}). Falling back to MockImageGenerator."
                    )
                    return MockImageGenerator()
            else:
                logger.info(
                    "OPENAI_API_KEY is not configured in settings. Falling back to MockImageGenerator."
                )
                return MockImageGenerator()

        elif target == "mock":
            return MockImageGenerator()

        else:
            logger.info(
                f"Unknown or unconfigured media provider '{target}'. Falling back to MockImageGenerator."
            )
            return MockImageGenerator()

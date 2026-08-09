import logging
from typing import Optional
from app.core.config import settings
from app.core.llm.base import BaseLLMProvider
from app.core.llm.mock_provider import MockLLMProvider
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.anthropic_provider import AnthropicProvider
from app.core.llm.gemini_provider import GeminiProvider

logger = logging.getLogger("aimos.llm.factory")


class LLMProviderFactory:
    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
        target = (provider_name or settings.DEFAULT_LLM_PROVIDER or "mock").lower()

        if target == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY missing. Falling back to MockLLMProvider.")
                return MockLLMProvider()
            return OpenAIProvider()

        elif target == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("ANTHROPIC_API_KEY missing. Falling back to MockLLMProvider.")
                return MockLLMProvider()
            return AnthropicProvider()

        elif target == "gemini":
            gemini_key = getattr(settings, "GEMINI_API_KEY", None)
            if not gemini_key:
                logger.warning("GEMINI_API_KEY missing. Falling back to MockLLMProvider.")
                return MockLLMProvider()
            return GeminiProvider()

        else:
            if target != "mock":
                logger.info(f"Unknown or requested provider '{target}'. Using MockLLMProvider.")
            return MockLLMProvider()

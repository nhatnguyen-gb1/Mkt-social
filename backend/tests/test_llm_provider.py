import pytest
from app.core.config import settings
from app.core.llm import (
    MockLLMProvider,
    LLMProviderFactory,
)
from app.schemas.agent import MarketResearchResult


@pytest.mark.asyncio
async def test_mock_llm_provider_generate():
    provider = MockLLMProvider()
    text = await provider.generate("Test prompt")
    assert "[MOCK LLM RESPONSE]" in text
    assert provider.get_provider_name() == "mock"
    usage = provider.get_last_usage()
    assert usage.total_tokens > 0


@pytest.mark.asyncio
async def test_mock_llm_provider_generate_structured():
    provider = MockLLMProvider()
    prompt = "Sản phẩm: Mooncake\nThị trường: Vietnam"
    result = await provider.generate_structured(prompt, MarketResearchResult)

    assert isinstance(result, MarketResearchResult)
    assert result.product_name == "Mooncake"
    assert result.target_market == "Vietnam"
    assert len(result.opportunities) > 0
    assert len(result.recommended_marketing_angles) > 0


def test_llm_provider_factory_fallback():
    # Force mock provider requested
    p_mock = LLMProviderFactory.get_provider("mock")
    assert p_mock.get_provider_name() == "mock"

    # Request openai without API key -> falls back to mock
    settings.OPENAI_API_KEY = None
    p_openai_fallback = LLMProviderFactory.get_provider("openai")
    assert p_openai_fallback.get_provider_name() == "mock"

    # Request anthropic without API key -> falls back to mock
    settings.ANTHROPIC_API_KEY = None
    p_anthropic_fallback = LLMProviderFactory.get_provider("anthropic")
    assert p_anthropic_fallback.get_provider_name() == "mock"

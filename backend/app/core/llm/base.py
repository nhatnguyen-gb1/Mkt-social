from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Any, Dict
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMUsageRecord(BaseModel):
    provider: str
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generates a text completion for the given prompt"""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        """Generates a structured Pydantic object for the given prompt"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the canonical provider name (e.g. 'openai', 'anthropic', 'gemini', 'mock')"""
        pass

    @abstractmethod
    def get_last_usage(self) -> LLMUsageRecord:
        """Returns token usage metadata from the most recent LLM invocation"""
        pass

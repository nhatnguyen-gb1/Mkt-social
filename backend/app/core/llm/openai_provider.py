import json
import logging
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.llm.base import BaseLLMProvider, LLMUsageRecord

logger = logging.getLogger("aimos.llm.openai")
T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model_name
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        self._last_usage = LLMUsageRecord(
            provider="openai",
            model_name=self.model_name,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            estimated_cost_usd=0.0,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured in environment variables. "
                "Please set OPENAI_API_KEY or use DEFAULT_LLM_PROVIDER=mock."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.endpoint, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"OpenAI API Error ({response.status_code}): {response.text}")

            res_data = response.json()
            usage = res_data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            comp_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # Rough cost estimation for gpt-4o-mini
            cost = (prompt_tokens * 0.15 / 1000000) + (comp_tokens * 0.60 / 1000000)

            self._last_usage = LLMUsageRecord(
                provider="openai",
                model_name=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
            )

            return res_data["choices"][0]["message"]["content"]

    async def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema_json = json.dumps(schema_class.model_json_schema(), indent=2)
        instruction = (
            f"{system_prompt or ''}\n\n"
            "IMPORTANT: Respond ONLY with a valid JSON object matching the JSON Schema below.\n"
            f"Schema:\n```json\n{schema_json}\n```"
        )
        raw_text = await self.generate(prompt=prompt, system_prompt=instruction, temperature=0.2)
        
        # Clean potential markdown formatting
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        data = json.loads(cleaned_text.strip())
        return schema_class.model_validate(data)

    def get_provider_name(self) -> str:
        return "openai"

    def get_last_usage(self) -> LLMUsageRecord:
        return self._last_usage

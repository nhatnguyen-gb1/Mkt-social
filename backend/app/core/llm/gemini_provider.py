import json
import logging
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.llm.base import BaseLLMProvider, LLMUsageRecord

logger = logging.getLogger("aimos.llm.gemini")
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", None)
        self.model_name = model_name
        self._last_usage = LLMUsageRecord(
            provider="gemini",
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
                "GEMINI_API_KEY is not configured in environment variables. "
                "Please set GEMINI_API_KEY or use DEFAULT_LLM_PROVIDER=mock."
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Gemini API Error ({response.status_code}): {response.text}")

            res_data = response.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini returned empty response candidates.")

            text = candidates[0]["content"]["parts"][0]["text"]
            
            usage = res_data.get("usageMetadata", {})
            prompt_tokens = usage.get("promptTokenCount", 0)
            comp_tokens = usage.get("candidatesTokenCount", 0)
            total_tokens = usage.get("totalTokenCount", 0)

            self._last_usage = LLMUsageRecord(
                provider="gemini",
                model_name=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=0.0,
            )

            return text

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
        return "gemini"

    def get_last_usage(self) -> LLMUsageRecord:
        return self._last_usage

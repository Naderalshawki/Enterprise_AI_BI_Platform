import json
import logging
from typing import AsyncGenerator
import httpx

from src.modules.llm.domain.entities import LLMRequest, LLMResponse, TokenUsage, ModelInfo
from src.modules.llm.domain.value_objects import AICapability
from src.modules.llm.infrastructure.providers.base_provider import BaseProvider
from src.modules.llm.infrastructure.config.provider_config import ProviderConfig

logger = logging.getLogger(__name__)

class GroqProvider(BaseProvider):
    """
    Groq Cloud AI Provider (Super Fast Inference).
    """
    capabilities = {
        AICapability.CHAT,
        AICapability.STREAMING,
    }

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self.base_url = (config.base_url or "https://api.groq.com/openai/v1").rstrip("/")
        # استخدام نموذج Groq السريع الذي حددته أنت
        self.default_model = config.default_model or "openai/gpt-oss-120b"
        
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("Initialized Groq provider: %s", self.default_model)

    def _format_messages(self, request: LLMRequest) -> list[dict]:
        return [{"role": message.role.value, "content": message.content} for message in request.messages]

    async def generate(self, request: LLMRequest) -> LLMResponse:
        endpoint = f"{self.base_url}/chat/completions"
        model = request.model or self.default_model
        
        payload = {
            "model": model,
            "messages": self._format_messages(request),
            "temperature": request.temperature,
            "stream": False,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(endpoint, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()

            usage = data.get("usage", {})
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=self.config.provider,
                model=model,
                usage=TokenUsage(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
            )
        except httpx.HTTPError as exc:
            logger.exception("Groq request failed")
            raise RuntimeError(f"Groq request failed: {exc}") from exc

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        endpoint = f"{self.base_url}/chat/completions"
        model = request.model or self.default_model
        
        payload = {
            "model": model,
            "messages": self._format_messages(request),
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                async with client.stream("POST", endpoint, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: ") and line.strip() != "data: [DONE]":
                            chunk_data = json.loads(line[6:])
                            content = chunk_data["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
        except httpx.HTTPError as exc:
            logger.exception("Groq streaming failed")
            raise RuntimeError(f"Groq streaming failed: {exc}") from exc

    async def health_check(self) -> bool:
        return True
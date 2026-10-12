from typing import AsyncGenerator

from google import genai
from google.genai import types

from src.modules.llm.domain.entities import (
    LLMRequest,
    LLMResponse,
    ModelInfo,
    EmbeddingRequest,
    EmbeddingResponse,
    VisionRequest,
    VisionResponse,
)

from src.modules.llm.domain.value_objects import (
    AICapability,
    ProviderName,
)

from src.modules.llm.infrastructure.providers.base_provider import (
    BaseProvider,
)

from src.modules.llm.infrastructure.config.provider_config import (
    ProviderConfig,
)

from src.modules.llm.infrastructure.mappers.request_mapper import (
    RequestMapper,
)

from src.modules.llm.infrastructure.mappers.response_mapper import (
    ResponseMapper,
)


class GeminiProvider(BaseProvider):
    """
    Google Gemini Provider
    """

    capabilities = {
        AICapability.CHAT,
        AICapability.EMBEDDING,
        AICapability.VISION,
    }

    def __init__(
        self,
        config: ProviderConfig,
    ):
        super().__init__(config)

        self.client = genai.Client(
            api_key=config.api_key,
        )

    # ==========================================================
    # Chat
    # ==========================================================

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        prompt = RequestMapper.to_gemini_prompt(
            request,
        )

        response = await self.client.aio.models.generate_content(
            model=request.model,
            contents=prompt,
        )

        return ResponseMapper.from_gemini(
            response=response,
            model=request.model,
        )

    # ==========================================================
    # Stream
    # ==========================================================

    async def generate_stream(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[str, None]:

        prompt = RequestMapper.to_gemini_prompt(
            request,
        )

        stream = await self.client.aio.models.generate_content_stream(
            model=request.model,
            contents=prompt,
        )

        async for chunk in stream:

            if getattr(
                chunk,
                "text",
                None,
            ):
                yield chunk.text

    # ==========================================================
    # Vision
    # ==========================================================

    async def vision(
        self,
        request: VisionRequest,
    ) -> VisionResponse:

        image_part = types.Part.from_bytes(
            data=request.image,
            mime_type=request.mime_type,
        )

        response = await self.client.aio.models.generate_content(
            model=request.model,
            contents=[
                image_part,
                request.prompt,
            ],
        )

        return ResponseMapper.from_gemini_vision(
            response=response,
            model=request.model,
        )

    # ==========================================================
    # Embeddings
    # ==========================================================

    async def embed(
        self,
        request: EmbeddingRequest,
    ) -> EmbeddingResponse:

        response = await self.client.aio.models.embed_content(
            **RequestMapper.to_gemini_embedding_request(
                request,
            )
        )

        return ResponseMapper.from_gemini_embedding(
            response=response,
            model=request.model,
        )

    # ==========================================================
    # Models
    # ==========================================================

    async def list_models(
        self,
    ) -> list[ModelInfo]:

        response = await self.client.aio.models.list()

        models = []

        for model in response:

            models.append(
                ModelInfo(
                    provider=ProviderName.GEMINI,
                    model_name=model.name,
                    supports_stream=True,
                    supports_json=True,
                    context_window=getattr(
                        model,
                        "input_token_limit",
                        None,
                    ),
                )
            )

        return models

    # ==========================================================
    # Health
    # ==========================================================

    async def health_check(
        self,
    ) -> bool:

        try:

            await self.client.aio.models.generate_content(
                model=self.config.default_model,
                contents="Hello",
            )

            return True

        except Exception as e:

            print(
                "Gemini Health Error:",
                e,
            )

            return False
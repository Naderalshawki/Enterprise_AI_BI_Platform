
from src.modules.llm.domain.interfaces import (
    LLMProvider,
    LLMRouter,
)

from src.modules.llm.domain.value_objects import (
    ProviderName,
)

from src.modules.llm.infrastructure.factory import (
    ProviderFactory,
)


class DefaultLLMRouter(LLMRouter):
    """
    Default implementation of the LLM Router.
    """

    def __init__(
        self,
        factory: ProviderFactory,
    ) -> None:
        self.factory = factory

    def get_provider(
        self,
        provider: ProviderName,
    ) -> LLMProvider:
        provider_key = ProviderName(provider)
        registered_providers = self.factory.providers

        try:
            return registered_providers[provider_key]
        except KeyError:
            raise ValueError(
                f"Provider '{provider_key.value}' is not registered."
            ) from None

    def get_default_provider(self) -> LLMProvider:
        return self.factory.get_default()

    def get_all_providers(self) -> list[LLMProvider]:
        return list(self.factory.providers.values())

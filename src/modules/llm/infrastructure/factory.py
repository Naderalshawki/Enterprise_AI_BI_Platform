from src.modules.llm.domain.interfaces import (
    LLMProvider,
)

from src.modules.llm.domain.value_objects import (
    ProviderName,
)


class ProviderFactory:
    """
    Registry for all LLM providers.
    """

    def __init__(self):
        self._providers: dict[ProviderName, LLMProvider] = {}

    # ==========================================================
    # Register
    # ==========================================================

    def register(
        self,
        provider: LLMProvider,
    ) -> None:

        self._providers[
            ProviderName(provider.provider_name)
        ] = provider

    # ==========================================================
    # Get Provider
    # ==========================================================

    def get(
        self,
        provider: ProviderName,
    ) -> LLMProvider:

        try:
            return self._providers[provider]

        except KeyError:

            raise ValueError(
                f"Provider '{provider.value}' is not registered."
            ) from None

    # ==========================================================
    # Default Provider
    # ==========================================================

    def get_default(
        self,
    ) -> LLMProvider:

        if not self._providers:
            raise ValueError(
                "No providers registered."
            )

        return next(
            iter(self._providers.values())
        )

    # ==========================================================
    # All Providers
    # ==========================================================

    @property
    def providers(
        self,
    ) -> dict[ProviderName, LLMProvider]:

        return self._providers

    # ==========================================================
    # Exists
    # ==========================================================

    def exists(
        self,
        provider: ProviderName,
    ) -> bool:

        return provider in self._providers
"""LLM Provider Factory for OpenRouter and HuggingFace/Novita."""

from typing import Any, Literal

from langchain_openai import ChatOpenAI

from config.settings import get_settings

# =============================================================================
# Provider Configurations
# =============================================================================

PROVIDERS_CONFIG = {
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            {
                "id": "google/gemini-2.0-flash-exp:free",
                "name": "Gemini 2.0 Flash (Free)",
                "context_window": 1000000,
            },
            {
                "id": "google/gemini-2.0-flash-thinking-exp:free",
                "name": "Gemini 2.0 Flash Thinking (Free)",
                "context_window": 1000000,
            },
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "context_window": 200000,
            },
            {
                "id": "meta-llama/llama-3.1-405b-instruct",
                "name": "Llama 3.1 405B",
                "context_window": 131072,
            },
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "context_window": 128000,
            },
            {
                "id": "openai/gpt-4o-mini",
                "name": "GPT-4o Mini",
                "context_window": 128000,
            },
        ],
    },
    "huggingface_novita": {
        "name": "HuggingFace (Novita)",
        "base_url": "https://router.huggingface.co/v1",
        "models": [
            {
                "id": "meta-llama/Llama-3.1-70B-Instruct:novita",
                "name": "Llama 3.1 70B Instruct",
                "context_window": 131072,
            },
            {
                "id": "meta-llama/Llama-3.1-8B-Instruct:novita",
                "name": "Llama 3.1 8B Instruct",
                "context_window": 131072,
            },
            {
                "id": "mistralai/Mixtral-8x22B-Instruct-v0.1:novita",
                "name": "Mixtral 8x22B Instruct",
                "context_window": 65536,
            },
            {
                "id": "mistralai/Mistral-7B-Instruct-v0.3:novita",
                "name": "Mistral 7B Instruct",
                "context_window": 32768,
            },
            {
                "id": "Qwen/Qwen2.5-72B-Instruct:novita",
                "name": "Qwen 2.5 72B Instruct",
                "context_window": 131072,
            },
            {
                "id": "deepseek-ai/DeepSeek-R1:novita",
                "name": "DeepSeek R1",
                "context_window": 65536,
            },
        ],
    },
}


class LLMProviderFactory:
    """Factory for creating LLM instances from different providers."""

    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available provider IDs."""
        return list(PROVIDERS_CONFIG.keys())

    @staticmethod
    def get_provider_display_names() -> dict[str, str]:
        """Get mapping of provider ID to display name."""
        return {pid: cfg["name"] for pid, cfg in PROVIDERS_CONFIG.items()}

    @staticmethod
    def get_models_for_provider(provider: str) -> list[dict[str, Any]]:
        """Get available models for a provider."""
        if provider not in PROVIDERS_CONFIG:
            raise ValueError(f"Unknown provider: {provider}")
        return PROVIDERS_CONFIG[provider]["models"]

    @staticmethod
    def get_model_choices_for_provider(provider: str) -> list[tuple[str, str]]:
        """Get model choices as (display_name, model_id) tuples for Gradio dropdown."""
        models = LLMProviderFactory.get_models_for_provider(provider)
        return [(m["name"], m["id"]) for m in models]

    @staticmethod
    def create_llm(
        provider: Literal["openrouter", "huggingface_novita"] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> ChatOpenAI:
        """
        Create an LLM instance for the specified provider and model.

        Args:
            provider: The LLM provider to use. Defaults to settings.
            model: The model ID to use. Defaults to settings.
            temperature: Temperature for generation. Defaults to settings.
            max_tokens: Maximum tokens to generate. Defaults to settings.
            **kwargs: Additional arguments passed to ChatOpenAI.

        Returns:
            Configured ChatOpenAI instance.
        """
        settings = get_settings()

        # Apply defaults from settings
        provider = provider or settings.default_llm_provider
        model = model or settings.default_llm_model
        temperature = temperature if temperature is not None else settings.default_temperature
        max_tokens = max_tokens or settings.default_max_tokens

        if provider not in PROVIDERS_CONFIG:
            raise ValueError(f"Unknown provider: {provider}")

        config = PROVIDERS_CONFIG[provider]
        base_url = config["base_url"]

        # Get API key based on provider
        if provider == "openrouter":
            api_key = settings.openrouter_api_key
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not set in environment")
            # OpenRouter requires extra headers
            default_headers = {
                "HTTP-Referer": "https://fintech-skilled-agents.local",
                "X-Title": "Fintech Skilled Agents",
            }
            kwargs.setdefault("default_headers", default_headers)

        elif provider == "huggingface_novita":
            # HuggingFace router uses HF_TOKEN for authentication
            # Requests are routed to Novita via HuggingFace infrastructure
            # See: https://huggingface.co/docs/inference-providers/providers/novita
            api_key = settings.huggingface_token
            if not api_key:
                raise ValueError("HUGGINGFACE_TOKEN not set in environment (required for HuggingFace router)")
        else:
            raise ValueError(f"Unknown provider: {provider}")

        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    **kwargs: Any,
) -> ChatOpenAI:
    """Convenience function to get an LLM instance."""
    return LLMProviderFactory.create_llm(provider=provider, model=model, **kwargs)

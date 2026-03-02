"""API client factory."""

from typing import Any

from .base import BaseAPIClient
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient


def create_client(provider: str, **kwargs: Any) -> BaseAPIClient:
    """Create an API client based on provider name.

    Args:
        provider: Provider name ('openai' or 'ollama').
        **kwargs: Provider-specific configuration.

    Returns:
        Configured API client instance.

    Raises:
        ValueError: If provider is not supported.
    """
    if provider == "openai":
        return OpenAIClient(
            base_url=kwargs.get("base_url", "https://api.openai.com/v1"),
            model=kwargs.get("model", "gpt-4o-mini"),
            api_key=kwargs.get("api_key", ""),
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.3),
        )
    elif provider == "ollama":
        return OllamaClient(
            base_url=kwargs.get("base_url", "http://localhost:11434"),
            model=kwargs.get("model", "llama3"),
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.3),
        )
    else:
        raise ValueError(f"Unsupported API provider: {provider}")

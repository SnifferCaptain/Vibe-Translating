"""Ollama API client."""

from typing import Any, Optional

import httpx

from .base import BaseAPIClient, ChatResponse, Message


class OllamaClient(BaseAPIClient):
    """Client for Ollama local API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        **kwargs: Any,
    ) -> None:
        """Initialize Ollama client.

        Args:
            base_url: Ollama server URL.
            model: Model name.
            **kwargs: Additional configuration.
        """
        super().__init__(base_url, model, **kwargs)

    def chat(
        self,
        messages: list[Message],
        tools: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat request to Ollama API.

        Args:
            messages: List of chat messages.
            tools: Optional tool definitions.
            **kwargs: Additional parameters.

        Returns:
            Chat response.

        Raises:
            httpx.HTTPStatusError: If API request fails.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": self._build_messages(messages),
            "stream": False,
            "options": {
                "num_predict": kwargs.get(
                    "max_tokens", self.max_tokens
                ),
                "temperature": kwargs.get(
                    "temperature", self.temperature
                ),
            },
        }
        if tools:
            payload["tools"] = tools

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        message = data.get("message", {})

        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return ChatResponse(
            content=message.get("content", ""),
            role=message.get("role", "assistant"),
            finish_reason="stop",
            tool_calls=message.get("tool_calls"),
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )

    def is_available(self) -> bool:
        """Check if Ollama service is running.

        Returns:
            True if Ollama is reachable.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

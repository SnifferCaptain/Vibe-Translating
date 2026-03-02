"""OpenAI-compatible API client."""

from typing import Any, Optional

import httpx

from .base import BaseAPIClient, ChatResponse, Message


class OpenAIClient(BaseAPIClient):
    """Client for OpenAI-compatible APIs."""

    def __init__(
        self,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        api_key: str = "",
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI client.

        Args:
            base_url: API base URL.
            model: Model name.
            api_key: API key for authentication.
            **kwargs: Additional configuration.
        """
        super().__init__(base_url, model, **kwargs)
        self.api_key = api_key

    def chat(
        self,
        messages: list[Message],
        tools: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat completion request to OpenAI-compatible API.

        Args:
            messages: List of chat messages.
            tools: Optional tool definitions.
            **kwargs: Additional parameters.

        Returns:
            Chat response.

        Raises:
            httpx.HTTPStatusError: If API request fails.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": self._build_messages(messages),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
        }
        if tools:
            payload["tools"] = tools

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]
        usage = data.get("usage", {})

        return ChatResponse(
            content=message.get("content", ""),
            role=message.get("role", "assistant"),
            finish_reason=choice.get("finish_reason", "stop"),
            tool_calls=message.get("tool_calls"),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
        )

    def is_available(self) -> bool:
        """Check if OpenAI API is reachable.

        Returns:
            True if API responds to models endpoint.
        """
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    f"{self.base_url}/models",
                    headers=headers,
                )
                return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

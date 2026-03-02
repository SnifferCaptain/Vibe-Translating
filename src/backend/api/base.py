"""Base API client interface for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Message:
    """A chat message."""

    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[list[dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ChatResponse:
    """Response from a chat completion."""

    content: str
    role: str = "assistant"
    finish_reason: str = "stop"
    tool_calls: Optional[list[dict[str, Any]]] = None
    usage: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "role": self.role,
            "finish_reason": self.finish_reason,
            "tool_calls": self.tool_calls,
            "usage": self.usage,
        }


class BaseAPIClient(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(self, base_url: str, model: str, **kwargs: Any) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL of the API.
            model: Model name to use.
            **kwargs: Additional configuration.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = kwargs.get("max_tokens", 4096)
        self.temperature = kwargs.get("temperature", 0.3)

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        tools: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send a chat completion request.

        Args:
            messages: List of chat messages.
            tools: Optional list of tool definitions.
            **kwargs: Additional parameters.

        Returns:
            Chat response from the model.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the API service is available.

        Returns:
            True if the service is reachable.
        """

    def _build_messages(
        self, messages: list[Message]
    ) -> list[dict[str, Any]]:
        """Convert Message objects to API format.

        Args:
            messages: List of Message objects.

        Returns:
            List of message dictionaries.
        """
        result = []
        for msg in messages:
            d: dict[str, Any] = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.name:
                d["name"] = msg.name
            if msg.tool_calls:
                d["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                d["tool_call_id"] = msg.tool_call_id
            result.append(d)
        return result

"""Tests for API clients."""

import pytest

from src.backend.api.base import Message, ChatResponse
from src.backend.api.openai_client import OpenAIClient
from src.backend.api.ollama_client import OllamaClient
from src.backend.api.factory import create_client
from tests.mock_server import MockServer


@pytest.fixture(scope="module")
def mock_server() -> MockServer:
    """Start mock API server for testing."""
    server = MockServer()
    server.start()
    yield server
    server.stop()


class TestMessage:
    """Tests for Message dataclass."""

    def test_create_message(self) -> None:
        """Test creating a message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_optional_fields(self) -> None:
        """Test optional message fields."""
        msg = Message(role="user", content="Hello")
        assert msg.name is None
        assert msg.tool_calls is None


class TestChatResponse:
    """Tests for ChatResponse dataclass."""

    def test_to_dict(self) -> None:
        """Test converting response to dict."""
        resp = ChatResponse(content="Hello", usage={})
        d = resp.to_dict()
        assert d["content"] == "Hello"
        assert d["role"] == "assistant"


class TestOpenAIClient:
    """Tests for OpenAI client with mock server."""

    def test_chat(self, mock_server: MockServer) -> None:
        """Test chat completion."""
        client = OpenAIClient(
            base_url=mock_server.openai_url,
            model="mock-model",
        )
        messages = [
            Message(role="user", content="こんにちは")
        ]
        resp = client.chat(messages)
        assert resp.content
        assert resp.role == "assistant"

    def test_is_available(
        self, mock_server: MockServer
    ) -> None:
        """Test availability check."""
        client = OpenAIClient(
            base_url=mock_server.openai_url,
            model="mock-model",
        )
        assert client.is_available()

    def test_unavailable(self) -> None:
        """Test unavailable server."""
        client = OpenAIClient(
            base_url="http://localhost:19999",
            model="mock-model",
        )
        assert not client.is_available()


class TestOllamaClient:
    """Tests for Ollama client with mock server."""

    def test_chat(self, mock_server: MockServer) -> None:
        """Test chat completion."""
        client = OllamaClient(
            base_url=mock_server.ollama_url,
            model="mock-model",
        )
        messages = [
            Message(role="user", content="Hello")
        ]
        resp = client.chat(messages)
        assert resp.content
        assert resp.role == "assistant"

    def test_is_available(
        self, mock_server: MockServer
    ) -> None:
        """Test availability check."""
        client = OllamaClient(
            base_url=mock_server.ollama_url,
            model="mock-model",
        )
        assert client.is_available()


class TestFactory:
    """Tests for API client factory."""

    def test_create_openai(self) -> None:
        """Test creating OpenAI client."""
        client = create_client("openai")
        assert isinstance(client, OpenAIClient)

    def test_create_ollama(self) -> None:
        """Test creating Ollama client."""
        client = create_client("ollama")
        assert isinstance(client, OllamaClient)

    def test_invalid_provider(self) -> None:
        """Test invalid provider raises error."""
        with pytest.raises(ValueError):
            create_client("invalid")

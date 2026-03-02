"""Tests for agent system."""

import tempfile
from pathlib import Path

import pytest

from src.backend.agent.memory import AgentMemory, TermEntry
from src.backend.agent.tools import Tool, ToolRegistry
from src.backend.agent.context import ContextManager
from src.backend.agent.core import TranslationAgent
from src.backend.api.base import Message
from src.backend.api.openai_client import OpenAIClient
from tests.mock_server import MockServer


@pytest.fixture(scope="module")
def mock_server() -> MockServer:
    """Start mock server."""
    server = MockServer()
    server.start()
    yield server
    server.stop()


class TestTermEntry:
    """Tests for TermEntry."""

    def test_to_dict(self) -> None:
        """Test serialization."""
        entry = TermEntry(
            source="hello", target="你好", category="general"
        )
        d = entry.to_dict()
        assert d["source"] == "hello"
        assert d["target"] == "你好"

    def test_from_dict(self) -> None:
        """Test deserialization."""
        d = {
            "source": "hello",
            "target": "你好",
            "category": "name",
        }
        entry = TermEntry.from_dict(d)
        assert entry.source == "hello"
        assert entry.category == "name"


class TestAgentMemory:
    """Tests for AgentMemory."""

    def test_add_and_get_term(self, tmp_path: Path) -> None:
        """Test adding and retrieving terms."""
        memory = AgentMemory(memory_dir=tmp_path / "mem")
        entry = TermEntry(source="test", target="测试")
        memory.add_term(entry)
        result = memory.get_term("test")
        assert result is not None
        assert result.target == "测试"

    def test_case_insensitive(self, tmp_path: Path) -> None:
        """Test case-insensitive term lookup."""
        memory = AgentMemory(memory_dir=tmp_path / "mem")
        memory.add_term(
            TermEntry(source="Hello", target="你好")
        )
        assert memory.get_term("hello") is not None

    def test_add_summary(self, tmp_path: Path) -> None:
        """Test adding summaries."""
        memory = AgentMemory(memory_dir=tmp_path / "mem")
        memory.add_summary("Summary text", "1-10")
        summaries = memory.get_summaries()
        assert len(summaries) == 1
        assert summaries[0]["summary"] == "Summary text"

    def test_save_and_load(self, tmp_path: Path) -> None:
        """Test persistence."""
        mem_dir = tmp_path / "mem"
        memory = AgentMemory(memory_dir=mem_dir)
        memory.add_term(
            TermEntry(source="test", target="测试")
        )
        memory.add_note("A note")
        memory.save()

        memory2 = AgentMemory(memory_dir=mem_dir)
        assert memory2.get_term("test") is not None
        assert len(memory2.get_notes()) == 1

    def test_clear(self, tmp_path: Path) -> None:
        """Test clearing memory."""
        memory = AgentMemory(memory_dir=tmp_path / "mem")
        memory.add_term(
            TermEntry(source="test", target="测试")
        )
        memory.clear()
        assert len(memory.get_all_terms()) == 0

    def test_bookmarks(self, tmp_path: Path) -> None:
        """Test bookmark functionality."""
        memory = AgentMemory(memory_dir=tmp_path / "mem")
        memory.add_bookmark(42, "Chapter 1")
        bookmarks = memory.get_bookmarks()
        assert len(bookmarks) == 1
        assert bookmarks[0]["position"] == 42

    def test_to_prompt_context(
        self, tmp_path: Path
    ) -> None:
        """Test generating prompt context."""
        memory = AgentMemory(memory_dir=tmp_path / "mem")
        memory.add_term(
            TermEntry(source="test", target="测试")
        )
        ctx = memory.to_prompt_context()
        assert "test" in ctx
        assert "测试" in ctx


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_and_get(self) -> None:
        """Test registering and getting tools."""
        registry = ToolRegistry()
        tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
            handler=lambda: "result",
        )
        registry.register(tool)
        assert registry.get("test_tool") is not None

    def test_execute(self) -> None:
        """Test executing a tool."""
        registry = ToolRegistry()
        tool = Tool(
            name="add",
            description="Add numbers",
            parameters={"type": "object", "properties": {}},
            handler=lambda a, b: a + b,
        )
        registry.register(tool)
        result = registry.execute("add", a=1, b=2)
        assert result == 3

    def test_openai_schema(self) -> None:
        """Test OpenAI schema generation."""
        registry = ToolRegistry()
        tool = Tool(
            name="test",
            description="Test",
            parameters={"type": "object", "properties": {}},
            handler=lambda: None,
        )
        registry.register(tool)
        schemas = registry.get_openai_schemas()
        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"

    def test_execute_unknown(self) -> None:
        """Test executing unknown tool raises error."""
        registry = ToolRegistry()
        with pytest.raises(ValueError):
            registry.execute("unknown")


class TestContextManager:
    """Tests for ContextManager."""

    def test_add_message(self) -> None:
        """Test adding messages."""
        ctx = ContextManager(max_tokens=1000)
        ctx.add_message(
            Message(role="user", content="Hello")
        )
        messages = ctx.get_messages()
        assert len(messages) == 1

    def test_system_prompt(self) -> None:
        """Test system prompt."""
        ctx = ContextManager()
        ctx.set_system_prompt("You are a translator")
        ctx.add_message(
            Message(role="user", content="Hello")
        )
        messages = ctx.get_messages()
        assert len(messages) == 2
        assert messages[0].role == "system"

    def test_needs_summarization(self) -> None:
        """Test summarization trigger."""
        ctx = ContextManager(
            max_tokens=20, summarize_threshold=0.5
        )
        ctx.add_message(
            Message(role="user", content="A" * 100)
        )
        assert ctx.needs_summarization()

    def test_replace_history(self) -> None:
        """Test replacing history with summary."""
        ctx = ContextManager(max_tokens=1000)
        for i in range(5):
            ctx.add_message(
                Message(
                    role="user", content=f"Message {i}"
                )
            )
        ctx.replace_history_with_summary("Summary", keep_last=2)
        messages = ctx.get_messages()
        assert len(messages) == 3
        assert "Summary" in messages[0].content

    def test_max_history(self) -> None:
        """Test max history limit."""
        ctx = ContextManager(max_history_turns=3)
        for i in range(5):
            ctx.add_message(
                Message(
                    role="user", content=f"Message {i}"
                )
            )
        messages = ctx.get_messages()
        assert len(messages) == 3


class TestTranslationAgent:
    """Tests for TranslationAgent."""

    def test_translate(
        self, mock_server: MockServer
    ) -> None:
        """Test basic translation."""
        client = OpenAIClient(
            base_url=mock_server.openai_url,
            model="mock-model",
        )
        agent = TranslationAgent(client=client)
        agent.configure(
            source_lang="ja", target_lang="zh-CN"
        )
        result = agent.translate("こんにちは")
        assert result  # Should get some response

    def test_fast_mode(
        self, mock_server: MockServer
    ) -> None:
        """Test fast mode translation."""
        client = OpenAIClient(
            base_url=mock_server.openai_url,
            model="mock-model",
        )
        agent = TranslationAgent(client=client)
        agent.configure(
            source_lang="ja",
            target_lang="zh-CN",
            fast_mode=True,
        )
        result = agent.translate("Hello")
        assert result

    def test_default_tools(
        self, mock_server: MockServer
    ) -> None:
        """Test default tools are registered."""
        client = OpenAIClient(
            base_url=mock_server.openai_url,
            model="mock-model",
        )
        agent = TranslationAgent(client=client)
        tools = agent.tools.get_all()
        assert len(tools) >= 2
        names = [t.name for t in tools]
        assert "store_term" in names
        assert "add_note" in names

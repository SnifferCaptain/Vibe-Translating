"""Core translation agent implementation."""

import json
from typing import Any, Optional

from ..api.base import BaseAPIClient, ChatResponse, Message
from .context import ContextManager
from .memory import AgentMemory, TermEntry
from .tools import Tool, ToolRegistry


class TranslationAgent:
    """AI-powered translation agent.

    Manages the translation workflow including term extraction,
    context summarization, and tool calling.
    """

    def __init__(
        self,
        client: BaseAPIClient,
        memory: Optional[AgentMemory] = None,
        context: Optional[ContextManager] = None,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        """Initialize the translation agent.

        Args:
            client: API client for LLM communication.
            memory: Agent memory instance.
            context: Context manager instance.
            tool_registry: Tool registry instance.
        """
        self.client = client
        self.memory = memory or AgentMemory()
        self.context = context or ContextManager()
        self.tools = tool_registry or ToolRegistry()
        self._source_lang = "ja"
        self._target_lang = "zh-CN"
        self._fast_mode = False
        self._expert_mode = False
        self._setup_default_tools()

    def configure(
        self,
        source_lang: str = "ja",
        target_lang: str = "zh-CN",
        fast_mode: bool = False,
        expert_mode: bool = False,
        context_window: int = 2048,
        max_history: int = 50,
        summarize_threshold: float = 0.8,
    ) -> None:
        """Configure the agent.

        Args:
            source_lang: Source language code.
            target_lang: Target language code.
            fast_mode: If True, skip tool calls for speed.
            expert_mode: If True, use expert workflow.
            context_window: Context window size.
            max_history: Max history turns.
            summarize_threshold: Summarization threshold.
        """
        self._source_lang = source_lang
        self._target_lang = target_lang
        self._fast_mode = fast_mode
        self._expert_mode = expert_mode
        self.context = ContextManager(
            max_tokens=context_window,
            summarize_threshold=summarize_threshold,
            max_history_turns=max_history,
        )
        self._setup_system_prompt()

    def translate(self, text: str) -> str:
        """Translate text using the agent.

        Args:
            text: Source text to translate.

        Returns:
            Translated text.
        """
        self._check_summarization()
        user_msg = self._build_translation_prompt(text)
        self.context.add_message(
            Message(role="user", content=user_msg)
        )

        tools = None if self._fast_mode else (
            self.tools.get_openai_schemas() or None
        )

        response = self.client.chat(
            messages=self.context.get_messages(),
            tools=tools,
        )

        result = self._process_response(response)

        self.context.add_message(
            Message(role="assistant", content=result)
        )

        return result

    def complete(self, text: str, max_length: int = 50) -> str:
        """Generate tab completion for partial text.

        Args:
            text: Partial text to complete.
            max_length: Maximum completion length.

        Returns:
            Completion suggestion.
        """
        prompt = (
            f"Continue this {self._target_lang} translation "
            f"naturally (max {max_length} chars, output ONLY "
            f"the continuation):\n{text}"
        )
        response = self.client.chat(
            messages=[Message(role="user", content=prompt)],
            max_tokens=max_length,
        )
        return response.content.strip()

    def summarize_context(self) -> str:
        """Trigger context summarization.

        Returns:
            Summary text.
        """
        messages = self.context.get_messages()
        if len(messages) <= 2:
            return ""

        content = "\n".join(
            f"{m.role}: {m.content}" for m in messages[1:]
        )
        summary_prompt = (
            "Summarize the following translation context "
            "concisely, preserving key terms and context:\n\n"
            f"{content}"
        )
        response = self.client.chat(
            messages=[
                Message(role="user", content=summary_prompt)
            ],
        )
        summary = response.content.strip()
        self.memory.add_summary(summary)
        self.context.replace_history_with_summary(summary)
        return summary

    def _setup_system_prompt(self) -> None:
        """Set up the system prompt based on configuration."""
        memory_context = self.memory.to_prompt_context()
        prompt = (
            f"You are an expert translator from "
            f"{self._source_lang} to {self._target_lang}. "
            f"Translate accurately while preserving meaning, "
            f"tone, and style. Output ONLY the translation.\n"
        )
        if self._expert_mode:
            prompt += (
                "Use tools to store important terms. "
                "Provide natural, publication-quality translations.\n"
            )
        if memory_context:
            prompt += f"\n{memory_context}\n"
        self.context.set_system_prompt(prompt)

    def _build_translation_prompt(self, text: str) -> str:
        """Build the translation prompt for given text.

        Args:
            text: Source text.

        Returns:
            Formatted prompt string.
        """
        if self._fast_mode:
            return (
                f"Translate the following {self._source_lang} "
                f"text to {self._target_lang}. Output ONLY the "
                f"translation:\n\n{text}"
            )
        return (
            f"Please translate the following "
            f"{self._source_lang} text to "
            f"{self._target_lang}:\n\n{text}"
        )

    def _process_response(self, response: ChatResponse) -> str:
        """Process agent response, handling tool calls.

        Args:
            response: Chat response from API.

        Returns:
            Final translated text.
        """
        if response.tool_calls and not self._fast_mode:
            for tool_call in response.tool_calls:
                func = tool_call.get("function", {})
                name = func.get("name", "")
                try:
                    args = json.loads(
                        func.get("arguments", "{}")
                    )
                except json.JSONDecodeError:
                    args = {}
                try:
                    self.tools.execute(name, **args)
                except (ValueError, TypeError):
                    pass
        return response.content.strip()

    def _check_summarization(self) -> None:
        """Check and trigger context summarization if needed."""
        if self.context.needs_summarization():
            self.summarize_context()

    def _setup_default_tools(self) -> None:
        """Register default agent tools."""
        self.tools.register(Tool(
            name="store_term",
            description=(
                "Store a terminology pair for consistent "
                "translation"
            ),
            parameters={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source language term",
                    },
                    "target": {
                        "type": "string",
                        "description": "Target language term",
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "name", "technical", "general",
                        ],
                        "description": "Term category",
                    },
                },
                "required": ["source", "target"],
            },
            handler=self._handle_store_term,
        ))
        self.tools.register(Tool(
            name="add_note",
            description="Add a translation note for context",
            parameters={
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string",
                        "description": "Note content",
                    },
                },
                "required": ["note"],
            },
            handler=self._handle_add_note,
        ))

    def _handle_store_term(
        self,
        source: str,
        target: str,
        category: str = "general",
    ) -> str:
        """Handle store_term tool call.

        Args:
            source: Source term.
            target: Target term.
            category: Term category.

        Returns:
            Confirmation message.
        """
        self.memory.add_term(
            TermEntry(
                source=source,
                target=target,
                category=category,
            )
        )
        return f"Stored: {source} → {target}"

    def _handle_add_note(self, note: str) -> str:
        """Handle add_note tool call.

        Args:
            note: Note text.

        Returns:
            Confirmation message.
        """
        self.memory.add_note(note)
        return f"Note added: {note}"

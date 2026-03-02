"""Context management for translation agent."""

from typing import Any, Optional

from ..api.base import Message


class ContextManager:
    """Manages conversation context and history.

    Handles context window limits, automatic summarization triggers,
    and message history for the translation agent.
    """

    def __init__(
        self,
        max_tokens: int = 2048,
        summarize_threshold: float = 0.8,
        max_history_turns: int = 50,
    ) -> None:
        """Initialize context manager.

        Args:
            max_tokens: Maximum context window size in tokens.
            summarize_threshold: Trigger summarization at this
                fraction of max_tokens.
            max_history_turns: Maximum conversation turns to keep.
        """
        self.max_tokens = max_tokens
        self.summarize_threshold = summarize_threshold
        self.max_history_turns = max_history_turns
        self._messages: list[Message] = []
        self._system_prompt: Optional[str] = None
        self._estimated_tokens: int = 0

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt.

        Args:
            prompt: System prompt text.
        """
        self._system_prompt = prompt

    def add_message(self, message: Message) -> None:
        """Add a message to the context.

        Args:
            message: Message to add.
        """
        self._messages.append(message)
        self._estimated_tokens += self._estimate_tokens(
            message.content
        )
        if len(self._messages) > self.max_history_turns:
            removed = self._messages.pop(0)
            self._estimated_tokens -= self._estimate_tokens(
                removed.content
            )

    def get_messages(self) -> list[Message]:
        """Get all messages including system prompt.

        Returns:
            List of messages for API call.
        """
        messages = []
        if self._system_prompt:
            messages.append(
                Message(role="system", content=self._system_prompt)
            )
        messages.extend(self._messages)
        return messages

    def needs_summarization(self) -> bool:
        """Check if context needs summarization.

        Returns:
            True if estimated tokens exceed threshold.
        """
        threshold = int(
            self.max_tokens * self.summarize_threshold
        )
        return self._estimated_tokens >= threshold

    def get_estimated_tokens(self) -> int:
        """Get estimated token count.

        Returns:
            Estimated number of tokens in context.
        """
        return self._estimated_tokens

    def clear(self) -> None:
        """Clear all messages (keeps system prompt)."""
        self._messages.clear()
        self._estimated_tokens = 0

    def replace_history_with_summary(
        self, summary: str, keep_last: int = 2
    ) -> None:
        """Replace old history with a summary message.

        Args:
            summary: Summary of previous conversation.
            keep_last: Number of recent messages to keep.
        """
        recent = self._messages[-keep_last:] if keep_last > 0 else []
        self._messages = [
            Message(
                role="assistant",
                content=f"[Previous context summary]\n{summary}",
            )
        ] + recent
        self._estimated_tokens = sum(
            self._estimate_tokens(m.content)
            for m in self._messages
        )

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate token count for text.

        Uses a simple heuristic of ~4 characters per token.

        Args:
            text: Text to estimate.

        Returns:
            Estimated token count.
        """
        return max(1, len(text) // 4)

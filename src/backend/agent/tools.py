"""Agent tool registry and definitions."""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class Tool:
    """A tool that the agent can call."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format.

        Returns:
            Tool definition in OpenAI schema.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Registry for agent tools."""

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool.

        Args:
            tool: Tool to register.
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """Unregister a tool.

        Args:
            name: Tool name to remove.
        """
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name: Tool name.

        Returns:
            Tool if found, None otherwise.
        """
        return self._tools.get(name)

    def get_all(self) -> list[Tool]:
        """Get all registered tools.

        Returns:
            List of all tools.
        """
        return list(self._tools.values())

    def get_openai_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas in OpenAI format.

        Returns:
            List of tool definitions.
        """
        return [t.to_openai_schema() for t in self._tools.values()]

    def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name.

        Args:
            name: Tool name.
            **kwargs: Tool arguments.

        Returns:
            Tool execution result.

        Raises:
            ValueError: If tool not found.
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return tool.handler(**kwargs)

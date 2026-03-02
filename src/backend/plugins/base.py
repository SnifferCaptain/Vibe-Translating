"""Base plugin interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PluginMeta:
    """Plugin metadata."""

    name: str
    version: str
    description: str
    author: str = ""
    dependencies: list[str] = field(default_factory=list)


class PluginBase(ABC):
    """Abstract base class for plugins.

    All plugins must inherit from this class and implement
    the required methods.
    """

    @abstractmethod
    def get_meta(self) -> PluginMeta:
        """Get plugin metadata.

        Returns:
            Plugin metadata.
        """

    @abstractmethod
    def activate(self, context: dict[str, Any]) -> None:
        """Activate the plugin.

        Args:
            context: Application context with service references.
        """

    @abstractmethod
    def deactivate(self) -> None:
        """Deactivate the plugin."""

    def get_api(self) -> dict[str, Any]:
        """Get plugin's public API.

        Returns functions that the plugin exposes to the frontend
        and other plugins.

        Returns:
            Dictionary of function_name -> callable.
        """
        return {}

    def get_settings_schema(self) -> dict[str, Any]:
        """Get plugin settings schema for GUI rendering.

        Returns:
            JSON-schema-like dictionary describing settings.
        """
        return {}

    def get_default_settings(self) -> dict[str, Any]:
        """Get default settings values.

        Returns:
            Dictionary of default setting values.
        """
        return {}

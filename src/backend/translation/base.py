"""Base translation mode interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModeInfo:
    """Translation mode metadata."""

    name: str
    display_name: str
    description: str
    icon: str = ""
    supported_formats: list[str] = field(default_factory=list)


class TranslationMode(ABC):
    """Abstract base class for translation modes."""

    @abstractmethod
    def get_info(self) -> ModeInfo:
        """Get mode metadata.

        Returns:
            Mode information.
        """

    @abstractmethod
    def process(
        self, content: Any, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Process content for translation.

        Args:
            content: Input content (text, file path, etc.).
            options: Processing options.

        Returns:
            Processing result with translated content.
        """

    def get_options_schema(self) -> dict[str, Any]:
        """Get options schema for GUI rendering.

        Returns:
            JSON-schema-like dictionary.
        """
        return {}

    def get_default_options(self) -> dict[str, Any]:
        """Get default options.

        Returns:
            Default option values.
        """
        return {}

    def supports_format(self, fmt: str) -> bool:
        """Check if this mode supports a file format.

        Args:
            fmt: File format extension.

        Returns:
            True if format is supported.
        """
        info = self.get_info()
        return fmt.lower() in info.supported_formats


class ModeRegistry:
    """Registry for translation modes."""

    def __init__(self) -> None:
        """Initialize the mode registry."""
        self._modes: dict[str, TranslationMode] = {}

    def register(self, mode: TranslationMode) -> None:
        """Register a translation mode.

        Args:
            mode: Mode instance to register.
        """
        info = mode.get_info()
        self._modes[info.name] = mode

    def unregister(self, name: str) -> None:
        """Unregister a translation mode.

        Args:
            name: Mode name to remove.
        """
        self._modes.pop(name, None)

    def get(self, name: str) -> Optional[TranslationMode]:
        """Get a mode by name.

        Args:
            name: Mode name.

        Returns:
            Mode instance or None.
        """
        return self._modes.get(name)

    def get_all(self) -> dict[str, ModeInfo]:
        """Get info for all registered modes.

        Returns:
            Dictionary of mode name to info.
        """
        return {
            name: mode.get_info()
            for name, mode in self._modes.items()
        }

    def get_names(self) -> list[str]:
        """Get all registered mode names.

        Returns:
            List of mode names.
        """
        return list(self._modes.keys())

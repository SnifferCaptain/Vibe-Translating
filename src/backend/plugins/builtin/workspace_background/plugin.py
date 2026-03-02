"""Workspace background plugin.

Allows users to set a custom background image for
the workspace area in GUI frontends.
"""

from pathlib import Path
from typing import Any

from ...base import PluginBase, PluginMeta


class WorkspaceBackgroundPlugin(PluginBase):
    """Plugin for customizing workspace background."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        self._enabled = False
        self._image_path = ""
        self._opacity = 0.1
        self._color = "#ffffff"

    def get_meta(self) -> PluginMeta:
        """Get plugin metadata."""
        return PluginMeta(
            name="workspace_background",
            version="1.0.0",
            description="Customize workspace background image and color",
            author="Vibe Translating Team",
        )

    def activate(self, context: dict[str, Any]) -> None:
        """Activate the plugin."""
        config = context.get("config")
        if config:
            self._enabled = config.get(
                "workspace.background.enabled", False
            )
            self._image_path = config.get(
                "workspace.background.image_path", ""
            )
            self._opacity = config.get(
                "workspace.background.opacity", 0.1
            )
        self._enabled = True

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self._enabled = False

    def get_api(self) -> dict[str, Any]:
        """Get plugin API."""
        return {
            "set_background": self.set_background,
            "get_background": self.get_background,
            "set_opacity": self.set_opacity,
            "set_color": self.set_color,
        }

    def get_settings_schema(self) -> dict[str, Any]:
        """Get settings schema for GUI."""
        return {
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "title": "Enable Background",
                    "default": False,
                },
                "image_path": {
                    "type": "string",
                    "title": "Background Image Path",
                    "default": "",
                },
                "opacity": {
                    "type": "number",
                    "title": "Background Opacity",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.1,
                },
                "color": {
                    "type": "string",
                    "title": "Background Color",
                    "default": "#ffffff",
                },
            },
        }

    def get_default_settings(self) -> dict[str, Any]:
        """Get default settings."""
        return {
            "enabled": False,
            "image_path": "",
            "opacity": 0.1,
            "color": "#ffffff",
        }

    def set_background(self, image_path: str) -> dict[str, Any]:
        """Set background image path.

        Args:
            image_path: Path to background image.

        Returns:
            Status response.
        """
        if image_path and not Path(image_path).exists():
            return {
                "success": False,
                "error": "Image file not found",
            }
        self._image_path = image_path
        return {
            "success": True,
            "image_path": self._image_path,
        }

    def get_background(self) -> dict[str, Any]:
        """Get current background settings.

        Returns:
            Current background configuration.
        """
        return {
            "enabled": self._enabled,
            "image_path": self._image_path,
            "opacity": self._opacity,
            "color": self._color,
        }

    def set_opacity(self, opacity: float) -> dict[str, Any]:
        """Set background opacity.

        Args:
            opacity: Opacity value (0.0 to 1.0).

        Returns:
            Status response.
        """
        self._opacity = max(0.0, min(1.0, opacity))
        return {"success": True, "opacity": self._opacity}

    def set_color(self, color: str) -> dict[str, Any]:
        """Set background color.

        Args:
            color: CSS color string.

        Returns:
            Status response.
        """
        self._color = color
        return {"success": True, "color": self._color}

"""Tests for plugin system."""

import sys
from pathlib import Path

import pytest

from src.backend.plugins.base import PluginBase, PluginMeta
from src.backend.plugins.manager import PluginManager


def _make_manager() -> PluginManager:
    """Create a PluginManager with sys.modules aliases.

    The builtin plugin loader imports PluginBase via the
    ``backend.plugins.base`` path while the test suite uses
    ``src.backend.plugins.base``.  Aliasing the modules lets
    ``issubclass`` succeed across both import paths.
    """
    for key, mod in list(sys.modules.items()):
        if key.startswith("src.backend"):
            alias = key[len("src."):]
            sys.modules.setdefault(alias, mod)
    return PluginManager()


class TestPluginBase:
    """Tests for plugin base class."""

    def test_default_api(self) -> None:
        """Test default API returns empty dict."""

        class TestPlugin(PluginBase):
            def get_meta(self) -> PluginMeta:
                return PluginMeta(
                    name="test", version="1.0", description="Test"
                )

            def activate(self, context: dict) -> None:
                pass

            def deactivate(self) -> None:
                pass

        plugin = TestPlugin()
        assert plugin.get_api() == {}
        assert plugin.get_settings_schema() == {}


class TestPluginManager:
    """Tests for PluginManager."""

    def test_load_builtin(self) -> None:
        """Test loading built-in plugins."""
        manager = _make_manager()
        loaded = manager.load_builtin_plugins()
        assert "workspace_background" in loaded

    def test_activate_deactivate(self) -> None:
        """Test plugin activation and deactivation."""
        manager = _make_manager()
        manager.load_builtin_plugins()
        assert manager.activate_plugin("workspace_background")
        assert "workspace_background" in manager.get_active_plugins()
        assert manager.deactivate_plugin("workspace_background")
        assert "workspace_background" not in manager.get_active_plugins()

    def test_get_plugin_api(self) -> None:
        """Test getting plugin API."""
        manager = _make_manager()
        manager.set_context({})
        manager.load_builtin_plugins()
        manager.activate_plugin("workspace_background")
        api = manager.get_plugin_api("workspace_background")
        assert "set_background" in api
        assert "get_background" in api
        assert "set_opacity" in api

    def test_plugin_functions(self) -> None:
        """Test calling plugin functions."""
        manager = _make_manager()
        manager.set_context({})
        manager.load_builtin_plugins()
        manager.activate_plugin("workspace_background")
        api = manager.get_plugin_api("workspace_background")

        result = api["set_opacity"](0.5)
        assert result["success"]
        assert result["opacity"] == 0.5

        bg = api["get_background"]()
        assert bg["opacity"] == 0.5

    def test_get_all_plugins(self) -> None:
        """Test getting all plugin metadata."""
        manager = _make_manager()
        manager.load_builtin_plugins()
        all_plugins = manager.get_all_plugins()
        assert "workspace_background" in all_plugins
        meta = all_plugins["workspace_background"]
        assert meta.version == "1.0.0"

    def test_load_external_nonexistent(self) -> None:
        """Test loading from nonexistent directory."""
        manager = PluginManager()
        loaded = manager.load_external_plugins(
            Path("/nonexistent")
        )
        assert loaded == []

    def test_activate_nonexistent(self) -> None:
        """Test activating nonexistent plugin."""
        manager = PluginManager()
        assert not manager.activate_plugin("nonexistent")

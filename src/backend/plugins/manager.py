"""Plugin manager for loading and managing plugins."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Optional

from .base import PluginBase, PluginMeta


class PluginManager:
    """Manages plugin lifecycle and discovery.

    Loads plugins from the builtin directory and external
    plugin directories.
    """

    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self._plugins: dict[str, PluginBase] = {}
        self._active: set[str] = set()
        self._context: dict[str, Any] = {}

    def set_context(self, context: dict[str, Any]) -> None:
        """Set the application context for plugins.

        Args:
            context: Application context with service references.
        """
        self._context = context

    def load_builtin_plugins(self) -> list[str]:
        """Load all built-in plugins.

        Returns:
            List of loaded plugin names.
        """
        builtin_dir = Path(__file__).parent / "builtin"
        return self._load_from_directory(builtin_dir)

    def load_external_plugins(
        self, directory: Path
    ) -> list[str]:
        """Load plugins from an external directory.

        Args:
            directory: Path to plugins directory.

        Returns:
            List of loaded plugin names.
        """
        if not directory.exists():
            return []
        return self._load_from_directory(directory)

    def activate_plugin(self, name: str) -> bool:
        """Activate a loaded plugin.

        Args:
            name: Plugin name.

        Returns:
            True if activation succeeded.
        """
        plugin = self._plugins.get(name)
        if not plugin:
            return False
        if name in self._active:
            return True
        try:
            plugin.activate(self._context)
            self._active.add(name)
            return True
        except Exception:
            return False

    def deactivate_plugin(self, name: str) -> bool:
        """Deactivate an active plugin.

        Args:
            name: Plugin name.

        Returns:
            True if deactivation succeeded.
        """
        plugin = self._plugins.get(name)
        if not plugin or name not in self._active:
            return False
        try:
            plugin.deactivate()
            self._active.discard(name)
            return True
        except Exception:
            return False

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a plugin by name.

        Args:
            name: Plugin name.

        Returns:
            Plugin instance or None.
        """
        return self._plugins.get(name)

    def get_active_plugins(self) -> list[str]:
        """Get names of active plugins.

        Returns:
            List of active plugin names.
        """
        return list(self._active)

    def get_all_plugins(self) -> dict[str, PluginMeta]:
        """Get metadata for all loaded plugins.

        Returns:
            Dictionary of plugin name to metadata.
        """
        return {
            name: plugin.get_meta()
            for name, plugin in self._plugins.items()
        }

    def get_plugin_api(
        self, name: str
    ) -> dict[str, Any]:
        """Get a plugin's public API.

        Args:
            name: Plugin name.

        Returns:
            Dictionary of exposed functions.
        """
        plugin = self._plugins.get(name)
        if not plugin or name not in self._active:
            return {}
        return plugin.get_api()

    def _load_from_directory(
        self, directory: Path
    ) -> list[str]:
        """Load plugins from a directory.

        Each subdirectory with a plugin.py file is treated
        as a plugin.

        Args:
            directory: Directory to scan.

        Returns:
            List of loaded plugin names.
        """
        loaded = []
        if not directory.exists():
            return loaded
        for item in sorted(directory.iterdir()):
            if not item.is_dir():
                continue
            if item.name.startswith("_"):
                continue
            plugin_file = item / "plugin.py"
            if not plugin_file.exists():
                continue
            try:
                plugin = self._load_plugin_file(plugin_file)
                if plugin:
                    meta = plugin.get_meta()
                    self._plugins[meta.name] = plugin
                    loaded.append(meta.name)
            except Exception:
                continue
        return loaded

    def _ensure_parent_packages(self) -> None:
        """Ensure backend and backend.plugins packages are in sys.modules."""
        if "backend" not in sys.modules:
            importlib.import_module("backend")
        if "backend.plugins" not in sys.modules:
            importlib.import_module("backend.plugins")

    def _load_plugin_file(
        self, path: Path
    ) -> Optional[PluginBase]:
        """Load a plugin from a Python file.

        Args:
            path: Path to plugin.py file.

        Returns:
            Plugin instance or None.
        """
        # Ensure the src directory is importable so that
        # plugins can use relative imports within the package.
        src_dir = str(Path(__file__).resolve().parents[2])
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        # Register parent packages so relative imports work.
        self._ensure_parent_packages()

        # Build a fully-qualified module name that preserves
        # the package hierarchy for relative imports.
        plugins_root = Path(__file__).resolve().parent
        rel = path.resolve().relative_to(plugins_root)
        parts = list(rel.with_suffix("").parts)
        module_name = (
            "backend.plugins." + ".".join(parts)
        )

        # Register intermediate sub-packages.
        for i in range(len(parts) - 1):
            pkg_name = "backend.plugins." + ".".join(
                parts[: i + 1]
            )
            if pkg_name not in sys.modules:
                pkg_path = plugins_root / Path(
                    *parts[: i + 1]
                )
                pkg_spec = importlib.util.spec_from_file_location(
                    pkg_name,
                    pkg_path / "__init__.py",
                    submodule_search_locations=[
                        str(pkg_path)
                    ],
                )
                if pkg_spec and pkg_spec.loader:
                    pkg_mod = importlib.util.module_from_spec(
                        pkg_spec
                    )
                    sys.modules[pkg_name] = pkg_mod
                    pkg_spec.loader.exec_module(pkg_mod)

        spec = importlib.util.spec_from_file_location(
            module_name, path,
        )
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginBase)
                and attr is not PluginBase
            ):
                return attr()
        return None

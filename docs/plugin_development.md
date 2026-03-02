# Vibe Translating - Plugin Development Guide

## Overview

Plugins extend Vibe Translating's functionality by registering new tools, modes, and UI elements. Plugins interact with the backend through a well-defined API.

## Creating a Plugin

### Directory Structure

```
plugins/
└── my_plugin/
    ├── __init__.py    # (can be empty)
    └── plugin.py      # Main plugin file
```

### Plugin Template

```python
"""My custom plugin."""

from typing import Any
from src.backend.plugins.base import PluginBase, PluginMeta


class MyPlugin(PluginBase):
    """A custom plugin example."""

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
        )

    def activate(self, context: dict[str, Any]) -> None:
        """Called when plugin is activated.

        Args:
            context: Contains 'config' (ConfigManager)
                and 'mode_registry' (ModeRegistry).
        """
        self.config = context.get("config")

    def deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass

    def get_api(self) -> dict[str, Any]:
        """Expose functions to frontends.

        Returns:
            Dict mapping function names to callables.
        """
        return {
            "my_function": self.my_function,
        }

    def get_settings_schema(self) -> dict[str, Any]:
        """Define settings for GUI rendering."""
        return {
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "title": "Enable",
                    "default": True,
                },
            },
        }

    def get_default_settings(self) -> dict[str, Any]:
        return {"enabled": True}

    def my_function(self, param: str) -> dict[str, Any]:
        return {"result": f"Processed: {param}"}
```

### Plugin Lifecycle

1. **Discovery**: Plugin manager scans directories for `plugin.py` files
2. **Loading**: Plugin class is instantiated (subclass of `PluginBase`)
3. **Activation**: `activate(context)` is called with app context
4. **API Access**: `get_api()` exposes functions to frontends
5. **Deactivation**: `deactivate()` cleans up resources

### Calling Plugin Functions from Frontends

```python
# From any frontend
response = service.handle_request(
    Request(
        method="call_plugin",
        params={
            "plugin": "my_plugin",
            "function": "my_function",
            "args": {"param": "hello"},
        },
    )
)
```

### WebUI API Call
```javascript
const resp = await fetch('/api/call', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        method: 'call_plugin',
        params: {
            plugin: 'my_plugin',
            function: 'my_function',
            args: {param: 'hello'},
        },
    }),
});
```

## Built-in Plugin: Workspace Background

The `workspace_background` plugin demonstrates the plugin system:

- **Location**: `src/backend/plugins/builtin/workspace_background/`
- **Functions**: `set_background`, `get_background`, `set_opacity`, `set_color`
- **Settings**: Background image, opacity, color

## Best Practices

1. Always return structured data (dicts) from plugin functions
2. Use `get_settings_schema()` for GUI-renderable settings
3. Handle errors gracefully, never crash the host application
4. Keep plugins lightweight - avoid heavy dependencies
5. Use the `context` dict to access shared services

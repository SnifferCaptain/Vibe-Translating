"""Backend service layer.

Central service that exposes all backend functionality
to frontends via the ServiceProtocol.
"""

from pathlib import Path
from typing import Any, Optional

from .agent.core import TranslationAgent
from .agent.memory import AgentMemory, TermEntry
from .api.factory import create_client
from .config.manager import ConfigManager
from .plugins.manager import PluginManager
from .translation.base import ModeRegistry
from .translation.book import BookMode
from .translation.frame_select import FrameSelectMode
from .translation.realtime import RealtimeMode
from .translation.supervision import SupervisionMode
from ..frontend.common.protocol import (
    Request,
    Response,
    ServiceProtocol,
)


class BackendService:
    """Main backend service.

    Orchestrates all backend components and exposes
    them to frontends via structured protocol.
    """

    def __init__(
        self, config: Optional[ConfigManager] = None
    ) -> None:
        """Initialize the backend service.

        Args:
            config: Configuration manager instance.
        """
        self.config = config or ConfigManager()
        self.protocol = ServiceProtocol()
        self.plugin_manager = PluginManager()
        self.mode_registry = ModeRegistry()
        self._agent: Optional[TranslationAgent] = None
        self._memory: Optional[AgentMemory] = None
        self._setup()

    def _setup(self) -> None:
        """Set up all backend components."""
        self._register_modes()
        self._setup_plugins()
        self._register_methods()

    def _register_modes(self) -> None:
        """Register built-in translation modes."""
        self.mode_registry.register(RealtimeMode())
        self.mode_registry.register(BookMode())
        self.mode_registry.register(FrameSelectMode())
        self.mode_registry.register(SupervisionMode())

    def _setup_plugins(self) -> None:
        """Load and activate plugins."""
        self.plugin_manager.set_context({
            "config": self.config,
            "mode_registry": self.mode_registry,
        })
        self.plugin_manager.load_builtin_plugins()

        active = self.config.get("plugins.active", [])
        if isinstance(active, list):
            for name in active:
                self.plugin_manager.activate_plugin(name)

        ext_dir = self.config.get("plugins.directory", "plugins")
        if ext_dir:
            self.plugin_manager.load_external_plugins(
                Path(ext_dir)
            )

    def _register_methods(self) -> None:
        """Register all backend methods for frontend access."""
        self.protocol.register(
            "get_config",
            self._get_config,
            "Get configuration value",
        )
        self.protocol.register(
            "set_config",
            self._set_config,
            "Set configuration value",
        )
        self.protocol.register(
            "save_config",
            self._save_config,
            "Save configuration to file",
        )
        self.protocol.register(
            "get_all_config",
            self._get_all_config,
            "Get all configuration",
        )
        self.protocol.register(
            "get_modes",
            self._get_modes,
            "Get available translation modes",
        )
        self.protocol.register(
            "get_mode_options",
            self._get_mode_options,
            "Get mode options schema",
        )
        self.protocol.register(
            "translate",
            self._translate,
            "Translate text",
        )
        self.protocol.register(
            "complete",
            self._complete,
            "Tab completion for translation",
        )
        self.protocol.register(
            "process_content",
            self._process_content,
            "Process content with a translation mode",
        )
        self.protocol.register(
            "get_memory",
            self._get_memory,
            "Get agent memory data",
        )
        self.protocol.register(
            "add_term",
            self._add_term,
            "Add terminology entry",
        )
        self.protocol.register(
            "get_terms",
            self._get_terms,
            "Get all terminology entries",
        )
        self.protocol.register(
            "get_plugins",
            self._get_plugins,
            "Get plugin information",
        )
        self.protocol.register(
            "activate_plugin",
            self._activate_plugin,
            "Activate a plugin",
        )
        self.protocol.register(
            "deactivate_plugin",
            self._deactivate_plugin,
            "Deactivate a plugin",
        )
        self.protocol.register(
            "call_plugin",
            self._call_plugin,
            "Call a plugin function",
        )
        self.protocol.register(
            "get_methods",
            self._get_methods,
            "Get all available methods",
        )
        self.protocol.register(
            "check_api",
            self._check_api,
            "Check API availability",
        )
        self.protocol.register(
            "get_bookmarks",
            self._get_bookmarks,
            "Get all bookmarks",
        )
        self.protocol.register(
            "add_bookmark",
            self._add_bookmark,
            "Add a bookmark",
        )
        self.protocol.register(
            "save_memory",
            self._save_memory,
            "Save agent memory to disk",
        )

    def handle_request(self, request: Request) -> Response:
        """Handle a frontend request.

        Args:
            request: Frontend request.

        Returns:
            Backend response.
        """
        return self.protocol.handle(request)

    def get_or_create_agent(self) -> TranslationAgent:
        """Get or create the translation agent.

        Returns:
            Translation agent instance.
        """
        if self._agent is None:
            provider = self.config.get("api.provider", "openai")
            provider_config = self.config.get_section(
                f"api.{provider}"
            )
            client = create_client(provider, **provider_config)
            self._memory = AgentMemory()
            self._agent = TranslationAgent(
                client=client, memory=self._memory
            )
            self._agent.configure(
                source_lang=self.config.get(
                    "translation.source_language", "ja"
                ),
                target_lang=self.config.get(
                    "translation.target_language", "zh-CN"
                ),
                fast_mode=self.config.get(
                    "translation.fast_mode", False
                ),
                expert_mode=self.config.get(
                    "agent.expert_mode", False
                ),
                context_window=self.config.get(
                    "translation.context_window", 2048
                ),
                max_history=self.config.get(
                    "agent.max_history_turns", 50
                ),
                summarize_threshold=self.config.get(
                    "agent.summarize_threshold", 0.8
                ),
            )
        return self._agent

    def _get_config(self, key: str) -> Any:
        return self.config.get(key)

    def _set_config(self, key: str, value: Any) -> dict[str, Any]:
        self.config.set(key, value)
        return {"key": key, "value": value}

    def _save_config(self) -> dict[str, bool]:
        self.config.save()
        return {"saved": True}

    def _get_all_config(self) -> dict[str, Any]:
        return self.config.get_all()

    def _get_modes(self) -> dict[str, Any]:
        modes = self.mode_registry.get_all()
        return {
            name: {
                "display_name": info.display_name,
                "description": info.description,
                "icon": info.icon,
                "supported_formats": info.supported_formats,
            }
            for name, info in modes.items()
        }

    def _get_mode_options(
        self, mode: str
    ) -> dict[str, Any]:
        m = self.mode_registry.get(mode)
        if not m:
            return {"error": f"Mode not found: {mode}"}
        return {
            "schema": m.get_options_schema(),
            "defaults": m.get_default_options(),
        }

    def _translate(self, text: str) -> dict[str, str]:
        agent = self.get_or_create_agent()
        result = agent.translate(text)
        return {"source": text, "translation": result}

    def _complete(
        self, text: str, max_length: int = 50
    ) -> dict[str, str]:
        agent = self.get_or_create_agent()
        result = agent.complete(text, max_length)
        return {"completion": result}

    def _process_content(
        self,
        mode: str,
        content: Any,
        options: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        m = self.mode_registry.get(mode)
        if not m:
            return {"error": f"Mode not found: {mode}"}
        return m.process(content, options or {})

    def _get_memory(self) -> dict[str, Any]:
        if not self._memory:
            return {"terms": [], "summaries": [], "notes": []}
        return {
            "terms": [
                t.to_dict() for t in self._memory.get_all_terms()
            ],
            "summaries": self._memory.get_summaries(),
            "notes": self._memory.get_notes(),
            "bookmarks": self._memory.get_bookmarks(),
        }

    def _add_term(
        self,
        source: str,
        target: str,
        category: str = "general",
    ) -> dict[str, str]:
        if not self._memory:
            self._memory = AgentMemory()
        self._memory.add_term(
            TermEntry(
                source=source,
                target=target,
                category=category,
            )
        )
        return {"source": source, "target": target}

    def _get_terms(self) -> list[dict[str, Any]]:
        if not self._memory:
            return []
        return [t.to_dict() for t in self._memory.get_all_terms()]

    def _get_plugins(self) -> dict[str, Any]:
        all_plugins = self.plugin_manager.get_all_plugins()
        active = self.plugin_manager.get_active_plugins()
        return {
            name: {
                "version": meta.version,
                "description": meta.description,
                "author": meta.author,
                "active": name in active,
            }
            for name, meta in all_plugins.items()
        }

    def _activate_plugin(
        self, name: str
    ) -> dict[str, bool]:
        ok = self.plugin_manager.activate_plugin(name)
        return {"activated": ok}

    def _deactivate_plugin(
        self, name: str
    ) -> dict[str, bool]:
        ok = self.plugin_manager.deactivate_plugin(name)
        return {"deactivated": ok}

    def _call_plugin(
        self,
        plugin: str,
        function: str,
        args: Optional[dict[str, Any]] = None,
    ) -> Any:
        api = self.plugin_manager.get_plugin_api(plugin)
        if not api:
            return {"error": f"Plugin not available: {plugin}"}
        func = api.get(function)
        if not func:
            return {"error": f"Function not found: {function}"}
        return func(**(args or {}))

    def _get_methods(self) -> list[dict[str, str]]:
        return self.protocol.get_methods()

    def _check_api(self) -> dict[str, Any]:
        provider = self.config.get("api.provider", "openai")
        provider_config = self.config.get_section(
            f"api.{provider}"
        )
        try:
            client = create_client(provider, **provider_config)
            available = client.is_available()
        except Exception:
            available = False
        return {
            "provider": provider,
            "available": available,
        }

    def _get_bookmarks(self) -> list[dict[str, Any]]:
        if not self._memory:
            return []
        return self._memory.get_bookmarks()

    def _add_bookmark(
        self,
        position: int,
        label: str = "",
        note: str = "",
    ) -> dict[str, Any]:
        if not self._memory:
            self._memory = AgentMemory()
        self._memory.add_bookmark(position, label, note)
        return {
            "position": position,
            "label": label,
            "note": note,
        }

    def _save_memory(self) -> dict[str, bool]:
        if self._memory:
            self._memory.save()
        return {"saved": True}

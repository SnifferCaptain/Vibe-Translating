"""Configuration manager for Vibe Translating.

Handles loading, saving, and accessing YAML-based configuration.
All parameters are stored in YAML files and can be accessed
via dot-notation paths.
"""

import copy
from pathlib import Path
from typing import Any, Optional

import yaml


_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "default.yaml"
_USER_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "user_config.yaml"


class ConfigManager:
    """Manages application configuration with YAML backend.

    Supports dot-notation access (e.g., 'api.openai.model'),
    default values, and user overrides.
    """

    def __init__(
        self,
        default_path: Optional[Path] = None,
        user_path: Optional[Path] = None,
    ) -> None:
        """Initialize the config manager.

        Args:
            default_path: Path to default config YAML file.
            user_path: Path to user config YAML file.
        """
        self._default_path = default_path or _DEFAULT_CONFIG_PATH
        self._user_path = user_path or _USER_CONFIG_PATH
        self._config: dict[str, Any] = {}
        self._defaults: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from default and user YAML files."""
        self._defaults = self._load_yaml(self._default_path)
        self._config = copy.deepcopy(self._defaults)
        if self._user_path.exists():
            user_config = self._load_yaml(self._user_path)
            self._deep_merge(self._config, user_config)

    def save(self, path: Optional[Path] = None) -> None:
        """Save current configuration to user YAML file.

        Args:
            path: Optional path to save to. Defaults to user config path.
        """
        save_path = path or self._user_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            yaml.dump(
                self._config,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'api.openai.model').
            default: Default value if key not found.

        Returns:
            The config value or default.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'api.openai.model').
            value: Value to set.
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_all(self) -> dict[str, Any]:
        """Get the complete configuration dictionary.

        Returns:
            Deep copy of the full configuration.
        """
        return copy.deepcopy(self._config)

    def get_section(self, section: str) -> dict[str, Any]:
        """Get a configuration section.

        Args:
            section: Top-level section name.

        Returns:
            Deep copy of the section dictionary.
        """
        value = self.get(section, {})
        if isinstance(value, dict):
            return copy.deepcopy(value)
        return {}

    def reset(self, key: Optional[str] = None) -> None:
        """Reset configuration to defaults.

        Args:
            key: Optional dot-notation key to reset. If None, resets all.
        """
        if key is None:
            self._config = copy.deepcopy(self._defaults)
        else:
            default_value = self._defaults
            keys = key.split(".")
            for k in keys:
                if isinstance(default_value, dict) and k in default_value:
                    default_value = default_value[k]
                else:
                    return
            self.set(key, copy.deepcopy(default_value))

    def get_flat(self) -> dict[str, Any]:
        """Get all config values as flat dot-notation keys.

        Returns:
            Dictionary with dot-notation keys and their values.
        """
        result: dict[str, Any] = {}
        self._flatten(self._config, "", result)
        return result

    def _flatten(
        self, data: dict[str, Any], prefix: str, result: dict[str, Any]
    ) -> None:
        """Recursively flatten a nested dictionary.

        Args:
            data: Dictionary to flatten.
            prefix: Current key prefix.
            result: Output dictionary.
        """
        for key, value in data.items():
            full_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
            if isinstance(value, dict):
                self._flatten(value, full_key, result)
            else:
                result[full_key] = value

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        """Load a YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            Parsed YAML data as dictionary.
        """
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
        """Deep merge override into base dictionary.

        Args:
            base: Base dictionary (modified in place).
            override: Override dictionary.
        """
        for key, value in override.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value

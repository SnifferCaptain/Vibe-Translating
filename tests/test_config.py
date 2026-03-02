"""Tests for configuration manager."""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.backend.config.manager import ConfigManager


@pytest.fixture
def config_dir(tmp_path: Path) -> tuple[Path, Path]:
    """Create temp config directory with default config."""
    default_path = tmp_path / "default.yaml"
    user_path = tmp_path / "user_config.yaml"
    default_config = {
        "app": {"name": "Test App", "version": "0.1.0"},
        "api": {
            "provider": "openai",
            "openai": {"model": "gpt-4o-mini", "api_key": ""},
        },
        "translation": {
            "source_language": "ja",
            "target_language": "zh-CN",
        },
    }
    with open(default_path, "w") as f:
        yaml.dump(default_config, f)
    return default_path, user_path


@pytest.fixture
def config(config_dir: tuple[Path, Path]) -> ConfigManager:
    """Create a ConfigManager instance."""
    default_path, user_path = config_dir
    return ConfigManager(
        default_path=default_path, user_path=user_path
    )


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_load_defaults(
        self, config: ConfigManager
    ) -> None:
        """Test loading default configuration."""
        assert config.get("app.name") == "Test App"
        assert config.get("app.version") == "0.1.0"

    def test_get_dot_notation(
        self, config: ConfigManager
    ) -> None:
        """Test dot-notation access."""
        assert config.get("api.provider") == "openai"
        assert config.get("api.openai.model") == "gpt-4o-mini"

    def test_get_default_value(
        self, config: ConfigManager
    ) -> None:
        """Test default value for missing key."""
        assert config.get("nonexistent", "default") == "default"

    def test_set_value(
        self, config: ConfigManager
    ) -> None:
        """Test setting configuration value."""
        config.set("api.provider", "ollama")
        assert config.get("api.provider") == "ollama"

    def test_set_nested_value(
        self, config: ConfigManager
    ) -> None:
        """Test setting nested value."""
        config.set("new.nested.key", "value")
        assert config.get("new.nested.key") == "value"

    def test_save_and_load(
        self, config_dir: tuple[Path, Path]
    ) -> None:
        """Test saving and reloading config."""
        default_path, user_path = config_dir
        config = ConfigManager(
            default_path=default_path, user_path=user_path
        )
        config.set("api.provider", "ollama")
        config.save()

        config2 = ConfigManager(
            default_path=default_path, user_path=user_path
        )
        assert config2.get("api.provider") == "ollama"

    def test_get_section(
        self, config: ConfigManager
    ) -> None:
        """Test getting a config section."""
        section = config.get_section("api")
        assert isinstance(section, dict)
        assert "provider" in section

    def test_reset(
        self, config: ConfigManager
    ) -> None:
        """Test resetting config to defaults."""
        config.set("api.provider", "ollama")
        config.reset("api.provider")
        assert config.get("api.provider") == "openai"

    def test_reset_all(
        self, config: ConfigManager
    ) -> None:
        """Test resetting all config."""
        config.set("api.provider", "ollama")
        config.reset()
        assert config.get("api.provider") == "openai"

    def test_get_flat(
        self, config: ConfigManager
    ) -> None:
        """Test getting flat config."""
        flat = config.get_flat()
        assert "app.name" in flat
        assert "api.provider" in flat

    def test_get_all(
        self, config: ConfigManager
    ) -> None:
        """Test getting complete config."""
        all_config = config.get_all()
        assert "app" in all_config
        assert "api" in all_config

    def test_user_override(
        self, config_dir: tuple[Path, Path]
    ) -> None:
        """Test user config overrides defaults."""
        default_path, user_path = config_dir
        user_config = {"api": {"provider": "ollama"}}
        with open(user_path, "w") as f:
            yaml.dump(user_config, f)

        config = ConfigManager(
            default_path=default_path, user_path=user_path
        )
        assert config.get("api.provider") == "ollama"
        assert config.get("app.name") == "Test App"

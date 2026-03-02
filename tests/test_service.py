"""Tests for backend service."""

import sys
from pathlib import Path

import pytest
import yaml

from src.backend.service import BackendService
from src.backend.config.manager import ConfigManager
from src.frontend.common.protocol import Request, Response
from tests.mock_server import MockServer


def _alias_src_modules() -> None:
    """Alias ``src.backend.*`` modules as ``backend.*``.

    This works around the plugin loader importing
    ``PluginBase`` via ``backend.plugins.base`` while
    the test suite uses the ``src.backend`` prefix.
    """
    for key, mod in list(sys.modules.items()):
        if key.startswith("src.backend"):
            alias = key[len("src."):]
            sys.modules.setdefault(alias, mod)


@pytest.fixture(scope="module")
def mock_server() -> MockServer:
    """Start mock server."""
    server = MockServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def service(
    tmp_path: Path, mock_server: MockServer
) -> BackendService:
    """Create a test BackendService."""
    _alias_src_modules()
    default_path = tmp_path / "default.yaml"
    user_path = tmp_path / "user_config.yaml"
    config_data = {
        "app": {"name": "Test", "version": "0.1.0"},
        "api": {
            "provider": "openai",
            "openai": {
                "base_url": mock_server.openai_url,
                "model": "mock-model",
                "api_key": "",
                "max_tokens": 100,
                "temperature": 0.3,
            },
        },
        "translation": {
            "source_language": "ja",
            "target_language": "zh-CN",
            "mode": "realtime",
            "fast_mode": False,
            "context_window": 2048,
        },
        "agent": {
            "expert_mode": False,
            "max_history_turns": 50,
            "summarize_threshold": 0.8,
        },
        "plugins": {
            "enabled": True,
            "directory": "plugins",
            "active": ["workspace_background"],
        },
    }
    with open(default_path, "w") as f:
        yaml.dump(config_data, f)
    config = ConfigManager(
        default_path=default_path, user_path=user_path
    )
    return BackendService(config=config)


class TestProtocol:
    """Tests for Request/Response protocol."""

    def test_request_to_dict(self) -> None:
        """Test request serialization."""
        req = Request(
            method="test", params={"key": "value"}
        )
        d = req.to_dict()
        assert d["method"] == "test"
        assert d["params"]["key"] == "value"

    def test_request_from_dict(self) -> None:
        """Test request deserialization."""
        d = {"method": "test", "params": {"key": "value"}}
        req = Request.from_dict(d)
        assert req.method == "test"

    def test_response_to_dict(self) -> None:
        """Test response serialization."""
        resp = Response(success=True, data={"result": 42})
        d = resp.to_dict()
        assert d["success"]
        assert d["data"]["result"] == 42


class TestBackendService:
    """Tests for BackendService."""

    def test_get_modes(
        self, service: BackendService
    ) -> None:
        """Test getting available modes."""
        resp = service.handle_request(
            Request(method="get_modes")
        )
        assert resp.success
        assert "realtime" in resp.data
        assert "book" in resp.data
        assert "frame_select" in resp.data
        assert "supervision" in resp.data

    def test_get_config(
        self, service: BackendService
    ) -> None:
        """Test getting config value."""
        resp = service.handle_request(
            Request(
                method="get_config",
                params={"key": "app.name"},
            )
        )
        assert resp.success
        assert resp.data == "Test"

    def test_set_config(
        self, service: BackendService
    ) -> None:
        """Test setting config value."""
        resp = service.handle_request(
            Request(
                method="set_config",
                params={
                    "key": "app.name",
                    "value": "Updated",
                },
            )
        )
        assert resp.success

    def test_get_plugins(
        self, service: BackendService
    ) -> None:
        """Test getting plugins."""
        resp = service.handle_request(
            Request(method="get_plugins")
        )
        assert resp.success
        assert "workspace_background" in resp.data

    def test_process_content(
        self, service: BackendService
    ) -> None:
        """Test processing content with a mode."""
        resp = service.handle_request(
            Request(
                method="process_content",
                params={
                    "mode": "realtime",
                    "content": "Test paragraph",
                },
            )
        )
        assert resp.success
        assert resp.data["mode"] == "realtime"

    def test_translate(
        self, service: BackendService
    ) -> None:
        """Test translation via service."""
        resp = service.handle_request(
            Request(
                method="translate",
                params={"text": "こんにちは"},
            )
        )
        assert resp.success
        assert "translation" in resp.data

    def test_add_and_get_terms(
        self, service: BackendService
    ) -> None:
        """Test term management."""
        service.handle_request(
            Request(
                method="add_term",
                params={
                    "source": "test",
                    "target": "测试",
                },
            )
        )
        resp = service.handle_request(
            Request(method="get_terms")
        )
        assert resp.success
        assert len(resp.data) >= 1

    def test_get_methods(
        self, service: BackendService
    ) -> None:
        """Test getting available methods."""
        resp = service.handle_request(
            Request(method="get_methods")
        )
        assert resp.success
        assert len(resp.data) > 0
        method_names = [m["method"] for m in resp.data]
        assert "translate" in method_names
        assert "get_config" in method_names

    def test_unknown_method(
        self, service: BackendService
    ) -> None:
        """Test handling unknown method."""
        resp = service.handle_request(
            Request(method="nonexistent")
        )
        assert not resp.success
        assert "Unknown method" in resp.error

    def test_call_plugin(
        self, service: BackendService
    ) -> None:
        """Test calling plugin function."""
        resp = service.handle_request(
            Request(
                method="call_plugin",
                params={
                    "plugin": "workspace_background",
                    "function": "get_background",
                },
            )
        )
        assert resp.success
        assert "enabled" in resp.data

    def test_bookmarks(
        self, service: BackendService
    ) -> None:
        """Test bookmark management."""
        service.handle_request(
            Request(
                method="add_bookmark",
                params={
                    "position": 10,
                    "label": "Test Bookmark",
                },
            )
        )
        resp = service.handle_request(
            Request(method="get_bookmarks")
        )
        assert resp.success

    def test_check_api(
        self, service: BackendService
    ) -> None:
        """Test API check."""
        resp = service.handle_request(
            Request(method="check_api")
        )
        assert resp.success
        assert "available" in resp.data

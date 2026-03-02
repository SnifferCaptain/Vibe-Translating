"""Mock translation API server for testing.

Supports both OpenAI-compatible and Ollama API formats.
Returns predictable translations for testing.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Optional


MOCK_TRANSLATIONS = {
    "こんにちは": "你好",
    "おはようございます": "早上好",
    "ありがとう": "谢谢",
    "Hello": "你好",
    "Good morning": "早上好",
}


def _get_mock_translation(text: str) -> str:
    """Get mock translation for text.

    Args:
        text: Source text.

    Returns:
        Mock translated text.
    """
    for src, tgt in MOCK_TRANSLATIONS.items():
        if src in text:
            return text.replace(src, tgt)
    return f"[Translated] {text}"


class MockAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for mock API requests."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress log output during tests."""
        pass

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/v1/models":
            self._send_json({
                "data": [
                    {"id": "mock-model", "object": "model"}
                ]
            })
        elif self.path == "/api/tags":
            self._send_json({
                "models": [
                    {"name": "mock-model", "size": 0}
                ]
            })
        else:
            self._send_json({"status": "ok"})

    def do_POST(self) -> None:
        """Handle POST requests."""
        content_length = int(
            self.headers.get("Content-Length", 0)
        )
        body = self.rfile.read(content_length)
        data = json.loads(body) if body else {}

        if self.path == "/v1/chat/completions":
            self._handle_openai_chat(data)
        elif self.path == "/api/chat":
            self._handle_ollama_chat(data)
        else:
            self._send_json({"error": "Unknown endpoint"}, 404)

    def _handle_openai_chat(
        self, data: dict[str, Any]
    ) -> None:
        """Handle OpenAI-format chat completion."""
        messages = data.get("messages", [])
        last_msg = messages[-1] if messages else {}
        content = last_msg.get("content", "")
        translation = _get_mock_translation(content)

        self._send_json({
            "id": "mock-completion",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": translation,
                },
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": len(content) // 4,
                "completion_tokens": len(translation) // 4,
                "total_tokens": (
                    len(content) + len(translation)
                ) // 4,
            },
        })

    def _handle_ollama_chat(
        self, data: dict[str, Any]
    ) -> None:
        """Handle Ollama-format chat request."""
        messages = data.get("messages", [])
        last_msg = messages[-1] if messages else {}
        content = last_msg.get("content", "")
        translation = _get_mock_translation(content)

        self._send_json({
            "message": {
                "role": "assistant",
                "content": translation,
            },
            "done": True,
            "prompt_eval_count": len(content) // 4,
            "eval_count": len(translation) // 4,
        })

    def _send_json(
        self, data: dict[str, Any], status: int = 200
    ) -> None:
        """Send JSON response.

        Args:
            data: Response data.
            status: HTTP status code.
        """
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


class MockServer:
    """Mock API server for testing.

    Can be started and stopped programmatically.
    """

    def __init__(
        self, host: str = "127.0.0.1", port: int = 0
    ) -> None:
        """Initialize mock server.

        Args:
            host: Server host.
            port: Server port (0 for auto-assign).
        """
        self.server = HTTPServer(
            (host, port), MockAPIHandler
        )
        self.host = host
        self.port = self.server.server_address[1]
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the server in a background thread."""
        self._thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the server."""
        self.server.shutdown()
        if self._thread:
            self._thread.join(timeout=5)

    @property
    def base_url(self) -> str:
        """Get server base URL."""
        return f"http://{self.host}:{self.port}"

    @property
    def openai_url(self) -> str:
        """Get OpenAI-compatible URL."""
        return f"{self.base_url}/v1"

    @property
    def ollama_url(self) -> str:
        """Get Ollama-compatible URL."""
        return self.base_url

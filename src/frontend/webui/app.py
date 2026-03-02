"""WebUI frontend for Vibe Translating.

Flask-based web interface with VS Code-like layout.
"""

import json
from typing import Any

from flask import Flask, jsonify, render_template, request

from ...backend.service import BackendService
from ..common.protocol import Request


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)
service = BackendService()


@app.route("/")
def index() -> str:
    """Render main page."""
    return render_template("index.html")


@app.route("/api/call", methods=["POST"])
def api_call() -> Any:
    """Handle API calls from frontend.

    Expects JSON body with 'method' and 'params'.
    """
    data = request.get_json()
    if not data or "method" not in data:
        return jsonify({"success": False, "error": "Invalid request"}), 400

    req = Request(
        method=data["method"],
        params=data.get("params", {}),
        request_id=data.get("request_id"),
    )
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/modes")
def get_modes() -> Any:
    """Get available translation modes."""
    req = Request(method="get_modes")
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/config")
def get_config() -> Any:
    """Get all configuration."""
    req = Request(method="get_all_config")
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/config", methods=["POST"])
def set_config() -> Any:
    """Set configuration value."""
    data = request.get_json()
    if not data or "key" not in data:
        return jsonify({"success": False, "error": "Missing key"}), 400
    req = Request(
        method="set_config",
        params={"key": data["key"], "value": data["value"]},
    )
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/translate", methods=["POST"])
def translate() -> Any:
    """Translate text."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"success": False, "error": "Missing text"}), 400
    req = Request(
        method="translate",
        params={"text": data["text"]},
    )
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/plugins")
def get_plugins() -> Any:
    """Get plugin information."""
    req = Request(method="get_plugins")
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/memory")
def get_memory() -> Any:
    """Get agent memory."""
    req = Request(method="get_memory")
    response = service.handle_request(req)
    return jsonify(response.to_dict())


@app.route("/api/methods")
def get_methods() -> Any:
    """Get all available backend methods."""
    req = Request(method="get_methods")
    response = service.handle_request(req)
    return jsonify(response.to_dict())


def main() -> None:
    """Entry point for WebUI frontend."""
    host = service.config.get("frontend.webui.host", "127.0.0.1")
    port = service.config.get("frontend.webui.port", 5000)
    debug = service.config.get("frontend.webui.debug", False)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

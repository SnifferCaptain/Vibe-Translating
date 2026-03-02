# Vibe Translating - Development Guide

## Architecture Overview

Vibe Translating is a Python-based AI translation platform with a strict frontend-backend separation.

### Directory Structure

```
Vibe-Translating/
├── .agent/                    # Project planning documents
├── src/
│   ├── backend/               # Backend core
│   │   ├── config/            # YAML configuration system
│   │   ├── api/               # LLM API clients (OpenAI, Ollama)
│   │   ├── agent/             # Translation agent with memory
│   │   ├── translation/       # Translation modes
│   │   ├── plugins/           # Plugin system
│   │   └── service.py         # Backend service layer
│   └── frontend/              # Frontend implementations
│       ├── common/            # Shared protocol
│       ├── cli/               # CLI frontend (Rich + prompt_toolkit)
│       ├── webui/             # Web UI (Flask)
│       └── gui/               # Desktop GUI (PyQt6)
├── tests/                     # Test suite with mock server
├── config/                    # Default configuration (YAML)
├── plugins/                   # External plugins directory
├── scripts/                   # Setup and build scripts
└── docs/                      # Documentation
```

### Core Principles

1. **Frontend-Backend Separation**: All frontends communicate with the backend through structured `Request`/`Response` objects via `ServiceProtocol`.
2. **YAML Configuration**: All parameters are stored in YAML files and accessible via dot-notation.
3. **Plugin System**: Backend exposes function definitions; plugins can extend functionality.
4. **Multi-Frontend**: CLI, WebUI, and PyQt GUI share the same backend.

## Getting Started

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### Setup

```bash
# Linux/macOS
bash scripts/setup.sh

# Windows
scripts\setup.bat

# Manual setup
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Running

```bash
# CLI
python -m src.frontend.cli.app

# WebUI (http://localhost:5000)
python -m src.frontend.webui.app

# GUI
python -m src.frontend.gui.app
```

### Testing

```bash
python -m pytest tests/ -v
```

## Backend Architecture

### Configuration System (`src/backend/config/`)

The `ConfigManager` handles all configuration:

```python
from src.backend.config import ConfigManager

config = ConfigManager()
config.get("api.provider")           # Get value
config.set("api.provider", "ollama") # Set value
config.save()                        # Save to file
config.get_flat()                    # Get all as flat dict
```

### API Clients (`src/backend/api/`)

Supports OpenAI-compatible and Ollama APIs:

```python
from src.backend.api import create_client, Message

client = create_client("openai", base_url="...", api_key="...")
response = client.chat([Message(role="user", content="Translate: こんにちは")])
print(response.content)
```

### Agent System (`src/backend/agent/`)

The `TranslationAgent` manages:
- **Memory**: Term extraction, summaries, bookmarks (persisted to YAML)
- **Context**: Message history with automatic summarization
- **Tools**: Extensible tool registry with OpenAI function calling format

```python
from src.backend.agent import TranslationAgent

agent = TranslationAgent(client=api_client)
agent.configure(source_lang="ja", target_lang="zh-CN")
result = agent.translate("こんにちは世界")
```

### Translation Modes (`src/backend/translation/`)

Four built-in modes:
- **Realtime**: In-place translation preserving formatting
- **Book**: Full book translation with chapter splitting
- **Frame Select**: Bounding box selection for images
- **Supervision**: Professional review with side-by-side comparison

### Service Layer (`src/backend/service.py`)

`BackendService` exposes all functionality via `ServiceProtocol`:

```python
from src.backend.service import BackendService
from src.frontend.common.protocol import Request

service = BackendService()
response = service.handle_request(
    Request(method="translate", params={"text": "Hello"})
)
```

## Frontend Development

### Protocol

All frontends use the same `Request`/`Response` protocol:

```python
from src.frontend.common.protocol import Request, Response

# Create a request
req = Request(method="translate", params={"text": "Hello"})

# Handle response
resp = service.handle_request(req)
if resp.success:
    print(resp.data)
```

### Adding a New Frontend

1. Create a new directory under `src/frontend/`
2. Import `BackendService` and `Request`/`Response`
3. Call `service.handle_request()` for all backend operations
4. Never access backend internals directly

## Code Style

- PEP 8 compliant
- Max line length: 100 characters
- Max file length: 500 lines
- Type hints on all functions
- Google-style docstrings
- Double quotes for strings

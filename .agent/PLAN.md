# Project Implementation Plan

## Project Overview

Vibe-Translating is a Python-based translation platform powered by AI agents. It supports multiple frontends (CLI, WebUI, PyQt GUI), multiple AI backends (OpenAI, Ollama), and a plugin system for extensibility.

## Architecture Overview

```
src/
├── frontend/          # UI layers (CLI, WebUI, PyQt GUI)
│   ├── cli/
│   ├── webui/
│   └── gui/
├── backend/           # Core logic, API clients, agent system
│   ├── api_clients/   # OpenAI, Ollama adapters
│   ├── agents/        # Agent orchestration and memory
│   └── translator/    # Translation modes and pipeline
├── plugins/           # Plugin system and built-in plugins
└── config/            # YAML configuration management
```

- **Frontend–Backend Separation**: All frontends communicate with the backend exclusively via structured JSON messages. No frontend contains business logic.
- **Plugin System**: Plugins are discovered and loaded dynamically. Each plugin declares its capabilities in a manifest.
- **Configuration**: All parameters are stored in YAML files and managed through a central config module.

## Technology Stack

| Component       | Technology          |
|-----------------|---------------------|
| Language        | Python 3.10+        |
| WebUI           | Flask + SocketIO    |
| Desktop GUI     | PyQt6               |
| Configuration   | PyYAML              |
| HTTP Client     | httpx               |
| CLI UX          | Rich, prompt-toolkit|
| Image handling  | Pillow              |
| File watching   | watchdog            |
| Testing         | pytest              |

## Implementation Phases

### Phase 1 — Core Foundation
- Project scaffolding and configuration system
- YAML config load/save
- Backend message protocol (JSON)
- Basic translation pipeline

### Phase 2 — AI Backends
- OpenAI API client
- Ollama API client
- Agent memory system
- Translation mode registry

### Phase 3 — Frontends
- CLI frontend (Rich + prompt-toolkit)
- WebUI frontend (Flask + SocketIO)
- PyQt6 desktop GUI

### Phase 4 — Plugin System
- Plugin loader and manifest format
- Workspace background plugin
- Plugin hook points

### Phase 5 — Deployment & Polish
- Deployment scripts for Windows and Ubuntu
- Documentation
- End-to-end testing

## Communication Protocol

All frontend–backend communication uses structured JSON messages:

```json
{
  "type": "translate_request",
  "payload": {
    "text": "...",
    "source_lang": "en",
    "target_lang": "ja",
    "mode": "standard"
  }
}
```

## Configuration

All runtime parameters are stored in YAML:

```yaml
api:
  provider: openai
  model: gpt-4o-mini
translation:
  default_source: en
  default_target: ja
plugins:
  enabled:
    - workspace_background
```

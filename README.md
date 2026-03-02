# Vibe Translating

AI-powered translation platform with intelligent agent support.

## Features

- **Multiple Frontends**: CLI, Web UI, and Desktop GUI (PyQt6)
- **AI Translation Agent**: Memory system, term extraction, context summarization
- **Translation Modes**: Real-time, Book, Frame Select, Supervision
- **Plugin System**: Extensible architecture with built-in workspace background plugin
- **YAML Configuration**: All parameters stored and editable via GUI or config files
- **API Support**: OpenAI-compatible and Ollama local deployment

## Quick Start

```bash
# Setup
bash scripts/setup.sh

# Run CLI
python -m src.frontend.cli.app

# Run Web UI (http://localhost:5000)
python -m src.frontend.webui.app

# Run Desktop GUI
python -m src.frontend.gui.app

# Run tests
python -m pytest tests/ -v
```

## Documentation

- [Development Guide](docs/development.md)
- [Plugin Development](docs/plugin_development.md)
- [User Manual](docs/user_manual.md)

## License

MIT

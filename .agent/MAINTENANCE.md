# Maintenance Guidelines

## Adding a New Translation Mode

1. Create a new module in `src/backend/translator/modes/`.
2. Implement a class that inherits from the base `TranslationMode`.
3. Define the mode name, prompt template, and any mode-specific parameters.
4. Register the mode in `src/backend/translator/registry.py`.
5. Add tests in `tests/backend/translator/modes/`.

```python
from src.backend.translator.modes.base import TranslationMode

class FormalMode(TranslationMode):
    name = "formal"
    description = "Produces formal, polished translations."

    def build_prompt(self, text: str, source: str, target: str) -> str:
        return f"Translate formally from {source} to {target}: {text}"
```

## Adding a New Plugin

1. Create a directory under `plugins/` with a `manifest.yaml` and a Python entry point.
2. In `manifest.yaml`, declare the plugin name, version, and hook points.
3. Implement hook functions referenced by the manifest.
4. The plugin loader discovers and loads the plugin automatically on startup.

```
plugins/
└── my_plugin/
    ├── manifest.yaml
    └── plugin.py
```

## Adding a New Frontend

1. Create a package under `src/frontend/<name>/`.
2. Implement an `app.py` with a `main()` entry point.
3. Communicate with the backend only through the JSON message protocol.
4. Add an entry in `[project.scripts]` in `pyproject.toml`.
5. Add tests in `tests/frontend/<name>/`.

## Dependency Management

This project uses **uv** as the primary package manager.

```bash
# Add a runtime dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Sync the environment
uv sync

# Fallback with pip
pip install -e ".[dev]"
```

Keep `requirements.txt` in sync with `pyproject.toml` for environments that do not support uv.

## Testing Requirements

- Run the full suite before every merge: `pytest`
- Add tests for every new module, mode, or plugin.
- Use mock servers (via `pytest` fixtures) for API client tests—never call live APIs in CI.
- Maintain the test directory structure to mirror `src/`.

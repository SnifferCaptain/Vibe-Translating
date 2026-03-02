# Coding Style Guide

## Python Standards

- **PEP 8** compliant at all times.
- **Max line length**: 100 characters.
- **Max file length**: 500 lines. Split into modules if a file exceeds this.
- **Type hints** on every function signature and variable where non-obvious.
- **All strings use double quotes** (`"hello"`, not `'hello'`).

## Docstrings

Use **Google-style** docstrings:

```python
def translate(text: str, target: str) -> str:
    """Translate text to the target language.

    Args:
        text: Source text to translate.
        target: ISO 639-1 language code.

    Returns:
        Translated text.

    Raises:
        TranslationError: If the API call fails.
    """
```

## Imports

Order imports in three groups separated by blank lines:

1. Standard library
2. Third-party packages
3. Local / project modules

```python
import os
from pathlib import Path

import httpx
import yaml

from src.backend.translator.engine import TranslationEngine
```

## Naming Conventions

| Element         | Convention    | Example              |
|-----------------|---------------|----------------------|
| Functions       | snake_case    | `load_config()`      |
| Variables       | snake_case    | `source_text`        |
| Classes         | PascalCase    | `TranslationAgent`   |
| Constants       | UPPER_SNAKE   | `MAX_RETRIES`        |
| Modules/files   | snake_case    | `api_client.py`      |

## Configuration

- Use **YAML** for all configuration files.
- Access config values through the central config module, never by reading files directly in business logic.

## Frontend–Backend Communication

- All messages between frontends and the backend use **structured data** (`dict` or `dataclass`), serialized as JSON.
- Never pass raw strings or unstructured data across the boundary.

## Error Handling

- Define custom exception classes per domain (e.g., `TranslationError`, `ConfigError`).
- Catch specific exceptions; avoid bare `except`.

## Testing

- Mirror the `src/` structure under `tests/`.
- Prefix test files with `test_` and test functions with `test_`.
- Use `pytest` fixtures for shared setup.

# Acceptance Criteria

## Test Suite

- [ ] All unit and integration tests pass (`pytest` exits 0).
- [ ] Test coverage meets the project minimum threshold.

## Frontends

- [ ] **CLI** frontend launches, accepts input, and displays translated output.
- [ ] **WebUI** frontend starts a Flask server, serves the UI, and handles translation requests via SocketIO.
- [ ] **PyQt GUI** frontend opens a window, accepts input, and displays results.

## AI Backends

- [ ] **OpenAI** API client sends requests and parses responses correctly (tested with a mock HTTP server).
- [ ] **Ollama** API client sends requests and parses responses correctly (tested with a mock HTTP server).

## Plugin System

- [ ] Plugin loader discovers and loads plugins from the `plugins/` directory.
- [ ] The **workspace background** plugin loads without errors and executes its hook.

## Configuration

- [ ] YAML config files load correctly with default values.
- [ ] Config changes save back to YAML and persist across restarts.
- [ ] Invalid config files produce clear error messages.

## Agent Memory

- [ ] Agent memory system stores and retrieves context entries.
- [ ] Memory persists across translation requests within a session.

## Translation Modes

- [ ] All built-in translation modes register in the mode registry at startup.
- [ ] Selecting a mode applies the correct prompt and parameters.

## Deployment

- [ ] Deployment script runs successfully on **Windows** (PowerShell).
- [ ] Deployment script runs successfully on **Ubuntu** (Bash).
- [ ] Dependencies install without errors via `pip install -e .` or `uv sync`.

## Documentation

- [ ] README covers installation, usage, and configuration.
- [ ] API client interface is documented.
- [ ] Plugin authoring guide exists.
- [ ] All public modules have docstrings.

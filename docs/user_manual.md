# Vibe Translating - User Manual

## Introduction

Vibe Translating is an AI-powered translation platform that uses intelligent agents to deliver high-quality translations. It supports multiple interfaces and translation modes.

## Installation

### Quick Setup

**Linux/macOS:**
```bash
git clone https://github.com/SnifferCaptain/Vibe-Translating.git
cd Vibe-Translating
bash scripts/setup.sh
```

**Windows:**
```bat
git clone https://github.com/SnifferCaptain/Vibe-Translating.git
cd Vibe-Translating
scripts\setup.bat
```

## Configuration

### API Setup

Before using Vibe Translating, configure your translation model:

**Option 1: OpenAI-compatible API**
- Set `api.provider` to `openai`
- Set `api.openai.api_key` to your API key
- Set `api.openai.base_url` if using a custom endpoint

**Option 2: Ollama (Local)**
- Install and start [Ollama](https://ollama.ai)
- Set `api.provider` to `ollama`
- The app auto-detects Ollama at `http://localhost:11434`

### Configuration File

All settings are stored in `config/default.yaml`. User overrides are saved to `config/user_config.yaml`.

## Interfaces

### CLI (Command Line)

```bash
python -m src.frontend.cli.app
```

**Commands:**
| Command | Description |
|---------|-------------|
| `translate <text>` | Translate text |
| `modes` | Show available modes |
| `config [key]` | View configuration |
| `set <key> <value>` | Change settings |
| `plugins` | List plugins |
| `memory` | View agent memory |
| `terms` | View terminology |
| `addterm <src> <tgt>` | Add a term |
| `save` | Save config & memory |
| `help` | Show all commands |

### Web UI

```bash
python -m src.frontend.webui.app
```

Open `http://localhost:5000` in your browser.

**Layout:**
- **Activity Bar** (left): Mode icons for switching between views
- **Sidebar**: Terms, bookmarks, and memory overview
- **Workspace**: Main translation area

### Desktop GUI (PyQt6)

```bash
python -m src.frontend.gui.app
```

**Layout** mirrors the WebUI with native desktop controls.

## Translation Modes

### 🔄 Real-time Translation

Translates documents in-place, preserving original formatting.

**Supported formats:** TXT, MD, PDF, MOBI, EPUB, HTML, URL

**Display modes:**
- **Translation Only**: Shows only the translated text
- **Side by Side**: Shows source and translation together

### 📚 Book Translation

Translates entire books with chapter splitting and background processing.

**Supported formats:** TXT, MD, PDF, MOBI, EPUB, DOCX

### 🖼️ Frame Select Translation

Draw bounding boxes on images to translate specific regions (ideal for manga).

**Supported formats:** PNG, JPG, JPEG, BMP, WEBP

**Options:**
- SAM segmentation for precise text region detection
- Configurable replacement font size and color

### 📝 Supervision Mode

Professional translation review with source/target side-by-side comparison.

**Supported formats:** TXT, MD, SRT, PO

## Agent Features

### Memory System

The agent automatically:
- **Extracts terms**: Builds a terminology database for consistent translations
- **Summarizes context**: Manages context window by summarizing older content
- **Stores bookmarks**: Mark important positions in documents

### Tab Completion

Press Tab while editing translations to get AI-powered completions. Completion length is configurable.

### Expert Mode

Enable expert mode for publication-quality translations with tool calling.

## Settings Reference

All settings are accessible via GUI (WebUI/PyQt) or CLI (`set` command).

| Setting | Type | Description |
|---------|------|-------------|
| `api.provider` | string | API provider (openai/ollama) |
| `api.openai.api_key` | string | OpenAI API key |
| `api.openai.model` | string | Model name |
| `translation.source_language` | string | Source language |
| `translation.target_language` | string | Target language |
| `translation.fast_mode` | bool | Skip tool calls |
| `agent.expert_mode` | bool | Expert translation mode |
| `agent.auto_extract_terms` | bool | Auto-extract terminology |
| `agent.auto_summarize` | bool | Auto-summarize context |
| `plugins.active` | list | Active plugin names |

## Plugins

### Managing Plugins

- View plugins in the Plugins panel (🧩 icon)
- Activate/deactivate plugins via settings
- External plugins go in the `plugins/` directory

### Workspace Background Plugin

Customize the workspace background:
- Set a background image
- Adjust opacity (0.0 - 1.0)
- Change background color

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API unavailable | Check API key or Ollama service |
| Translation error | Verify model name and settings |
| Plugin not loading | Check plugin directory structure |
| GUI won't start | Install PyQt6: `pip install PyQt6` |

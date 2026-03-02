#!/bin/bash
# Vibe Translating - Setup Script for Linux/macOS
set -e

echo "=== Vibe Translating Setup ==="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "Python version: $python_version"

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Using uv to create virtual environment..."
uv venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -r requirements.txt

echo "Installing dev dependencies..."
uv pip install pytest pytest-cov pytest-asyncio

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the CLI:"
echo "  python -m src.frontend.cli.app"
echo ""
echo "To run the WebUI:"
echo "  python -m src.frontend.webui.app"
echo ""
echo "To run the GUI:"
echo "  python -m src.frontend.gui.app"
echo ""
echo "To run tests:"
echo "  python -m pytest tests/ -v"

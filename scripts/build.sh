#!/bin/bash
# Vibe Translating - Build/Package Script for Linux/macOS
set -e

echo "=== Vibe Translating Build ==="

# Ensure virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "Error: Virtual environment not found. Run setup.sh first."
        exit 1
    fi
fi

echo "Running tests..."
python -m pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed! Aborting build."
    exit 1
fi

echo "Building package..."
pip install build
python -m build

echo ""
echo "=== Build Complete ==="
echo "Distribution files are in dist/"
ls -la dist/

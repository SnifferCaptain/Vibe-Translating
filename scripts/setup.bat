@echo off
REM Vibe Translating - Setup Script for Windows
echo === Vibe Translating Setup ===

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
)

echo Creating virtual environment with uv...
uv venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
uv pip install -r requirements.txt

echo Installing dev dependencies...
uv pip install pytest pytest-cov pytest-asyncio

echo.
echo === Setup Complete ===
echo.
echo To activate the environment:
echo   .venv\Scripts\activate.bat
echo.
echo To run the CLI:
echo   python -m src.frontend.cli.app
echo.
echo To run the WebUI:
echo   python -m src.frontend.webui.app
echo.
echo To run the GUI:
echo   python -m src.frontend.gui.app
echo.
echo To run tests:
echo   python -m pytest tests/ -v

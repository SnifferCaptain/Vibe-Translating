@echo off
REM Vibe Translating - Build/Package Script for Windows
echo === Vibe Translating Build ===

REM Ensure virtual environment is active
if not defined VIRTUAL_ENV (
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    ) else (
        echo Error: Virtual environment not found. Run setup.bat first.
        exit /b 1
    )
)

echo Running tests...
python -m pytest tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo Tests failed! Aborting build.
    exit /b 1
)

echo Building package...
pip install build
python -m build

echo.
echo === Build Complete ===
echo Distribution files are in dist/
dir dist\

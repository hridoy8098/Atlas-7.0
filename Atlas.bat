@echo off
title Atlas 7.0 — Personal AI Assistant
cd /d "%~dp0"
echo ============================================================
echo   ATLAS 7.0 — Personal AI Assistant
echo ============================================================
echo.
echo  Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo  Python found
echo.
echo  Installing/updating dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Some packages failed to install
    echo The app may not work correctly.
)
echo.
echo  Starting Atlas 7.0...
echo  Open http://localhost:8000 in your browser
echo  Press Ctrl+C to stop
echo.
python main.py
pause

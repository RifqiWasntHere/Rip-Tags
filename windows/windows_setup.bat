@echo off

cd /d "%~dp0"

echo === SETUP RIP TAGS ===

where python >nul 2>nul

if errorlevel 1 (
    echo.
    echo Python not found.
    echo Install Python from:
    echo https://python.org
    pause
    exit /b
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete.
pause

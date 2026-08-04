@echo off
setlocal

cd /d "%~dp0\.."

echo === SETUP RIP TAGS ===

where python >nul 2>nul

if errorlevel 1 (
    echo.
    echo Python not found.
    echo Install Python from:
    echo https://python.org
    if not "%CI%"=="true" pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    if not "%CI%"=="true" pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo.
echo Setup complete.
if not "%CI%"=="true" pause
endlocal

@echo off
setlocal

set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"
set "PROJECT_DIR=%CD%"

echo === SETUP RIP TAGS ===
echo Script directory: "%~dp0"
echo Project directory: "%PROJECT_DIR%"
echo Current directory: %CD%

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found at "%PROJECT_DIR%\requirements.txt"
    if not "%CI%"=="true" pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo Python not found.
    echo Install Python from:
    echo https://python.org
    if not "%CI%"=="true" pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment in "%PROJECT_DIR%\.venv"...
    python -m venv ".venv"
)

call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    if not "%CI%"=="true" pause
    exit /b 1
)

pip install -r "requirements.txt"
if errorlevel 1 (
    echo Failed to install requirements.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo.
echo Setup complete.
if not "%CI%"=="true" pause
endlocal

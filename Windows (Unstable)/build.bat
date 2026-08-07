@echo off
setlocal

set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"
set "PROJECT_DIR=%CD%"

echo === BUILD RIP TAGS ===
echo Script directory: "%~dp0"
echo Project directory: "%PROJECT_DIR%"
echo Current directory: %CD%

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Virtual environment not found.
    echo Run "Windows (Unstable)\windows_setup.bat" first.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo === Installing PyInstaller ===
.venv\Scripts\pip install --quiet pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo === Generating icons ===
.venv\Scripts\python build_icons.py
if errorlevel 1 (
    echo Failed to generate icons.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo === Cleaning previous build ===
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo === Building Rip Tags.exe ===
.venv\Scripts\python -m PyInstaller rip_tags.spec --noconfirm
if errorlevel 1 (
    echo Build failed.
    if not "%CI%"=="true" pause
    exit /b 1
)

if not exist "dist\Rip Tags" (
    echo.
    echo ERROR: Expected output directory "dist\Rip Tags" was not created.
    echo Listing dist directory:
    dir "dist" 2>nul || echo dist directory does not exist.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo.
echo === Build successful! ===
echo Output: dist\Rip Tags\Rip Tags.exe
echo.

if not "%CI%"=="true" pause
endlocal

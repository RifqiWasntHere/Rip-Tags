@echo off
setlocal

cd /d "%~dp0\.."

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
    pause
    exit /b 1
)

echo.
echo === Build successful! ===
echo Output: dist\Rip Tags\Rip Tags.exe
echo.

if not "%CI%"=="true" pause
endlocal

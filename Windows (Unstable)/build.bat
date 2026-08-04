@echo off
setlocal

set "PROJECT_DIR=%~dp0.."

echo === BUILD RIP TAGS ===
echo Script directory: "%~dp0"
echo Project directory: "%PROJECT_DIR%"
echo Current directory: %CD%

if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
    echo.
    echo Virtual environment not found.
    echo Run "Windows (Unstable)\windows_setup.bat" first.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo === Installing PyInstaller ===
"%PROJECT_DIR%\.venv\Scripts\pip" install --quiet pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo === Generating icons ===
"%PROJECT_DIR%\.venv\Scripts\python" "%PROJECT_DIR%\build_icons.py"
if errorlevel 1 (
    echo Failed to generate icons.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo === Cleaning previous build ===
if exist "%PROJECT_DIR%\build" rmdir /s /q "%PROJECT_DIR%\build"
if exist "%PROJECT_DIR%\dist" rmdir /s /q "%PROJECT_DIR%\dist"

echo === Building Rip Tags.exe ===
"%PROJECT_DIR%\.venv\Scripts\python" -m PyInstaller "%PROJECT_DIR%\rip_tags.spec" --noconfirm
if errorlevel 1 (
    echo Build failed.
    if not "%CI%"=="true" pause
    exit /b 1
)

echo.
echo === Build successful! ===
echo Output: %PROJECT_DIR%\dist\Rip Tags\Rip Tags.exe
echo.

if not "%CI%"=="true" pause
endlocal

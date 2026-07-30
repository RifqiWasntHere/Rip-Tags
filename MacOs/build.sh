#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

cd "$ROOT_DIR"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Virtual environment not found. Run MacOs/setup.sh first."
  exit 1
fi

echo "Installing PyInstaller..."
"$VENV_PIP" install --quiet pyinstaller

echo "Cleaning previous build..."
rm -rf build dist

echo "Building Rip Tags.app..."
"$VENV_PYTHON" -m PyInstaller rip_tags.spec --noconfirm

APP_PATH="$ROOT_DIR/dist/Rip Tags.app"

if [[ -d "$APP_PATH" ]]; then
  echo ""
  echo "Build successful!"
  echo "App location: $APP_PATH"
  echo ""
  echo "To run: open \"$APP_PATH\""
else
  echo "Build failed. Check the output above for errors."
  exit 1
fi

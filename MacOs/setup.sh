#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN=""

have_python() {
  command -v python3 >/dev/null 2>&1
}

install_python_with_brew() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "python3 not found and Homebrew is not installed."
    echo "Install Python 3 first: https://www.python.org/downloads/macos/"
    exit 1
  fi

  echo "Installing Python with Homebrew..."
  brew install python
}

if have_python; then
  PYTHON_BIN="$(command -v python3)"
else
  install_python_with_brew
  if have_python; then
    PYTHON_BIN="$(command -v python3)"
  else
    echo "python3 is still unavailable after installation."
    exit 1
  fi
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Virtual environment is incomplete. Recreating..."
  rm -rf "$VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

if [[ -f "$ROOT_DIR/requirements.txt" ]]; then
  echo "Installing dependencies..."
  "$VENV_PIP" install -r "$ROOT_DIR/requirements.txt"
else
  echo "requirements.txt not found."
  exit 1
fi

echo "Setup complete."
echo "Run the app with: $ROOT_DIR/MacOs/run.sh"

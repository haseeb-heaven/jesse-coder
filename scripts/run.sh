#!/usr/bin/env bash
# ==========================================================
# Jesse Coding Bot - Unified Interface Launcher
# ==========================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
SRC_DIR="$ROOT_DIR/source"
INT_DIR="$ROOT_DIR/interfaces"

# Detect Python virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_BIN="python3"
elif [ -f "$ROOT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$ROOT_DIR/.venv/bin/python3"
elif [ -f "$ROOT_DIR/env/bin/python3" ]; then
    PYTHON_BIN="$ROOT_DIR/env/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
else
    echo "Error: python3 not found."
    exit 1
fi

export PYTHONPATH="$INT_DIR:$SRC_DIR:$ROOT_DIR:$PYTHONPATH"

# Mode dispatch
if [ "$1" == "test" ]; then
    "$PYTHON_BIN" "$SRC_DIR/run_tests.py" "${@:2}"
elif [ "$1" == "example" ]; then
    "$PYTHON_BIN" "$SRC_DIR/example_stream.py"
elif [ "$1" == "tui" ]; then
    "$PYTHON_BIN" "$INT_DIR/tui/main.py" "${@:2}"
elif [ "$1" == "gui" ] || [ "$1" == "web" ]; then
    "$PYTHON_BIN" "$INT_DIR/gui/app.py" "${@:2}"
else
    "$PYTHON_BIN" "$INT_DIR/cli/main.py" "$@"
fi

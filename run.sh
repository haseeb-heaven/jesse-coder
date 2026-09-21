#!/usr/bin/env bash
# ==========================================================
# Jesse Coding Bot - One-Click Launcher
# ==========================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Detect Python virtual environment
if [ -f "$PARENT_DIR/env/bin/python3" ]; then
    PYTHON_BIN="$PARENT_DIR/env/bin/python3"
elif [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
else
    echo "Error: python3 not found."
    exit 1
fi

echo "Using Python: $PYTHON_BIN"
export PYTHONPATH="$PARENT_DIR:$SCRIPT_DIR:$PYTHONPATH"

# Mode dispatch
if [ "$1" == "test" ]; then
    "$PYTHON_BIN" "$SCRIPT_DIR/run_tests.py" "${@:2}"
elif [ "$1" == "example" ]; then
    "$PYTHON_BIN" "$SCRIPT_DIR/example_stream.py"
elif [ "$1" == "tui" ]; then
    "$PYTHON_BIN" "$SCRIPT_DIR/tui_app.py" "${@:2}"
else
    "$PYTHON_BIN" "$SCRIPT_DIR/main.py" "$@"
fi

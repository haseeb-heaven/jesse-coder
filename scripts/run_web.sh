#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# Activate virtual environment if available
if [ -n "$VIRTUAL_ENV" ]; then
    : # already in active virtual environment
elif [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
    source "$ROOT_DIR/.venv/bin/activate"
elif [ -f "$ROOT_DIR/env/bin/activate" ]; then
    source "$ROOT_DIR/env/bin/activate"
fi

# Ensure frontend bundle exists
if [ ! -f "$ROOT_DIR/web/static/bundle.js" ]; then
    "$SCRIPT_DIR/build_frontend.sh"
fi

echo "🚀 Starting JesseCoder WebApp from source/web_app.py..."
python3 "$ROOT_DIR/source/web_app.py" "$@"

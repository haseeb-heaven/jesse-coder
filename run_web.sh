#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Activate virtual environment if available
if [ -n "$VIRTUAL_ENV" ]; then
    : # already in active virtual environment
elif [ -f "$DIR/.venv/bin/activate" ]; then
    source "$DIR/.venv/bin/activate"
elif [ -f "$DIR/env/bin/activate" ]; then
    source "$DIR/env/bin/activate"
elif [ -f "$DIR/../env/bin/activate" ]; then
    source "$DIR/../env/bin/activate"
fi

# Ensure frontend bundle exists
if [ ! -f "$DIR/web/static/bundle.js" ]; then
    "$DIR/build_frontend.sh"
fi

echo "🚀 Starting JesseCoder WebApp..."
python3 "$DIR/web_app.py" "$@"

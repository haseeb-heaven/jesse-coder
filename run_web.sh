#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Activate virtual environment if available
if [ -f "/Users/haseeb-mir/Documents/Code/Python/env/bin/activate" ]; then
    source "/Users/haseeb-mir/Documents/Code/Python/env/bin/activate"
elif [ -f "$DIR/env/bin/activate" ]; then
    source "$DIR/env/bin/activate"
fi

# Ensure frontend bundle exists
if [ ! -f "$DIR/web/static/bundle.js" ]; then
    "$DIR/build_frontend.sh"
fi

echo "🚀 Starting JesseCoder WebApp..."
python3 "$DIR/web_app.py" "$@"

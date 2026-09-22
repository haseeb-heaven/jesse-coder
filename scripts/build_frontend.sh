#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "⚡ Compiling TypeScript frontend for JesseCoder..."
npx esbuild interfaces/gui/src/app.ts --bundle --outfile=interfaces/gui/static/bundle.js --minify
echo "✔ Frontend bundle built: interfaces/gui/static/bundle.js"

#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "⚡ Compiling TypeScript frontend for JesseCoder..."
npx esbuild web/src/app.ts --bundle --outfile=web/static/bundle.js --minify
echo "✔ Frontend bundle built: web/static/bundle.js"

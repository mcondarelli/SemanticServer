#!/usr/bin/bash
set -e

script_path=$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")
sdir="$(dirname "${script_path}")"
here="$(cd "$sdir" && pwd)"

root="$(dirname "${here}")"
cd $root

YAML="$root/openapi.yaml"
OUT="$root/src/semanticserver/models/generated.py"
VENV="$root/.venv"

# Sanity check
[ -f "$YAML" -a -d "$(dirname $OUT)" -a -d "$VENV" ] \
    || (echo "ERROR '$script_path' should be in SemanticParser/scripts/"; exit 1)

source "$VENV/bin/activate"

echo "🚀 Launching Semantic Server..."
uvicorn semanticserver.main:app --host 0.0.0.0 --port 9095 --reload --reload-dir "$root/src/semanticserver" --app-dir src

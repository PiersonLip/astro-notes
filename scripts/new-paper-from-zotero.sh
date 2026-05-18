#!/usr/bin/env bash
# Create a paper note from the current Zotero selection (optional title override).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/new-paper.py"

title=${1:-}
folder=${2:-}
doi=${3:-}

args=(--from-zotero)
if [[ -n "${title// }" ]]; then
  args+=("$title")
fi
if [[ -n "${folder// }" ]]; then
  args+=(--folder "$folder")
fi
if [[ -n "${doi// }" ]]; then
  args+=(--doi "$doi")
fi

python3 "$PY" "${args[@]}"
exec "$ROOT/scripts/focus-last-created.sh"

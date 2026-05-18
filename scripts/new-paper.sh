#!/usr/bin/env bash
# Usage: new-paper.sh "title" cite_key [folder] [doi]
# Optional folder/doi are omitted when blank (safe for VS Code task inputs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/new-paper.py"

title=${1:?title required}
cite_key=${2:?cite_key required}
folder=${3:-}
doi=${4:-}

args=("$title" "$cite_key")
if [[ -n "${folder// }" ]]; then
  args+=(--folder "$folder")
fi
if [[ -n "${doi// }" ]]; then
  args+=(--doi "$doi")
fi

exec python3 "$PY" "${args[@]}"

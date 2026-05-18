#!/usr/bin/env bash
# Open the last file created by a note script (used after VS Code tasks).
# Must not block: tasks wait for this script to exit.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKER="$ROOT/.vscode/last-created-path"
if [[ ! -f "$MARKER" ]]; then
  exit 0
fi
path="$(tr -d '\r' <"$MARKER")"
goto="${path}:1:1"

open_bg() {
  nohup "$@" >/dev/null 2>&1 &
}

hook="${VSCODE_IPC_HOOK_CLI:-${CODE_IPC_HOOK_CLI:-}}"
if [[ -n "$hook" ]]; then
  open_bg "$hook" -r -g "$goto"
  exit 0
fi
if command -v cursor >/dev/null 2>&1; then
  open_bg cursor -r -g "$goto"
  exit 0
fi
if command -v code >/dev/null 2>&1; then
  open_bg code -r -g "$goto"
  exit 0
fi
exit 0

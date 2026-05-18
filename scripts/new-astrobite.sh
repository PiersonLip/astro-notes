#!/usr/bin/env bash
# Wrapper for new-astrobite.py (keeps task/shell usage unchanged)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/new-astrobite.py" "$@"

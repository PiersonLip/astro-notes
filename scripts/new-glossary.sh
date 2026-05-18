#!/usr/bin/env bash
# Usage: new-glossary.sh [key] [name] [description]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/new-glossary.py" "$@"
exec "$ROOT/scripts/focus-last-created.sh"

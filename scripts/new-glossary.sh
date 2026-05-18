#!/usr/bin/env bash
# Usage: new-glossary.sh [key] [name] [description]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/new-glossary.py" "$@"

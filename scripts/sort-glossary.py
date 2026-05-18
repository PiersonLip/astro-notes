#!/usr/bin/env python3
"""Sort subTex/Astro-glossary.tex entries alphabetically by key."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from glossary_utils import sort_glossary_file

ROOT = Path(__file__).resolve().parent.parent
GLOSSARY_FILE = ROOT / "subTex" / "Astro-glossary.tex"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sort glossary entries A–Z by key.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report whether sorting is needed without writing",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=GLOSSARY_FILE,
        help="Glossary file path",
    )
    args = parser.parse_args()

    path = args.file.resolve()
    if not path.is_file():
        print(f"Not found: {path}", file=sys.stderr)
        return 1

    try:
        changed, msg = sort_glossary_file(path, dry_run=args.dry_run)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(msg)
    return 0 if changed or not args.dry_run else 0


if __name__ == "__main__":
    sys.exit(main())

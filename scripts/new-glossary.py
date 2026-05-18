#!/usr/bin/env python3
"""Add a glossary entry to subTex/Astro-glossary.tex (matches glossaryEntry snippet)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from glossary_utils import entry_exists, format_entry, sort_glossary_file
from note_utils import open_in_editor

ROOT = Path(__file__).resolve().parent.parent
GLOSSARY_FILE = ROOT / "subTex" / "Astro-glossary.tex"


def name_to_key(name: str, prefix: str = "") -> str:
    """Suggest a key like hierarchical-merger from a display name."""
    words = re.findall(r"[A-Za-z0-9]+", name)
    key = "-".join(w.lower() for w in words if w)
    if prefix:
        prefix = prefix.rstrip(":") + ":"
        if not key.startswith(prefix):
            key = prefix + key
    return key


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add \\newglossaryentry to Astro-glossary.tex and sort."
    )
    parser.add_argument("key", nargs="?", default="", help="Entry key (e.g. ac:GW, TDE)")
    parser.add_argument("name", nargs="?", default="", help="Display name field")
    parser.add_argument(
        "description",
        nargs="?",
        default="",
        help="Description (use \\\\ for line breaks)",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional key prefix without colon (ac, obs)",
    )
    args = parser.parse_args()

    key = args.key.strip()
    name = args.name.strip()
    description = args.description.strip()

    if not key and name:
        key = name_to_key(name, args.prefix.strip())
    if not key or not name:
        parser.print_help()
        return 1

    if entry_exists(GLOSSARY_FILE, key):
        print(f"Key already exists: {key}", file=sys.stderr)
        return 1

    block = format_entry(key, name, description)
    existing = GLOSSARY_FILE.read_text(encoding="utf-8") if GLOSSARY_FILE.is_file() else ""
    sep = "" if (not existing or existing.endswith("\n")) else "\n"
    GLOSSARY_FILE.write_text(existing + sep + block + "\n", encoding="utf-8")

    changed, sort_msg = sort_glossary_file(GLOSSARY_FILE)
    print(f"Added: {key}")
    print(f"Use in notes: \\gls{{{key}}}")
    if changed:
        print(sort_msg)

    open_in_editor(GLOSSARY_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())

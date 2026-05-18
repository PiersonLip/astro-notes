"""Parse and sort \\newglossaryentry blocks in Astro-glossary.tex."""

from __future__ import annotations

import re
from pathlib import Path

ENTRY_START = re.compile(r"\\newglossaryentry\{([^}]+)\}\{")


def parse_glossary_entries(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (preamble, [(sort_key, entry_text), ...])."""
    m = ENTRY_START.search(text)
    if not m:
        return text, []

    preamble = text[: m.start()].rstrip()
    entries: list[tuple[str, str]] = []
    pos = m.start()

    while pos < len(text):
        m = ENTRY_START.search(text, pos)
        if not m:
            break
        key = m.group(1)
        brace = m.end() - 1
        depth = 0
        end = brace
        for i in range(brace, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        else:
            raise ValueError(f"Unclosed glossary entry for key: {key!r}")

        entry_text = text[m.start() : end].rstrip()
        entries.append((key.lower(), entry_text))
        pos = end
        while pos < len(text) and text[pos] in "\r\n":
            pos += 1

    return preamble, entries


def validate_entries(entries: list[tuple[str, str]]) -> None:
    for sort_key, entry in entries:
        if not entry.strip().startswith(r"\newglossaryentry"):
            raise ValueError(
                f"Malformed entry {sort_key!r}: does not start with \\newglossaryentry"
            )
        if entry.count("{") != entry.count("}"):
            raise ValueError(
                f"Malformed entry {sort_key!r}: unbalanced braces "
                f"({entry.count('{')} open, {entry.count('}')} close)"
            )


def sort_glossary_file(path: Path, dry_run: bool = False) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    preamble, entries = parse_glossary_entries(text)
    if not entries:
        return False, "No glossary entries found."

    validate_entries(entries)
    sorted_entries = sorted(entries, key=lambda x: x[0])
    if [e[1] for e in entries] == [e[1] for e in sorted_entries]:
        return False, "Glossary already sorted."

    body = "\n\n".join(e[1] for e in sorted_entries)
    if preamble:
        new_text = preamble + "\n\n" + body + "\n"
    else:
        new_text = body + "\n"

    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True, f"Sorted {len(entries)} entries in {path.name}"


def format_entry(key: str, name: str, description: str) -> str:
    desc = description.replace("\r\n", "\n").strip()
    return (
        f"\\newglossaryentry{{{key}}}{{\n"
        f"name={{{name}}},\n"
        f"description={{{desc}}}\n"
        f"}}"
    )


def entry_exists(path: Path, key: str) -> bool:
    if not path.is_file():
        return False
    pattern = re.compile(rf"\\newglossaryentry\{{{re.escape(key)}\}}\{{")
    return bool(pattern.search(path.read_text(encoding="utf-8")))

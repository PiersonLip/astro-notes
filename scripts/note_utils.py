"""Shared helpers for astro note scripts."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

SMALL_WORDS = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or"}
BIB_KEY = re.compile(r"@\w+\{([^,]+),")


def title_to_basename(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    parts: list[str] = []
    for i, w in enumerate(words):
        if i > 0 and w.lower() in SMALL_WORDS:
            parts.append(w.lower())
        else:
            parts.append(w[:1].upper() + w[1:].lower() if w else "")
    return "".join(parts)


def latex_escape(s: str) -> str:
    repl = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
    ]
    for a, b in repl:
        s = s.replace(a, b)
    return s


def read_bib_keys(bib_file: Path) -> set[str]:
    if not bib_file.is_file():
        return set()
    return set(BIB_KEY.findall(bib_file.read_text(encoding="utf-8")))


def cite_key_in_bib(bib_file: Path, key: str) -> bool:
    return key in read_bib_keys(bib_file)


def cite_key_in_any(bib_files: list[Path], key: str) -> Path | None:
    """Return the first .bib file that contains key, else None."""
    for bib_file in bib_files:
        if cite_key_in_bib(bib_file, key):
            return bib_file
    return None


def append_bib_block(bib_file: Path, block: str) -> None:
    existing = bib_file.read_text(encoding="utf-8") if bib_file.is_file() else ""
    prefix = "" if (not existing or existing.endswith("\n")) else "\n"
    bib_file.write_text(existing + prefix + block.rstrip() + "\n", encoding="utf-8")


def register_input_line(input_file: Path, line: str) -> None:
    if not input_file.is_file():
        return
    body = input_file.read_text(encoding="utf-8")
    if line in body:
        return
    with input_file.open("a", encoding="utf-8") as f:
        if body and not body.endswith("\n"):
            f.write("\n")
        f.write(line + "\n")


def open_in_editor(path: Path) -> None:
    for cmd in (["cursor", "-r", str(path)], ["cursor", str(path)], ["code", "-r", str(path)]):
        try:
            subprocess.run(cmd, check=False, capture_output=True)
            return
        except FileNotFoundError:
            continue

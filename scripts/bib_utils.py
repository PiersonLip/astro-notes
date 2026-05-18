"""Read cite keys and titles from AstroNotes.bib / sources.bib."""

from __future__ import annotations

import re
from pathlib import Path

ENTRY_KEY = re.compile(r"@\w+\{([^,]+),")
TITLE_FIELD = re.compile(r"\btitle\s*=\s*\{([^}]*)\}", re.I)


def parse_bib_entries(bib_path: Path) -> dict[str, str]:
    """Map cite key → title (best effort)."""
    if not bib_path.is_file():
        return {}
    text = bib_path.read_text(encoding="utf-8")
    entries: dict[str, str] = {}
    for m in ENTRY_KEY.finditer(text):
        key = m.group(1)
        start = m.start()
        end = text.find("\n@", start + 1)
        chunk = text[start : end if end != -1 else None]
        tm = TITLE_FIELD.search(chunk)
        if tm:
            title = tm.group(1).replace("{", "").replace("}", "")
            entries[key] = title
    return entries


def title_for_key(cite_key: str, bib_paths: list[Path]) -> str | None:
    for path in bib_paths:
        titles = parse_bib_entries(path)
        if cite_key in titles:
            return titles[cite_key]
    return None

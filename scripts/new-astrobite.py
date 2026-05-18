#!/usr/bin/env python3
"""Create a new Astrobites note .tex, register in astroBiteInput.tex, optional sources.bib entry."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from note_utils import open_in_editor

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "astroBitesNotes" / "notes"
INPUT_FILE = ROOT / "astroBitesNotes" / "astroBiteInput.tex"
BIB_FILE = ROOT / "sources.bib"

SMALL_WORDS = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or"}
ASTROBITES_DATE = re.compile(
    r"https?://(?:www\.)?astrobites\.org/(\d{4})/(\d{2})/(\d{2})/", re.I
)
META_AUTHOR = re.compile(
    r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']',
    re.I,
)
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


def parse_astrobites_date(url: str) -> str | None:
    m = ASTROBITES_DATE.search(url)
    if not m:
        return None
    y, mo, d = m.groups()
    return f"{y}-{mo}-{d}"


def surname_from_author(name: str) -> str:
    name = name.strip()
    if not name:
        return ""
    # "Last, First" or "First Last"
    if "," in name:
        return name.split(",", 1)[0].strip()
    parts = name.split()
    return parts[-1] if parts else name


def cite_key_for(author: str, pub_date: str, existing: set[str]) -> str:
    year = pub_date[:4] if pub_date else str(date.today().year)
    base = f"{surname_from_author(author)}{year}"
    base = re.sub(r"[^A-Za-z0-9]", "", base)
    if not base:
        base = f"Astrobite{year}"
    key = base
    n = 2
    while key in existing:
        key = f"{base}{chr(96 + n)}" if n < 27 else f"{base}{n}"
        n += 1
    return key


def fetch_author(url: str) -> str | None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read(400_000).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    m = META_AUTHOR.search(html)
    return m.group(1).strip() if m else None


def read_bib_keys() -> set[str]:
    if not BIB_FILE.is_file():
        return set()
    return set(BIB_KEY.findall(BIB_FILE.read_text(encoding="utf-8")))


def url_in_bib(url: str) -> bool:
    if not BIB_FILE.is_file():
        return False
    return url in BIB_FILE.read_text(encoding="utf-8")


def append_bib_entry(
    key: str, author: str, title: str, pub_date: str, url: str
) -> None:
    today = date.today().isoformat()
    block = f"""
@online{{{key},
  author = {{{author}}},
  title = {{{title}}},
  date = {{{pub_date}}},
  url = {{{url}}},
  organization = {{Astrobites}},
  urldate = {{{today}}}
}}
"""
    existing = BIB_FILE.read_text(encoding="utf-8") if BIB_FILE.is_file() else ""
    prefix = "" if (not existing or existing.endswith("\n")) else "\n"
    BIB_FILE.write_text(existing + prefix + block, encoding="utf-8")


def write_tex(path: Path, title: str, cite_key: str | None, label: str) -> None:
    safe_title = latex_escape(title)
    cite_part = f" \\cite{{{cite_key}}}" if cite_key else ""
    content = f"""\\pagebreak
\\chapter{{{safe_title}{cite_part} \\label{{{label}}}}}
\\hrule
\\vspace{{.5cm}}

\\section{{Abstract and intro}}
\\hrule
\\vspace{{.5cm}}

\\begin{{list}}{{-}}{{}}
\\item 
\\end{{list}}
"""
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new Astrobites note.")
    parser.add_argument("title")
    parser.add_argument("url")
    parser.add_argument(
        "author",
        nargs="?",
        default="",
        help="Author name (optional; fetched from page when omitted)",
    )
    args = parser.parse_args()

    title = args.title.strip()
    url = args.url.strip()
    author = args.author.strip()

    if not title or not url:
        parser.print_help()
        return 1

    basename = title_to_basename(title)
    if not basename:
        print("Could not derive filename from title.", file=sys.stderr)
        return 1

    tex_file = NOTES_DIR / f"{basename}.tex"
    input_line = f"\\input{{astroBitesNotes/notes/{basename}.tex}}"
    label = f"chap:{basename}"

    if tex_file.exists():
        print(f"Already exists: {tex_file}", file=sys.stderr)
        return 1

    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    pub_date = parse_astrobites_date(url)
    cite_key: str | None = None
    bib_note = ""

    if url_in_bib(url):
        bib_note = "Bib: URL already in sources.bib (skipped new entry)."
        text = BIB_FILE.read_text(encoding="utf-8")
        for m in re.finditer(r"@\w+\{([^,]+),", text):
            start = m.start()
            end = text.find("\n@", start + 1)
            chunk = text[start : end if end != -1 else None]
            if url in chunk:
                cite_key = m.group(1)
                break
    else:
        if not author:
            author = fetch_author(url) or ""

        if author and pub_date:
            keys = read_bib_keys()
            cite_key = cite_key_for(author, pub_date, keys)
            append_bib_entry(cite_key, author, title, pub_date, url)
            bib_note = f"Bib: added @online{{{cite_key}}} to sources.bib"
        elif not author:
            bib_note = (
                "Bib: skipped (could not resolve author — pass author as 3rd arg "
                "or add @online entry manually)"
            )
        else:
            bib_note = (
                "Bib: skipped (URL is not a standard astrobites.org/YYYY/MM/DD/ link)"
            )

    write_tex(tex_file, title, cite_key, label)

    if INPUT_FILE.is_file():
        body = INPUT_FILE.read_text(encoding="utf-8")
        if input_line not in body:
            with INPUT_FILE.open("a", encoding="utf-8") as f:
                if body and not body.endswith("\n"):
                    f.write("\n")
                f.write(input_line + "\n")

    print(f"Created: {tex_file}")
    print(f"Added to: astroBiteInput.tex")
    if bib_note:
        print(bib_note)

    open_in_editor(tex_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())

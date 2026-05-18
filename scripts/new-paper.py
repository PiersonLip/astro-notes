#!/usr/bin/env python3
"""Create a new paper note under paperNotes/, register in paperIncludes.tex, optional bib entry."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from bib_utils import title_for_key
from note_utils import (
    append_bib_block,
    cite_key_in_any,
    cite_key_to_folder,
    latex_escape,
    open_in_editor,
    register_input_line,
    title_to_basename,
)
from zotero_bbt import selected_citekey_and_title

ROOT = Path(__file__).resolve().parent.parent
PAPER_ROOT = ROOT / "paperNotes"
INPUT_FILE = ROOT / "paperNotes" / "paperIncludes.tex"
ZOTERO_BIB = ROOT / "AstroNotes.bib"
MANUAL_BIB = ROOT / "sources.bib"
BIB_LOOKUP = [ZOTERO_BIB, MANUAL_BIB]

ARXIV_ID = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:)\s*(\d{4}\.\d{4,5}|\d{7})", re.I
)
DOI_IN_TEXT = re.compile(r"\b(10\.\d{4,9}/[^\s\]}\"]+)", re.I)


def normalize_doi(doi: str) -> str | None:
    doi = doi.strip()
    if not doi:
        return None
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    m = DOI_IN_TEXT.search(doi)
    return m.group(1).rstrip(".,)") if m else (doi if doi.startswith("10.") else None)


def parse_arxiv_id(text: str) -> str | None:
    text = text.strip()
    m = ARXIV_ID.search(text)
    if m:
        return m.group(1)
    if re.fullmatch(r"\d{4}\.\d{4,5}|\d{7}", text):
        return text
    return None


def http_get(url: str, accept: str = "*/*", timeout: int = 25) -> str | None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "astro-notes/1.0 (mailto:local)",
            "Accept": accept,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def rekey_bibtex(bibtex: str, cite_key: str) -> str:
    return re.sub(
        r"^@\w+\{[^,]+,",
        f"@{detect_entry_type(bibtex)}{{{cite_key},",
        bibtex.strip(),
        count=1,
        flags=re.MULTILINE,
    )


def detect_entry_type(bibtex: str) -> str:
    m = re.match(r"@(\w+)\{", bibtex.strip())
    return m.group(1) if m else "article"


def fetch_bibtex_from_doi(doi: str) -> str | None:
    return http_get(f"https://doi.org/{doi}", accept="application/x-bibtex")


def fetch_bibtex_from_arxiv(arxiv_id: str) -> str | None:
    return http_get(f"https://arxiv.org/bibtex/{arxiv_id}")


def fetch_bibtex_from_crossref(doi: str) -> str | None:
    """Fallback when doi.org bibtex is unavailable."""
    raw = http_get(
        f"https://api.crossref.org/works/{doi}",
        accept="application/json",
    )
    if not raw:
        return None
    try:
        msg = json.loads(raw)["message"]
    except (KeyError, json.JSONDecodeError):
        return None

    title = (msg.get("title") or [""])[0]
    authors = msg.get("author") or []
    author_str = " and ".join(
        f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
        for a in authors
        if a.get("family")
    )
    year = ""
    for field in ("published-print", "published-online", "created"):
        parts = (msg.get(field) or {}).get("date-parts")
        if parts and parts[0]:
            year = str(parts[0][0])
            break
    journal = (msg.get("container-title") or [""])[0]
    volume = msg.get("volume", "")
    pages = msg.get("page", "")
    lines = [
        "@article{PLACEHOLDER,",
        f"\ttitle = {{{title}}},",
    ]
    if author_str:
        lines.append(f"\tauthor = {{{author_str}}},")
    if journal:
        lines.append(f"\tjournal = {{{journal}}},")
    if volume:
        lines.append(f"\tvolume = {{{volume}}},")
    if pages:
        lines.append(f"\tpages = {{{pages}}},")
    if year:
        lines.append(f"\tyear = {{{year}}},")
    lines.append(f"\tdoi = {{{doi}}},")
    lines.append(f"\turl = {{https://doi.org/{doi}}},")
    lines.append("}")
    return "\n".join(lines)


def resolve_bib(
    cite_key: str, doi: str | None, arxiv: str | None
) -> tuple[str | None, str]:
    found_in = cite_key_in_any(BIB_LOOKUP, cite_key)
    if found_in:
        return None, f"Bib: @{cite_key} found in {found_in.name}"

    if doi and not arxiv:
        aid = parse_arxiv_id(doi)
        if aid:
            arxiv = aid
            doi = None

    bibtex: str | None = None
    source = ""

    if doi:
        norm = normalize_doi(doi)
        if norm:
            bibtex = fetch_bibtex_from_doi(norm)
            source = f"DOI {norm}"
            if not bibtex:
                bibtex = fetch_bibtex_from_crossref(norm)
                source = f"Crossref {norm}"

    if not bibtex and arxiv:
        aid = parse_arxiv_id(arxiv)
        if aid:
            bibtex = fetch_bibtex_from_arxiv(aid)
            source = f"arXiv {aid}"

    if not bibtex:
        return None, (
            "Bib: skipped (cite key not in AstroNotes.bib or sources.bib — "
            "add in Zotero or pass a DOI/arXiv ID)"
        )

    block = rekey_bibtex(bibtex, cite_key)
    append_bib_block(MANUAL_BIB, block)
    return (
        block,
        f"Bib: added @{cite_key} to sources.bib from {source} "
        "(prefer adding to Zotero → AstroNotes.bib)",
    )


def write_paper_tex(path: Path, title: str, cite_key: str) -> None:
    safe_title = latex_escape(title)
    content = f"""\\ifdefined\\AnMainDocument\\else
\\documentclass[../../mainNotes.tex]{{subfiles}}
\\begin{{document}}
\\fi

\\pagebreak
\\chapter{{{safe_title} \\cite{{{cite_key}}}}}
\\hrule
\\vspace{{.5cm}}

\\section{{Abstract}}
\\hrule
\\vspace{{.5cm}}

\\begin{{list}}{{-}}{{}}
\\item 
\\end{{list}}

\\ifdefined\\AnMainDocument\\else
\\end{{document}}
\\fi
"""
    path.write_text(content, encoding="utf-8")


def fill_from_zotero(title_override: str) -> tuple[str, str] | None:
    picked = selected_citekey_and_title()
    if not picked:
        return None
    cite_key, title = picked
    if title_override.strip():
        title = title_override.strip()
    return cite_key, title


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new paper note (chapter + cite, paperNotes/ layout)."
    )
    parser.add_argument(
        "title",
        nargs="?",
        default="",
        help="Paper title (for chapter heading); optional with --from-zotero",
    )
    parser.add_argument(
        "cite_key",
        nargs="?",
        default="",
        help="BibTeX citation key (e.g. from Zotero)",
    )
    parser.add_argument(
        "--folder",
        default="",
        help="Subfolder under paperNotes/ (default: from cite key, else title)",
    )
    parser.add_argument(
        "--tex",
        default="",
        help="TeX filename (default: <folder>Notes.tex)",
    )
    parser.add_argument(
        "--doi",
        default="",
        help="DOI or doi.org URL (optional; used if cite key missing from bib)",
    )
    parser.add_argument(
        "--arxiv",
        default="",
        help="arXiv ID or URL (optional fallback for bib)",
    )
    parser.add_argument(
        "--from-zotero",
        action="store_true",
        help="Use the selected Zotero item (Better BibTeX JSON-RPC) for cite key and title",
    )
    args = parser.parse_args()

    title = args.title.strip()
    cite_key = args.cite_key.strip()

    if args.from_zotero:
        filled = fill_from_zotero(title)
        if not filled:
            print(
                "Could not read Zotero selection (is Zotero running with one item selected?)",
                file=sys.stderr,
            )
            return 1
        cite_key, zotero_title = filled
        if not title:
            title = zotero_title

    if not cite_key and not args.from_zotero:
        parser.print_help()
        return 1

    if not title:
        title = title_for_key(cite_key, BIB_LOOKUP) or cite_key

    folder = args.folder.strip() or cite_key_to_folder(cite_key) or title_to_basename(title)
    tex_name = args.tex.strip() or f"{folder}Notes.tex"

    if not folder:
        print("Could not derive folder name.", file=sys.stderr)
        return 1
    if not tex_name.endswith(".tex"):
        tex_name += ".tex"

    note_dir = PAPER_ROOT / folder
    tex_file = note_dir / tex_name
    input_line = f"\\input{{paperNotes/{folder}/{tex_name}}}"

    if tex_file.exists():
        print(f"Already exists: {tex_file}", file=sys.stderr)
        return 1

    note_dir.mkdir(parents=True, exist_ok=True)
    write_paper_tex(tex_file, title, cite_key)
    register_input_line(INPUT_FILE, input_line)

    _, bib_note = resolve_bib(cite_key, args.doi, args.arxiv)

    print(f"Created: {tex_file}")
    print(f"Added to: paperNotes/paperIncludes.tex")
    print(f"Cite key: {cite_key}")
    print(f"Folder: {folder}")
    print(bib_note)

    open_in_editor(tex_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())

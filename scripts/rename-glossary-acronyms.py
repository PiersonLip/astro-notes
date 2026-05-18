#!/usr/bin/env python3
"""One-off helper: rename acronym glossary keys to ac: prefix across the repo."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# old_key -> new_key
ACRONYM_RENAMES: dict[str, str] = {
    "AGB": "ac:AGB",
    "BEER": "ac:BEER",
    "BH_LS": "ac:BH-LS",
    "DD": "ac:DD",
    "GRBs": "ac:GRBs",
    "GWR": "ac:GWR",
    "LVB": "ac:LVB",
    "MB": "ac:MB",
    "MSP": "ac:MSP",
    "ONeMg": "ac:ONeMg",
    "RSG": "ac:RSG",
    "SD": "ac:SD",
    "SMBH": "ac:SMBH",
    "TDE": "ac:TDE",
    "TESS": "ac:TESS",
    "TI-SNe": "ac:TI-SNe",
    "TIb-SNe": "ac:TIb-SNe",
    "TIc-SNe": "ac:TIc-SNe",
    "TII-SNe": "ac:TII-SNe",
    "WNh": "ac:WNh",
    "WR-star": "ac:WR-star",
    "ZAMS": "ac:ZAMS",
    "Case-A-RLO": "ac:Case-A-RLO",
    "Case-B-RLO": "ac:Case-B-RLO",
    "odd_modes": "ac:odd-modes",
    "even_modes": "ac:even-modes",
}

REMOVE_KEYS = {"someBS"}


def replace_gls(text: str, renames: dict[str, str]) -> str:
    for old, new in sorted(renames.items(), key=lambda x: -len(x[0])):
        text = text.replace(f"\\gls{{{old}}}", f"\\gls{{{new}}}")
        text = text.replace(f"\\Gls{{{old}}}", f"\\Gls{{{new}}}")
    return text


def rename_glossary_file(path: Path, renames: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for key in REMOVE_KEYS:
        text = re.sub(
            rf"\\newglossaryentry\{{{re.escape(key)}\}}\{{[\s\S]*?\n\}}\n*",
            "",
            text,
            count=1,
        )
    for old, new in renames.items():
        text = text.replace(f"\\newglossaryentry{{{old}}}{{", f"\\newglossaryentry{{{new}}}{{")
    text = replace_gls(text, renames)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    rename_glossary_file(ROOT / "subTex" / "Astro-glossary.tex", ACRONYM_RENAMES)
    for tex in ROOT.rglob("*.tex"):
        if "tikz-cache" in tex.parts:
            continue
        body = tex.read_text(encoding="utf-8")
        updated = replace_gls(body, ACRONYM_RENAMES)
        if updated != body:
            tex.write_text(updated, encoding="utf-8")
            print(f"updated {tex.relative_to(ROOT)}")

    from glossary_utils import sort_glossary_file

    sort_glossary_file(ROOT / "subTex" / "Astro-glossary.tex")
    print("sorted glossary")


if __name__ == "__main__":
    main()

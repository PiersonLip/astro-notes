# astro-notes project memory

## Bibliography setup

- **`AstroNotes.bib`** — Zotero Better BibTeX auto-export (“Keep updated”). Do not edit by hand; Zotero overwrites on change.
- **`sources.bib`** — Manual / Astrobites entries (`Mittal2026`, `Amen2026`, book `TaurisvandenHeuvel+2023`, etc.).
- **`mainNotes.tex`** loads both: `\addbibresource{sources.bib}` and `\addbibresource{AstroNotes.bib}`.

Use **Zotero/BBT cite keys** for new paper notes (e.g. `soamPhotoevaporationDustPolarization2021`, not old `sources.bib` keys).

### Cite key migrations (old → Zotero)

| Old (`sources.bib`) | Zotero (`AstroNotes.bib`) |
|---------------------|---------------------------|
| `green_upper_2025` | `greenUpperLimitFrequency2025` |
| `el-badry_sun-like_2022` | `el-badrySunlikeStarOrbiting2022` |
| `yungelson_elusive_2024` | `yungelsonElusiveHotStripped2024` |

## Note-creation scripts

| Script / task | Hotkey (in `astro-notes` workspace) | What it does |
|---------------|-------------------------------------|--------------|
| `scripts/new-astrobite.sh` | `Ctrl+Shift+A` | Astrobites `.tex` in `astroBitesNotes/notes/`, optional bib in `sources.bib`, updates `astroBiteInput.tex` |
| `scripts/new-paper.sh` | `Ctrl+Shift+Alt+P` | Paper note under `paperNotes/<folder>/`, updates `paperIncludes.tex`; checks **`AstroNotes.bib` first**, then `sources.bib` |
| `scripts/new-paper-from-zotero.sh` | (task: **New Paper Note (from Zotero)**) | Same, but cite key + title from Zotero selection (BBT JSON-RPC at `localhost:23119`) |
| `scripts/new-glossary.sh` | `Ctrl+Shift+G` | Add `\newglossaryentry` to `subTex/Astro-glossary.tex`, then sort A–Z |
| `scripts/sort-glossary.sh` | (auto) | Sort glossary entries by key |

VS Code tasks: **New Astrobite Note**, **New Paper Note**, **New Glossary Entry**, **Sort Glossary**, **Build mainNotes (latexmk)** (`Tasks: Run Task`).

Paper task args: title, cite key, optional folder, optional DOI — empty folder/DOI are safe (wrapper omits empty flags). Default **folder** is derived from cite key (e.g. `greenUpperLimitFrequency2025` → `greenUpper`), not the full title.

**Zotero paper task:** select one item in Zotero, run **New Paper Note (from Zotero)**; optional title overrides Zotero title. Requires Zotero running with Better BibTeX.

**Paper subfiles:** each chapter is a `subfiles` child of `mainNotes.tex`. Compile one chapter alone: open its `.tex` and run **Build Paper Subfile** (or `latexmk -pdf -shell-escape` on that file) for synctex without rebuilding the whole book.

## Layout conventions

- **Astrobites:** `\chapter{Title \cite{key} \label{chap:...}}`, section “Abstract and intro”, bullet list.
- **Papers:** `\documentclass[../../mainNotes.tex]{subfiles}` wrapper; `\chapter{Title \cite{key}}`, `\section{Abstract}`, bullet list; folder defaults from cite key (override in prompt).

## Glossary (`subTex/Astro-glossary.tex`)

Loaded via `\loadglsentries{subTex/Astro-glossary}` in `mainNotes.tex`.

**New entry** (matches `glossaryEntry` snippet):

```latex
\newglossaryentry{key}{
name={Display Name},
description={...}
}
```

- **Task / `Ctrl+Shift+G`:** prompts for key (optional), name, description. Use `\\` in description for line breaks.
- **Snippet:** `glossaryEntry` in workspace or global `Snippets.code-snippets`.
- **In notes:** `\gls{key}`.

**Auto-sort A–Z by key** runs when:

1. After **New Glossary Entry** (always)
2. Manually: task **Sort Glossary** or `python3 scripts/sort-glossary.py`

LaTeX Workshop uses **global user settings** (no workspace override). Build recipe should be **latexmk (pdf)** (`-pdf -shell-escape`) for tikz externalization and biblatex.

Prefix **acronyms** with `ac:` and **observatories** with `obs:` (e.g. `ac:GW`, `ac:TESS`, `obs:Pan-STARRS`). Full terms stay unprefixed (`chandrasekhar-limit`, `kilonova`).

## Keybindings files

- `~/.config/Code/User/keybindings.json`
- `~/.config/Cursor/User/keybindings.json`

Do not bind both Astrobites and papers to the same key.

Keybinding `when` clause uses `resourcePath =~ /astro-notes/` (not `workspaceFolderBasename`) so shortcuts work when any file under the repo is open, even if the workspace root is a parent folder.

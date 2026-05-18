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
| `scripts/new-paper.sh` | `Ctrl+Shift+Alt+P` | Paper note under `paperNotes/<folder>/`, updates `paperNotes.tex`; checks **`AstroNotes.bib` first**, then `sources.bib` |

VS Code tasks: **New Astrobite Note**, **New Paper Note** (`Tasks: Run Task`).

Paper task args: title, cite key, optional folder, optional DOI — empty folder/DOI are safe (wrapper omits empty flags).

## Layout conventions

- **Astrobites:** `\chapter{Title \cite{key} \label{chap:...}}`, section “Abstract and intro”, bullet list.
- **Papers:** `\chapter{Title \cite{key}}`, `\section{Abstract}`, bullet list; folder defaults from title (camelCase, small words lowercased).

## Keybindings files

- `~/.config/Code/User/keybindings.json`
- `~/.config/Cursor/User/keybindings.json`

Do not bind both Astrobites and papers to the same key.

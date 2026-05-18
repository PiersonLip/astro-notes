#!/usr/bin/env bash
# Compile one paper chapter standalone (subfiles + synctex). Usage:
#   build-paper-subfile.sh paperNotes/greenUpper/greenUpperNotes.tex
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
tex_rel="${1:?path to paper .tex under paperNotes/}"
tex_dir="$(dirname "$tex_rel")"
work="$ROOT/$tex_dir"
shopt -s nullglob
cleanup() {
  for link in "$work"/sources.bib "$work"/AstroNotes.bib; do
    [[ -L "$link" ]] && rm -f "$link"
  done
}
trap cleanup EXIT
cd "$work"
ln -sf ../../sources.bib sources.bib
ln -sf ../../AstroNotes.bib AstroNotes.bib
exec latexmk -pdf -shell-escape -interaction=nonstopmode "$(basename "$tex_rel")"

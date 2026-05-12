#!/usr/bin/env bash
# build.sh — wraps xelatex (two passes + optional bibtex + optional third pass)
# and emits a structured build_log.md.
#
# Usage:
#   bash auto-mm-writing/assets/build.sh <run_slug>
#
# Assumes paper sources live at runs/<run_slug>/stage3_writing/paper/.
# Writes the log to runs/<run_slug>/stage3_writing/build_log.md.

set -uo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <run_slug>" >&2
    exit 2
fi

SLUG="$1"
PAPER="runs/$SLUG/stage3_writing/paper"
LOG="runs/$SLUG/stage3_writing/build_log.md"

if [[ ! -d "$PAPER" ]]; then
    echo "build.sh: paper dir not found: $PAPER" >&2
    exit 2
fi

TS=$(date -u +%FT%TZ)
{
    echo "# Build log — $TS"
    echo ""
    echo "Paper dir: $PAPER"
    echo "xelatex: $(xelatex --version 2>/dev/null | head -1)"
    echo ""
} > "$LOG"

run_pass() {
    local label="$1"
    {
        echo ""
        echo "## $label"
        echo ''
        echo '```'
    } >> "$LOG"
    ( cd "$PAPER" && xelatex -interaction=nonstopmode -halt-on-error main.tex ) 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    echo '```' >> "$LOG"
    return $rc
}

run_bibtex() {
    {
        echo ""
        echo "## Bibtex"
        echo ''
        echo '```'
    } >> "$LOG"
    ( cd "$PAPER" && bibtex main ) 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    echo '```' >> "$LOG"
    return $rc
}

run_pass "Pass 1" || true

if ls "$PAPER"/*.bib >/dev/null 2>&1; then
    run_bibtex || true
fi

run_pass "Pass 2" || true

# Third pass if cleveref still complains
if grep -q "Label(s) may have changed" "$LOG"; then
    run_pass "Pass 3 (label fixup)" || true
fi

# Warning summary
{
    echo ""
    echo "## Warning summary"
    echo "- Fatal errors:        $(grep -c '^! ' "$LOG")"
    echo "- Undef citations:     $(grep -c 'Citation .* undefined' "$LOG")"
    echo "- Undef references:    $(grep -c 'Reference .* undefined' "$LOG")"
    echo "- Overfull hboxes:     $(grep -c 'Overfull' "$LOG")"
    echo "- Underfull hboxes:    $(grep -c 'Underfull' "$LOG")"
    echo "- Package warnings:    $(grep -c 'Package .* Warning:' "$LOG")"
} >> "$LOG"

# Gate decision
FATAL=$(grep -c '^! ' "$LOG")
UNDEF_CITE=$(grep -c 'Citation .* undefined' "$LOG")
UNDEF_REF=$(grep -c 'Reference .* undefined' "$LOG")

if [[ "$FATAL" -gt 0 || "$UNDEF_CITE" -gt 0 || "$UNDEF_REF" -gt 0 ]]; then
    echo "" >> "$LOG"
    echo "**Verdict: FAILED** — fix fatal errors and undefined refs/citations before proceeding." >> "$LOG"
    exit 1
fi

if [[ ! -f "$PAPER/main.pdf" ]]; then
    echo "" >> "$LOG"
    echo "**Verdict: FAILED** — main.pdf was not produced." >> "$LOG"
    exit 1
fi

PAGES=$(python3 -c "import PyPDF2; print(len(PyPDF2.PdfReader('$PAPER/main.pdf').pages))" 2>/dev/null || echo "?")
echo "" >> "$LOG"
echo "**Verdict: ok** — pages=$PAGES" >> "$LOG"
exit 0

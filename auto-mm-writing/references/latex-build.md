# LaTeX build — xelatex protocol and warning triage

The writing stage compiles with xelatex (twice) and parses the log. This file is the protocol.

## Why xelatex

- Native UTF-8 (no `\usepackage[utf8]{inputenc}` ritual).
- Native CJK via `\usepackage{xeCJK}` for CUMCM papers.
- Modern font handling (`\setmainfont{...}`).
- Compatible with `easymcm2.sty`.

Don't use `pdflatex` — it's fragile with CJK and Unicode math symbols.
Don't use `latexmk` from the skill — we want explicit two-pass control.

## Build commands

```bash
cd runs/<slug>/stage3_writing/paper

# First pass — generates aux/toc/cleveref refs
xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tee ../build_log_pass1.txt

# bibtex if .bib changed (or biber, depending on .sty)
# easymcm2 uses bibtex
bibtex main 2>&1 | tee ../bibtex_log.txt

# Second pass — resolves refs and bib
xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tee ../build_log_pass2.txt

# Third pass if cleveref says "Label may have changed"
if grep -q "Label(s) may have changed" ../build_log_pass2.txt; then
  xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tee ../build_log_pass3.txt
fi
```

The skill writes `build_log.md` summarizing the runs, total warnings by category, total errors, final page count.

## Warning triage

After the last pass, grep the log for blocking and non-blocking issues:

```bash
LOG=../build_log_pass2.txt

# Blocking — must fix
grep -E '^! ' $LOG          # LaTeX errors
grep -E 'Citation .* undefined' $LOG
grep -E 'Reference .* undefined' $LOG
grep -E 'No file .* found' $LOG       # missing input file

# Non-blocking — fix when time permits
grep -E 'Overfull \\hbox' $LOG        # text running into margin
grep -E 'Underfull \\hbox' $LOG       # less-bad spacing
grep -E 'LaTeX Warning: Marginpar on page' $LOG
grep -E 'Package .* Warning:' $LOG
```

### Blocking → escalate to user if not fixable

If a citation is undefined and the bibkey isn't in `references.bib`:
- Add the entry (if a real source).
- Or remove the `\cite{}` from the body.
- Don't ship with an undefined citation — it renders as `[?]`.

If a reference is undefined and the `\label{}` doesn't exist:
- Add the label at the intended target.
- Or remove the `\ref{}` from the body and rephrase.

If a file is not found:
- Check the file path (case-sensitive on Linux, case-insensitive on macOS — the contest server likely Linux).
- Check the include path (`\graphicspath{}` etc.).

### Non-blocking → log but proceed

Overfull/underfull boxes are common in tables and long URLs. Address the worst ones (>10pt overfull); ignore the rest.

Package warnings vary by package. Most are informational. Read once, judge.

## Common errors and fixes

| Error | Fix |
|---|---|
| `! LaTeX Error: File 'easymcm2.sty' not found` | The .sty file is in the same dir as main.tex but xelatex's search path missed it. Run xelatex with TEXINPUTS=. or copy the .sty to the build directory. |
| `! Package fontspec Error: The font "Source Han Sans" cannot be found` | Install the font, or pick a different one in `chinese_friendly()` of `figure_style.py`. |
| `! Undefined control sequence \Cref` | `\usepackage{cleveref}` missing. Add to preamble. |
| `! Missing $ inserted` | A math character outside math mode (often `_` in normal text). Escape with `\_`. |
| `Overfull \hbox in paragraph at line N` | Reword the offending line, or add `\sloppy` locally. |
| `! pdfTeX warning: pdflatex: arithmetic: number too big` | Usually an image with extreme dimensions. Resize. |
| `Citation 'foo' on page X undefined` | Add `foo` to `references.bib` or remove `\cite{foo}`. |
| `Reference 'fig:bar' on page X undefined` | Add `\label{fig:bar}` at the target, or remove `\ref{fig:bar}`. |
| `! Argument of \@xfloat has an extra }` | A figure environment is mismatched. Check braces. |

## Building inside a CI-like sandbox

The skill's helper script (assets/build.sh) wraps the build commands and emits a structured `build_log.md`:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../paper" || exit 1
echo "# Build log — $(date -u +%FT%TZ)" > ../build_log.md
echo "" >> ../build_log.md

run_pass() {
    echo "## Pass $1" >> ../build_log.md
    echo '```' >> ../build_log.md
    xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tee -a ../build_log.md
    echo '```' >> ../build_log.md
}

run_pass 1
if ls *.bib >/dev/null 2>&1; then
    echo "## Bibtex" >> ../build_log.md
    bibtex main 2>&1 | tee -a ../build_log.md
fi
run_pass 2

# Warning summary
echo "## Warning summary" >> ../build_log.md
{
    echo "- Errors:           $(grep -c '^! ' ../build_log.md)"
    echo "- Undef citations:  $(grep -c 'Citation .* undefined' ../build_log.md)"
    echo "- Undef references: $(grep -c 'Reference .* undefined' ../build_log.md)"
    echo "- Overfull hboxes:  $(grep -c 'Overfull' ../build_log.md)"
    echo "- Underfull hboxes: $(grep -c 'Underfull' ../build_log.md)"
} >> ../build_log.md
```

The orchestrator's gate parses the "Warning summary" line and blocks the ship if errors or undef refs > 0.

## Output PDF verification

After the build:

```bash
# Page count check
python3 -c "
import PyPDF2
r = PyPDF2.PdfReader('main.pdf')
print(f'pages={len(r.pages)}')
print(f'metadata={dict(r.metadata)}')
"

# File size check
ls -lh main.pdf

# Text extraction sanity check
python3 -c "
from pdfminer.high_level import extract_text
t = extract_text('main.pdf')
print(f'chars={len(t)} first200={t[:200]!r}')
"
```

If the PDF has 0 pages or 0 chars extracted, the build silently failed — escalate.

If the PDF has the wrong page count vs the contest's max — escalate to user with options to trim or extend the appendix.

## Reproducibility

The build is reproducible if:
- The `.tex` sources are unchanged.
- The image files are unchanged.
- The `references.bib` is unchanged.
- The TeX Live version is recorded in `build_log.md` (run `xelatex --version`).

A reproducible build is required for the orchestrator's integrity gate to issue the same PDF on a clean re-invocation.

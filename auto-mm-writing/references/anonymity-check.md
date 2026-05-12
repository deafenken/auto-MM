# Anonymity check — Rule 2 enforcement

The submitted paper must contain zero personally-identifying information. One leaked username is enough for disqualification. This file is the protocol; the writing stage runs the scan, writes `anonymity_report.md`, and blocks `submit.zip` if any hit is found.

## What gets scanned

1. **PDF metadata** — `/Author`, `/Creator`, `/Producer`, `/Title`, `/Subject`, `/Keywords`, `/Trapped`, XMP packets.
2. **PDF body text** — extracted via pdfminer; greppable Unicode.
3. **PDF object streams** — names of fonts (rarely leaks names, but worth checking), embedded files.
4. **Source LaTeX files** — `*.tex`, `*.sty`, `*.cls`, `*.bib`.
5. **Code listings embedded in the paper** — file paths inside `\begin{lstlisting}...\end{lstlisting}` blocks.

## Forbidden pattern categories

### Category A: hard identifiers (always block)

- Author names — both English and Chinese.
- School names — university, college, high school.
- Advisor names + titles ("Prof.", "Dr.", "教授", "副教授", "讲师", "导师", "指导老师", "指导教师").
- Team names that contain the school or city.
- Country / region in a way that identifies team (cautious: a "we are from XYZ University" is a hit).

### Category B: indirect identifiers (block on match)

- OS usernames in file paths: `/Users/<name>`, `/Volumes/<name>`, `/home/<name>`, `C:\\Users\\<name>`.
- Git remote URLs: `github.com/<user>/`, `gitee.com/<user>/`.
- Email addresses with personal handles.
- Conference / team submission IDs that map to identity.
- Macros that print author names (`\author{...}` in LaTeX should be empty or generic).

### Category C: metadata leaks (block on match)

- PDF `/Author` field non-empty.
- `\hypersetup{pdfauthor=...}` non-empty in LaTeX.
- `\title{}` or `\subtitle{}` containing identifiers (rare but check).

### Category D: AI report identifiers (MCM-specific)

The AI report must declare LLM usage but **not the author**. If the AI report mentions "Author X used GPT-4 to...", that's a hit. Use "we" or "the team."

## Scan implementation

```python
# scripts/anonymity_scan.py
import re, json, sys
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

# Patterns — extend per contest profile
PATTERNS_EN = [
    r"\bUniversity of [A-Z][A-Za-z]+\b",
    r"\b[A-Z][a-z]+ University\b",
    r"\bProf\.?\s+[A-Z][a-z]+\b",
    r"\bDr\.?\s+[A-Z][a-z]+\b",
    r"/Users/[A-Za-z0-9_]+",
    r"/Volumes/[A-Za-z0-9_]+",
    r"github\.com/[A-Za-z0-9_-]+/",
    r"gitee\.com/[A-Za-z0-9_-]+/",
]

PATTERNS_ZH = [
    r"姓名[:：]?\s*\S+",
    r"学校[:：]?\s*\S+",
    r"学院[:：]?\s*\S+",
    r"指导老师[:：]?\s*\S+",
    r"指导教师[:：]?\s*\S+",
    r"导师[:：]?\s*\S+",
    r"[一-鿿]{2,4}大学",
    r"[一-鿿]{2,4}学院",
    r"教授",
    r"副教授",
]

def scan_pdf(pdf_path, lang):
    p = Path(pdf_path)
    hits = []

    # Metadata
    with p.open("rb") as f:
        doc = PDFDocument(PDFParser(f))
        meta = doc.info[0] if doc.info else {}
        for key in (b"Author", b"Creator", b"Producer", b"Title", b"Subject", b"Keywords"):
            val = meta.get(key, b"")
            if isinstance(val, bytes):
                val = val.decode(errors="ignore")
            if val and val.strip():
                hits.append({"kind": "metadata", "field": key.decode(), "value": val})

    # Body text
    text = extract_text(str(p))
    patterns = PATTERNS_EN + PATTERNS_ZH if lang == "both" else (PATTERNS_EN if lang == "en" else PATTERNS_ZH)
    for pat in patterns:
        for m in re.finditer(pat, text):
            hits.append({"kind": "body", "pattern": pat, "match": m.group(0)[:120]})

    return hits

def scan_sources(paper_dir, lang):
    hits = []
    patterns = PATTERNS_EN + PATTERNS_ZH if lang == "both" else (PATTERNS_EN if lang == "en" else PATTERNS_ZH)
    for f in Path(paper_dir).rglob("*"):
        if f.suffix.lower() not in {".tex", ".sty", ".cls", ".bib"}:
            continue
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        for pat in patterns:
            for m in re.finditer(pat, text):
                line_no = text[: m.start()].count("\n") + 1
                hits.append({"kind": "source", "file": str(f), "line": line_no,
                             "pattern": pat, "match": m.group(0)[:120]})
    return hits

if __name__ == "__main__":
    pdf, paper_dir, lang, out = sys.argv[1:5]
    report = {
        "pdf": pdf,
        "lang": lang,
        "metadata_and_body_hits": scan_pdf(pdf, lang),
        "source_hits": scan_sources(paper_dir, lang),
    }
    Path(out).write_text(json.dumps(report, ensure_ascii=False, indent=2))
    n = len(report["metadata_and_body_hits"]) + len(report["source_hits"])
    print(f"anonymity_scan: {n} hits → {out}")
    sys.exit(1 if n > 0 else 0)
```

The skill writes this script to `assets/anonymity_scan.py` and runs it after every build.

## Per-contest pattern customization

`run.yaml.contest.family` selects the pattern set:

- MCM / English → `PATTERNS_EN` only.
- CUMCM / Chinese → `PATTERNS_ZH` only.
- 其他 → ask user; default to both.

The user can extend patterns by writing `runs/<slug>/inputs/anonymity_extra.json`:

```json
[
  {"pattern": "AcmeUniversity", "reason": "school not in default list"},
  {"pattern": "Zhang Wei", "reason": "team member name"}
]
```

The scan loads this file unconditionally and appends its entries.

## False positives

Some matches are unavoidable:

- "University" mentioned in a citation (e.g. "[3] J. Smith, University of X press, 2018"). This is fine in `references.bib` — cited authors are NOT anonymized.
- "Professor" used in a paper about academia (e.g. "the professor's grading rubric"). Context-sensitive.

The skill's response: when a hit is in `references.bib` or a contextually-appropriate location, allow the user to whitelist it in `runs/<slug>/anonymity_whitelist.txt` with a one-line reason per entry. The whitelist is consulted before declaring a hit.

## Pre-build prevention

Better than scanning is preventing leakage in the first place:

- Set `\hypersetup{pdfauthor={}, pdftitle={Your Title Here}, pdfsubject={}, pdfcreator={}}` in `main.tex`.
- Strip OS username from code listings: use a path-rewriting helper that replaces `/Users/<name>` with `~`.
- Configure git not to embed remote URLs in commit hashes referenced from the paper.
- Use a generic author macro: `\newcommand{\authoredby}{Team \theControlNumber}`.

The writing stage runs these substitutions at copy-into-paper time so the user doesn't have to remember.

## On a positive hit

```markdown
# anonymity_report.md

## SCAN FAILED — 2 hits
Generated at <ts>. submit.zip is BLOCKED until resolved.

### Hit 1 — body text
- Pattern: `/Users/[A-Za-z0-9_]+`
- Match: `/Users/candyman`
- Location: extracted from paper PDF body (likely a code listing path).
- Likely fix: the code listing in `part_4_Appendix.tex` line 87 has a hardcoded path. Replace with `~/` or strip the absolute prefix.

### Hit 2 — metadata
- Field: `/Author`
- Value: "Marguerite Miller"
- Likely fix: add `\hypersetup{pdfauthor={}}` to main.tex preamble.
```

The user fixes, then re-invokes `auto-mm-writing --re-anonymize`. The skill rebuilds and re-scans. The cycle continues until 0 hits.

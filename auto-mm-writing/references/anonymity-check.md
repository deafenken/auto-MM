# Anonymity check — Rule 2 enforcement

The submitted paper must contain zero personally-identifying information. One leaked username is enough for disqualification. This file is the protocol; the writing stage runs the scan, writes `anonymity_report.json`, and blocks `submit.zip` if any hit is found.

## What gets scanned

1. **PDF metadata — selected fields only**: `/Author`, `/Title`, `/Subject`, `/Keywords`. `/Producer` and `/Creator` are intentionally **excluded** because xelatex always writes engine-version strings there — those are not PII.
2. **PDF body text** — extracted via `pdfminer.six`.
3. **Paper sources** — only `*.tex` and `*.bib` files. `*.sty` and `*.cls` are **NOT scanned** because they are upstream template/style files and often contain maintainer GitHub URLs that are not the team's identity.
4. **Code listings embedded in the paper PDF** are scanned as part of the PDF body text in (2).

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

The actual scanner is bundled at `auto-mm-writing/assets/anonymity_scan.py` (see that file for the canonical source). It implements three discrimination rules:

1. **Metadata**: only `Author`, `Title`, `Subject`, `Keywords` are scanned. `Producer` and `Creator` are excluded because normal `xelatex` PDFs always populate them with version strings, which are not PII.

2. **PDF body and `.tex` / `.bib` sources** are scanned with `PATTERNS_EN` + `PATTERNS_ZH`. `.sty` and `.cls` files are **NOT scanned** — they are upstream template/style files, often contain maintainer GitHub URLs and contacts that are not the team's identity.

3. **Per-contest pattern set** is selected by `run.yaml.contest.family`: MCM → English only, CUMCM → 中文 only, other → both. Patterns are extensible via `runs/<slug>/inputs/anonymity_extra.json`.

Pattern set summary (full list in the bundled script):

| Pattern | Matches |
|---|---|
| `\bUniversity of [A-Z][A-Za-z]+\b` | "University of Foo" |
| `\b[A-Z][a-z]+ University\b` | "Foo University" |
| `\bProf\.?\s+[A-Z][a-z]+\b` | "Prof. Foo", "Prof Foo" |
| `/Users/[A-Za-z0-9_]+`, `/Volumes/[…]`, `/home/[…]` | OS-username file paths |
| `github\.com/[A-Za-z0-9_-]+/`, `gitee\.com/[…]/` | personal git remotes |
| `姓名[:：]?\s*\S+`, `学校[:：]?\s*\S+`, etc. | 中文 metadata leaks |
| `[一-鿿]{2,4}大学`, `[一-鿿]{2,4}学院` | 中文 school names |

The scanner respects `runs/<slug>/anonymity_whitelist.txt` (one regex per line + reason) — entries listed there are skipped. Whitelist is consulted **before** declaring a hit.

The scanner exits non-zero on any hit; the orchestrator's writing-stage gate blocks `submit.zip` accordingly.

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
# anonymity_report.json (rendered as markdown for review)

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

---
name: auto-mm-writing
description: >-
  Stage 3 of auto-mm. Copies the contest template (MCM EasyMCM2 or
  CUMCM 高教社) into stage3_writing/paper/, symlinks figures from
  stage2_solving/figures/, then walks the section files in order
  (problem restatement, assumptions, notation, data, model, algorithm,
  results, sensitivity, strengths/weaknesses, AI report). Iterates the
  abstract three times — every pass must keep every hard number from
  stage2_solving/validation.md. Builds with xelatex twice, runs the
  anonymity scan (Rule 2), checks the section checklist, scans for
  orphan figures (Rule 8), packages submit.zip with macOS metadata
  filtered out. Refuses to ship if anonymity or the integrity gate fail.
---

# Stage 3 — Writing

The artifact stage. Everything before this exists to feed this stage. Time discipline matters most here because writing is the most unrecoverable — code can be re-run in a pinch, but a rushed paper can't be re-typeset.

## Trigger

- Delegated by the orchestrator after `stage2_solving/hand_off.md` is written.
- Can be invoked directly: `auto-mm-writing <run_slug>` to rebuild after a code/figure change, or `--re-anonymize` to re-run the anonymity scan.

## Inputs

- `runs/<run_slug>/run.yaml` — contest family, language, team control number, deadline.
- `runs/<run_slug>/stage1_modeling/{model.md, assumptions.md, notation.md, candidates.md, literature.md}`
- `runs/<run_slug>/stage2_solving/{validation.md, sensitivity.md, figures/, leaderboard.csv}`
- `runs/<run_slug>/stage0_triage/{problem_choice.md, contest_brief.md}` — for problem restatement and current-year contest facts.
- `auto-mm-writing/assets/{mcm-template,cumcm-template}/` — the template package.

## Outputs (the contract)

```
runs/<run_slug>/stage3_writing/
├── paper/
│   ├── main.tex                  # from template, edited
│   ├── easymcm2.sty | (cumcm sty)
│   ├── part_*.tex                # filled per template structure
│   ├── img/ → ../../stage2_solving/figures/   # symlink
│   ├── references.bib            # built from stage1_modeling/literature.md
│   └── main.pdf                  # build output
├── abstract_draft.md             # iterated abstracts (history kept)
├── section_checklist.md          # which sections present / missing
├── build_log.md                  # xelatex stdout + warning grep
├── anonymity_report.md           # PDF text + metadata scan results
├── submission/
│   ├── <submission_root>/        # the flat tree to be zipped
│   └── submit.zip
└── hand_off.md
```

## Workflow

### 1. Copy the template

Based on `run.yaml.contest.family`. Uses plain `grep`/`awk` — no `yq` dependency.

```bash
SLUG="<run_slug>"
RUN="runs/$SLUG"

# extract contest.family from run.yaml without yq
FAMILY=$(awk '/^contest:/{p=1;next} p && /^[^[:space:]]/{p=0} p && /family:/{print $2; exit}' "$RUN/run.yaml")

case "$FAMILY" in
  mcm|MCM)   TPL=auto-mm-writing/assets/mcm-template ;;
  cumcm|CUMCM) TPL=auto-mm-writing/assets/cumcm-template ;;
  *) echo "Unknown contest family: $FAMILY — see auto-mm/references/contest-types.md"; exit 1 ;;
esac

# For CUMCM: refuse to proceed if the template is only the placeholder
if [[ "$FAMILY" =~ ^(cumcm|CUMCM)$ ]]; then
    if ! ls "$TPL"/*.tex >/dev/null 2>&1; then
        echo "ESCALATE: cumcm-template/ contains no .tex file. Drop the year's official template in and re-invoke." >&2
        exit 1
    fi
fi

mkdir -p "$RUN/stage3_writing/paper"
cp -r "$TPL/"* "$RUN/stage3_writing/paper/"
# remove the README we ship next to the template files (it's documentation, not a paper source)
rm -f "$RUN/stage3_writing/paper/README.md"
```

If `cumcm-template/` contains only the placeholder README, escalate per `auto-mm/references/escalation-policy.md` — ask the user to drop the year's template in.

### 2. Symlink figures

```bash
cd runs/$SLUG/stage3_writing/paper
rm -rf img
ln -s ../../stage2_solving/figures img
```

If the user's template uses a different folder (e.g. `figures/`), adjust the symlink target.

### 3. Configure `main.tex`

For MCM:

```latex
\usepackage[<team_control_number>]{easymcm2}
\problem{<X>}                  % the chosen problem letter
\title{Your Title Here}        % rewrite for this run
```

Pull the team control number from `run.yaml.team.control_number`. Refuse if it's null and family is MCM (it's required).

For CUMCM: configure 报名号 in the spot the template indicates.

### 4. Fill the sections

Walk the template's section files in order. For each, write content from the upstream stage's artifacts:

| Section | Source | Notes |
|---|---|---|
| Background / 背景 | `stage0_triage/contest_brief.md` + paraphrase from problem PDF | A few paragraphs, not the whole problem statement. |
| Problem restatement / 问题重述 | `inputs/problems/<X>.pdf` paraphrase | List each sub-question with a one-sentence brief. |
| Our work summary / 我们的工作 | one paragraph per sub-question with what we did + headline result | Reference `validation.md` numbers. |
| Assumptions / 模型假设 | `stage1_modeling/assumptions.md` verbatim | Numbered, with Why + If-wrong lines. |
| Notation / 符号说明 | `stage1_modeling/notation.md` | One table, full. |
| Data processing / 数据预处理 | `stage0_triage/data_recon.md` + how anomalies were handled | Include a data-flow figure if available. |
| Model / 模型建立 | `stage1_modeling/model.md` | Constraint groups separated, derivations included. |
| Algorithm / 算法设计 | prose summary of `stage2_solving/pipeline.py` | Justify each algorithmic component (Rule 5). |
| Results / 结果分析 | `stage2_solving/validation.md` + result tables | Reference every figure shipped. |
| Sensitivity / 灵敏度 | `stage2_solving/sensitivity.md` | One subsection per `to-sweep` parameter. |
| Strengths / Weaknesses | `stage1_modeling/model.md` "Known limitations" + reflection on validation | Concise. |
| References / 参考文献 | `stage1_modeling/literature.md` → `references.bib` | Only verified entries. |
| Appendix / 附录 | code listings, long tables | Reference from body. |
| AI Report (MCM only) | document LLM usage per COMAP 2024 rules | Mandatory; separate from main paper page count. |

Every section file ends with a one-line comment `% filled-by-auto-mm-writing: <ts>` for traceability.

### 5. Iterate the abstract

The abstract is the most-read part of the paper. Iterate three times:

**Pass 1** — structural draft:
- One sentence: problem type + overall approach.
- One paragraph per sub-question with model, algorithm, headline number.
- One paragraph of management/policy insight.

**Pass 2** — number tightening:
- Replace every "good results" with the actual number.
- Verify every number is sourced from `validation.md` (greppable check).
- Replace passive voice with active.

**Pass 3** — length and tone:
- Compress to one page (LaTeX renders to one page in the template).
- Cut hedge words ("we attempt to", "we tried to").
- Keep the keyword line.

Save each pass to `abstract_draft.md` so revisions are traceable. The final pass copies into the template's `\begin{abstract}...\end{abstract}` block.

Per Rule 9: an abstract that doesn't contain ≥5 hard numbers blocks the integrity gate.

### 6. Build with xelatex (twice)

```bash
cd runs/$SLUG/stage3_writing/paper
xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tee ../build_log.md
xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tee -a ../build_log.md
```

Then scan the log:

```bash
grep -E 'Overfull|Underfull|Undefined control sequence|Citation .* undefined|Reference .* undefined|Label\(s\) may have changed|LaTeX Warning' ../build_log.md > /tmp/warnings.txt
```

Address every warning:
- "Citation undefined" → fix `references.bib` or add the `\cite{}`.
- "Reference undefined" → fix `\ref{}` target.
- "Overfull \hbox" → reword the offending line; in tables, use `\\` or shorter cell content.
- "Label may have changed" → run xelatex one more time.

The orchestrator's gate checks that `main.pdf` exists and the log has zero undefined citations/references. Overfull boxes are flagged but not blocking (in moderation).

### 7. Section checklist

`section_checklist.md`:

```markdown
| Section | Required | Present | Source |
|---|---|---|---|
| Abstract | yes | ✅ | main.tex |
| Problem restatement | yes | ✅ | part_1_pre.tex |
| Assumptions (numbered) | yes | ✅ | part_1_pre.tex |
| Notation | yes | ✅ | part_1_pre.tex |
| ... | | | |
```

Any "Required: yes, Present: no" row blocks the hand-off.

### 8. Anonymity scan (mandatory; Rule 2)

Run `auto-mm-writing/assets/anonymity_scan.py` (full spec in `references/anonymity-check.md`). What it actually checks:

- **PDF metadata**: `/Author`, `/Title`, `/Subject`, `/Keywords` (Producer / Creator are excluded — xelatex always writes engine strings there, not PII).
- **PDF body text** + **`.tex` / `.bib` source** for the patterns below. `.sty` and `.cls` files are NOT scanned (template/style files; not the team's identity).
  - MCM (English): `University of X`, `X University`, `Prof. X`, `Dr. X` (titled-name forms — not bare given names).
  - CUMCM (中文): `姓名:…`, `学校:…`, `学院:…`, `指导老师:…`, `指导教师:…`, `X大学`, `X学院`, `教授`/`副教授`/`讲师`.
- **File paths**: `/Users/<name>`, `/Volumes/<name>`, `/home/<name>`, `C:\Users\<name>` — these leak when code listings include hardcoded paths.
- **Git remotes**: `github.com/<user>/<repo>`, `gitee.com/<user>/<repo>` — these leak when code listings include `git clone …` lines.

Any hit → the scanner returns exit code 1, writes `anonymity_report.json` with the match + file:line, and **blocks the submission**. Escalate to the user.

### 9. Submission package

After all gates pass. All paths absolute from repo root — do NOT `cd` partway through.

```bash
# Always run from repo root (where the runs/ directory lives)
SLUG="<run_slug>"
RUN="runs/$SLUG"
ROOT_NAME="<root_name>"             # e.g. team control number for MCM, 报名号 for CUMCM
SUBMIT="$RUN/stage3_writing/submission"
ROOT="$SUBMIT/$ROOT_NAME"

mkdir -p "$ROOT"

# paper PDF
cp "$RUN/stage3_writing/paper/main.pdf" "$ROOT/$ROOT_NAME.pdf"

# AI report (MCM 2024+) — typically already inside main.pdf via part_4_Appendix.tex,
# so this is only needed if the contest portal asks for it separately
# cp "$RUN/stage3_writing/paper/ai-report.pdf" "$ROOT/ai-report.pdf"

# code
mkdir -p "$ROOT/code"
cp "$RUN/stage2_solving/pipeline.py" "$ROOT/code/"
cp -r "$RUN/stage2_solving/src" "$ROOT/code/"
find "$ROOT/code" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

# supporting material per contest convention
mkdir -p "$ROOT/supporting/figures-raw" "$ROOT/supporting/data-derived"
cp "$RUN/stage2_solving/figures/"*.pdf "$ROOT/supporting/figures-raw/" 2>/dev/null || true

# zip — note: the zip command runs from inside $SUBMIT so paths in the
# archive are relative to $ROOT_NAME, not to the repo root.
( cd "$SUBMIT" && zip -r -X submit.zip "$ROOT_NAME" \
    -x "*/._*" "*/.DS_Store" "*/~$*" \
       "*/__pycache__/*" "*/.git/*" "*/.gitignore" \
       "*/*.pyc" "*/*.pyo" \
       "*/*.aux" "*/*.log" "*/*.out" "*/*.toc" "*/main.synctex.gz" )

# verify
unzip -l "$SUBMIT/submit.zip" | head -50
```

Run a final post-zip check:

```bash
# Decompress to a temp directory and verify no forbidden files leaked through
TMP=$(mktemp -d)
unzip -q "$SUBMIT/submit.zip" -d "$TMP"
find "$TMP" \( -name "._*" -o -name ".DS_Store" -o -name "__pycache__" \) -print
ls -lR "$TMP" | head -30
rm -rf "$TMP"
```

If the zip contains forbidden patterns (`.DS_Store`, `._*`) → re-zip with the filter; the macOS `zip -X` flag normally handles AppleDouble, but verify.

### 10. Write `hand_off.md`

```markdown
# Stage 3 → Done hand-off

## What I did
- Copied the <family> template into paper/.
- Wrote sections from upstream artifacts. Three abstract passes.
- Built with xelatex twice. Zero undefined refs/citations.
- Anonymity scan: passed (no hits in metadata or body text).
- Section checklist: all required sections present.
- Built submit.zip at <path>. Size: <KB>. Contents: <N files>.

## What's true now
- Paper: <pages> pages.
- Headline numbers in abstract: <list>.
- Hours remaining: <H>.
- Lockdown mode: <yes/no>.

## What you should do next
Hand the user submit.zip and main.pdf. They review and submit through
the contest portal. If they request a revision, re-invoke with the
specific change (e.g. `auto-mm-writing --revise abstract` or
`--revise section:results`).
```

Append `progress.jsonl` events `paper_built` and `submission_packaged`. Exit.

## Idempotency

- Re-running with no changes to inputs is a no-op (skip xelatex if `main.pdf` newer than all `.tex`).
- The anonymity scan is always re-run — it's cheap and catches regressions from a re-built PDF.
- `submit.zip` is rebuilt only if its inputs (PDF + code) have newer timestamps.

## Failure modes

| Symptom | Action |
|---|---|
| Template missing (CUMCM placeholder) | Escalate; ask user to drop in the year's template. |
| xelatex fails on first run | Read the error. Most often: missing package (install via tlmgr), encoding issue (UTF-8 BOM), CJK font missing. |
| Anonymity hit | Block submission. Write `anonymity_report.md`. Escalate. |
| Orphan figure label | Add `\Cref{fig:...}` reference or remove the figure. |
| Abstract over one page | Iterate Pass 3 again with stricter cuts. |
| AI report missing (MCM 2024+) | Block; write a draft from `progress.jsonl` + `validation.md`. |
| Code listing too long for appendix | Move to supporting material zip; reference in appendix. |
| Final zip too large | Drop intermediate experiment artifacts; keep only main + key supporting. |

## When to load which reference

| File | Load when |
|---|---|
| `references/abstract-writing.md` | Step 5 — every pass of the abstract |
| `references/section-checklist.md` | Step 7 — building the checklist; the table varies by contest |
| `references/anonymity-check.md` | Step 8 — running the scan |
| `references/latex-build.md` | Step 6 — interpreting xelatex warnings |
| `references/submission-package.md` | Step 9 — assembling the zip and the supporting material tree |
| `references/ai-report-mcm.md` | Step 4 (AI report section) — what to include for MCM since 2024 |
| `auto-mm/references/contest-types.md` | Step 1 — which template to copy + which anonymity patterns to scan |
| `auto-mm/references/integrity-rules.md` | Step 8 (Rule 2), Step 6 (Rule 8 orphan figs), Step 5 (Rule 9 abstract numbers) |

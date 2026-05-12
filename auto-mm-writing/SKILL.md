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

Based on `run.yaml.contest.family`:

```bash
SLUG=<run_slug>
FAMILY=$(yq '.contest.family' runs/$SLUG/run.yaml)

case "$FAMILY" in
  mcm|MCM) TPL=auto-mm-writing/assets/mcm-template ;;
  cumcm|CUMCM) TPL=auto-mm-writing/assets/cumcm-template ;;
  *) echo "Unknown family — see references/contest-types.md"; exit 1 ;;
esac

mkdir -p runs/$SLUG/stage3_writing/paper
cp -r $TPL/* runs/$SLUG/stage3_writing/paper/
```

If `cumcm-template/` contains only the placeholder README, escalate: ask the user to drop the year's template in.

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

Run the scan from `references/anonymity-check.md`. It checks:

- PDF metadata (`/Author`, `/Creator`, `/Producer`, `/Title`).
- PDF body text for forbidden patterns (configurable per contest):
  - MCM: common Western given names + university list + advisor titles.
  - CUMCM: 中文姓名候选, 学校列表, 学院, 指导老师, 指导教师.
- File paths leaked from code listings (`/Users/<name>`, `/Volumes/<name>`, `/home/<name>`).
- Git remote URLs in code listings.

Any hit → write `anonymity_report.md` with the match + file:line and **block the submission**. Escalate to the user.

### 9. Submission package

After all gates pass:

```bash
SUBMIT=runs/$SLUG/stage3_writing/submission
mkdir -p $SUBMIT/<root>     # root name per contest convention
cp paper/main.pdf $SUBMIT/<root>/<TeamControlNumber>.pdf
# code package
mkdir -p $SUBMIT/<root>/code
cp -r ../../stage2_solving/pipeline.py ../../stage2_solving/src $SUBMIT/<root>/code/
# supporting material per contest's rubric (figures, data, references)
...
# zip with macOS metadata filtered
cd $SUBMIT
zip -r -X submit.zip <root> -x "*/._*" "*/.DS_Store" "*/~$*" "*/__pycache__/*" "*/.git/*"
unzip -l submit.zip | head -50  # verify
```

Run a final post-zip check:

```bash
# decompress to /tmp, rebuild PDF text scan
unzip -q submit.zip -d /tmp/auto-mm-verify
ls -lR /tmp/auto-mm-verify | head
```

If the zip contains forbidden patterns (`.DS_Store`, `._*`) → re-zip with the filter; the macOS `zip -X` flag handles this but verify.

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

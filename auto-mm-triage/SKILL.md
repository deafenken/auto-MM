---
name: auto-mm-triage
description: >-
  Stage 0 of auto-mm. Indexes the problem PDFs in inputs/problems/, summarizes
  each (A/B/C/D), recons the attachment data in inputs/data/, scores every
  candidate problem against a 5-axis rubric (data sufficiency, method fit, risk,
  differentiator, team familiarity), and either recommends a single problem or
  presents a ranked shortlist for the user to lock in. Once a problem is
  committed, renames the run directory from <contest>-<year>-untriaged to
  <contest>-<year>-<problem> and writes the hand-off for the modeling stage.
  Never picks a problem the user hasn't approved — the final commitment is
  always user-driven.
---

# Stage 0 — Triage

The first analytical step after `auto-mm` collects contest metadata. Turns "we have N candidate problems" into "we are running problem X, and here's why."

## Trigger

- Delegated to by the `auto-mm` orchestrator on first invocation, after `run.yaml` and `inputs/problems/` are populated.
- Can be invoked directly: `auto-mm-triage <run_slug>` to re-score (e.g., if a new problem clarification arrives or the user wants to revisit the choice in the first 6 hours).

After Stage 1 (modeling) has committed an approach, the orchestrator **will not** re-invoke triage. Switching problems mid-run is forbidden — it is more expensive than finishing the chosen problem badly.

## Inputs

- `runs/<run_slug>/run.yaml` — contest family, year, problem set, deadline.
- `runs/<run_slug>/inputs/problems/` — one PDF/HTML per candidate problem (A.pdf, B.pdf, …).
- `runs/<run_slug>/inputs/data/` — attachment data files (optional; some problems are data-light).
- `runs/<run_slug>/inputs/notices/` — clarifications, errata posted by the organizer (optional).
- The user (interactively) — only for the lock-in confirmation in Step 5. Never for analytical judgments the agent can make itself.

## Outputs (the contract)

```
runs/<run_slug>/stage0_triage/
├── contest_brief.md           # current-year contest facts (page limit, AI report rule, etc.)
├── problems_index.md          # one-paragraph summary per candidate problem
├── data_recon.md              # what's in inputs/data/: files, row counts, fields, units, oddities
├── selection_scorecard.md     # the 5-axis rubric scored per problem
├── problem_choice.md          # CHOSEN problem + 3-paragraph rationale + lock-in checklist
└── hand_off.md
```

Exact schemas live in `auto-mm/references/state-contract.md`.

## Workflow

### 1. Confirm inputs are present

```bash
ls runs/<run_slug>/inputs/problems/
ls runs/<run_slug>/inputs/data/ 2>/dev/null
```

If `inputs/problems/` is empty → escalate per `auto-mm/references/escalation-policy.md` (`bad_input`). Ask the user to drop the problem PDFs in.

If a problem listed in `run.yaml.contest.problem_set` has no matching file → escalate. Do not silently work with a subset.

### 2. Index each problem

For every file in `inputs/problems/`:

- Read the full statement (Read tool for PDFs, WebFetch if URL).
- Extract: problem letter, title, one-sentence brief, sub-questions count, primary task type (optimization / inference / classification / forecasting / network / mixed / open-ended).
- Note any explicit data files referenced, any hard numerical constraints stated, any "must include" deliverables (e.g., a memo, a 2-page summary).

Write to `problems_index.md`:

```markdown
# Problems index — <run_slug>

## Problem A — "..."
- Type: <task type>
- Sub-questions: <N>
- Brief: <one sentence>
- Data referenced: <files / none>
- Special deliverables: <e.g. "1-page memo to the city council">
- Hard constraints stated in problem: <bulleted>

## Problem B — ...
...
```

### 3. Recon the data

For every file in `inputs/data/`:

- CSV / Excel / Parquet → row count, column count + dtypes, missingness per column (%), basic stats for numeric columns, value frequency for categoricals.
- Image directories → file count, total size, one or two example dimensions.
- Text / JSON → top-level structure, record count, key fields.
- Time series → time range, sampling frequency, gaps.

Write to `data_recon.md`. Keep under 150 lines — this file is read by every later stage. Flag anomalies (NaN spikes, encoding issues, unit ambiguity, suspicious outliers) under a `## Anomalies` section because Stage 1 must address them.

Also write a one-line summary linking each problem to the data it depends on (e.g. "Problem A: uses dataset_a.csv (12,304 rows)").

### 4. Score every problem

Use the 5-axis rubric from `references/problem-selection-rubric.md`:

| Axis | Score | Notes |
|---|---|---|
| Data sufficiency | -2..+2 | Does the data answer the question, or is heavy external collection needed? |
| Method fit | -2..+2 | Does the problem map to methods we can implement in the available hours? |
| Risk | -2..+2 | Ambiguity, edge cases, "trap" sub-questions, novel jargon? |
| Differentiator | -2..+2 | Is there room for a non-obvious technique (attention, MILP+ALNS, Bayesian update) that judges value? |
| Team familiarity | -2..+2 | Does the user have prior context in this domain? Ask if uncertain. |

Sum the axis scores. Tie-break by `risk` (lower-risk wins).

Write `selection_scorecard.md`:

```markdown
# Selection scorecard — <run_slug>

| Axis | A | B | C | D |
|---|---|---|---|---|
| Data sufficiency | +1 | -1 | +2 | -1 |
| Method fit | +1 | 0 | +2 | +1 |
| Risk | -1 | 0 | +1 | -2 |
| Differentiator | +1 | +1 | +1 | +2 |
| Team familiarity | 0 | -1 | +1 | 0 |
| **Total** | +2 | -1 | +7 | 0 |

## Reasoning per problem
### A — total +2
<short paragraphs, axis by axis>
...
```

### 5. Recommend, then ask the user to lock in

The agent **recommends**, the user **locks in**. Do not commit to a problem unilaterally.

Print:

```
Triage done. Scored 4 problems on the 5-axis rubric.

  C: +7  (recommended — data fully shipped, optimization-friendly, light ML upside)
  A: +2
  D:  0
  B: -1

Top reasons for C: <one line per axis where C scored ≥ +1>
Top risks for C:   <one line per axis where C scored ≤ -1, or "no major risks">

Reply with one of:
  "go C"       — lock in C, rename the run, hand off to modeling
  "go <letter>" — lock in another letter (the recommendation can be overridden)
  "more on <letter>" — print the full scorecard reasoning for that problem
  "discuss"     — print my full thinking, then ask again
```

Wait. Do not modify any state until the user replies. If 30 minutes pass with no reply (and we are not yet in lockdown), re-print the recommendation but still wait.

### 6. Commit and rename

Once the user replies "go X":

```bash
PROV=runs/<provisional_slug>
# atomically update run.yaml via .tmp + rename
python3 -c "
import yaml, pathlib, os
p = pathlib.Path('$PROV/run.yaml')
tmp = p.with_suffix('.yaml.tmp')
data = yaml.safe_load(p.read_text())
data['chosen_problem'] = 'X'
data['run_slug'] = f\"{data['contest']['family']}-{data['contest']['year']}-X\"
tmp.write_text(yaml.safe_dump(data, sort_keys=False))
os.replace(tmp, p)        # atomic on POSIX
"
# rename directory atomically. mv -n fails if target exists — see escalation below.
mv -n "$PROV" "runs/<contest>-<year>-X"
```

Order matters: write `run.yaml` with the new `chosen_problem`+`run_slug` FIRST, then rename the directory. If the process dies between the two, resume sees `run.yaml.chosen_problem != null` inside the still-provisional directory and re-attempts the rename idempotently.

If `mv -n` fails (target exists), escalate — the user may have a previous run with the same slug.

### 7. Write `problem_choice.md` and `hand_off.md`

`problem_choice.md` uses the template in `auto-mm/references/state-contract.md` § "stage0_triage/problem_choice.md".

`hand_off.md` follows the 3-paragraph convention:

```markdown
# Stage 0 → Stage 1 hand-off

## What I did
- Indexed <N> problems, recon'd inputs/data/, scored 5 axes, wrote problem_choice.md.
- Committed to Problem <X>. Renamed run to <new_slug>.

## What's true now
- Problem <X>: <one-sentence brief>.
- Has <N> sub-questions: <list with one-line each>.
- Data: <main files + row counts>.
- Hard constraints to respect: <bullet list referencing problem_choice.md>.
- Deadline UTC: <ts>. Hours remaining: <N>.
- Modeling budget for this stage: <H>h (from run.yaml.budget.per_stage_hours.modeling).

## What you should do next
Stage 1: decompose Problem <X> into Q1..Qk. For each, define I/O, hard/soft
constraints, and the optimization or inference target. Propose 2-4 candidate
model families with one-paragraph pros/cons each. Pick one and write the
formal model (objective, constraints, derivations) in model.md. Build the
notation table early — every formula must reference it. Pitfalls from the
華中杯 retro apply: respect the problem statement's wording verbatim
(integrity Rule 1); do NOT add an AI/ML module unless it addresses real
uncertainty (Rule 4).
```

Append `progress.jsonl` events `problems_indexed` and `problem_chosen`. Exit.

## Idempotency

If `stage0_triage/problem_choice.md` already exists when this skill runs:

- Re-run is harmless: re-read `inputs/problems/` and recompute only if any file's mtime is newer than `problem_choice.md`'s mtime.
- If `run.yaml.chosen_problem` is non-null and `problem_choice.md` exists → log `triage_skipped` and exit 0.
- A user can force re-triage via the orchestrator's `--re-triage` flag (which sets `chosen_problem: null` and removes the rename — only do this in the first 6 hours of the contest).

## Failure modes

| Symptom | Action |
|---|---|
| `inputs/problems/` empty | Escalate `bad_input`. Ask user to drop PDFs. |
| Problem PDF unreadable / OCR garbage | Escalate. Suggest the user re-download or screenshot + describe. |
| `inputs/data/` referenced by problem statement but missing files | Escalate. Some problems ship data later; user may need to wait. |
| All problems score ≤ 0 | Print the scorecard, recommend the least-bad option, but flag the risk and ask the user to confirm. |
| User refuses to lock in within 6 hours | Escalate `budget_overrun` — triage is consuming modeling time. |

## When to load which reference

| File | Load when |
|---|---|
| `references/problem-selection-rubric.md` | Step 4 — scoring each problem |
| `references/data-recon-checklist.md` | Step 3 — what to extract from each data file |
| `references/contest-typology.md` | Step 2 — recognizing the task type from the problem statement |
| `auto-mm/references/state-contract.md` | Writing any output file |
| `auto-mm/references/integrity-rules.md` | Step 4 — Rule 1 (problem-statement-first) and Rule 7 (budget) inform scoring |
| `auto-mm/references/escalation-policy.md` | Any failure mode in the table above |
| `auto-mm/references/contest-types.md` | Building `contest_brief.md` from current-year facts |

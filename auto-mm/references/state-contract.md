# State contract — `runs/<run_slug>/`

Single source of truth for every file the four stage skills read and write. **No agent memory crosses invocations.** If a piece of information is not on disk under `runs/<run_slug>/`, it does not exist.

`<run_slug>` is built by the orchestrator at first invocation as `<contest>-<year>-<problem>` once selected (e.g. `mcm-2026-C`, `cumcm-2026-A`, `huazhongbei-2025-A`). Before the user picks a problem in Stage 0, the slug is provisional: `<contest>-<year>-untriaged`.

## Full layout

```
runs/<run_slug>/
├── run.yaml                       # contest type, problem set, deadline, time budget, language, team
├── .heartbeat                     # JSON: {stage, substep, ts_utc, pid} — overwritten every tick
├── progress.jsonl                 # append-only: every meaningful sub-step
├── STOP                           # if present, supervisor & orchestrator exit cleanly
├── PAUSE                          # if present, orchestrator finishes current substep then idles
├── inputs/                        # everything from the contest organizers (read-only after Stage 0)
│   ├── problems/                  # raw problem PDFs / HTML / images (A.pdf, B.pdf, ...)
│   ├── data/                      # raw attachment data: CSVs, Excel, images, etc.
│   └── notices/                   # any clarifications, errata posted by organizers
├── stage0_triage/
│   ├── contest_brief.md           # current-year contest facts (page limit, AI report rule, deadlines)
│   ├── problems_index.md          # one-line summary of every problem (A/B/C/D)
│   ├── data_recon.md              # what's in inputs/data/: row counts, fields, units, oddities
│   ├── selection_scorecard.md     # the rubric scores for each candidate problem
│   ├── problem_choice.md          # CHOSEN problem + rationale
│   └── hand_off.md
├── stage1_modeling/
│   ├── problem_decomposition.md   # sub-questions Q1..Qk with I/O, hard/soft constraints, metric
│   ├── assumptions.md             # numbered assumptions + 1-paragraph justification each
│   ├── notation.md                # the symbol table (sets, params, decision vars, indices)
│   ├── candidates.md              # 2-4 candidate model families with pros/cons + verdict
│   ├── model.md                   # the chosen formal model (objective, constraints, derivations)
│   ├── literature.md              # supporting references (real, citeable)
│   └── hand_off.md
├── stage2_solving/
│   ├── pipeline.py | pipeline.m   # entry script; reads inputs/data, writes outputs/
│   ├── src/                       # supporting Python modules (data.py, model.py, solve.py, report.py, style.py)
│   ├── runs/<exp_id>/             # one folder per experiment (baseline, main, ablation, sens)
│   │   ├── config.yaml
│   │   ├── result.json            # primary metrics
│   │   ├── tables/                # CSV/Markdown
│   │   └── log.txt
│   ├── leaderboard.csv            # rolling: exp_id, primary metric, status (rebuilt from runs/*/result.json)
│   ├── figures/                   # one subfolder per figure (see below) + the final <fig_id>.pdf next to it
│   │   ├── <fig_id>/              # brief.md, prompt.md, source/, output.pdf, self_check.md, status
│   │   └── <fig_id>.pdf           # the approved copy LaTeX references
│   ├── validation.md              # baseline / exact-Gap / ablation / cross-method (≥3 of 4)
│   ├── sensitivity.md             # parameter sweeps + insight bullets
│   └── hand_off.md
└── stage3_writing/
    ├── paper/                     # the LaTeX project (copied from template)
    │   ├── main.tex
    │   ├── references.bib         # built from stage1_modeling/literature.md
    │   ├── img/                   # symlink or copy from stage2_solving/figures
    │   └── main.pdf               # build output
    ├── abstract_draft.md          # iterated drafts; final synced into paper/
    ├── section_checklist.md       # what's present / missing per required section
    ├── build_log.md               # xelatex output + grep results for warnings
    ├── anonymity_report.json      # PDF text + metadata scan results (machine-readable)
    ├── submission/
    │   ├── <root_name>/           # final flat tree to be zipped (e.g. team control number)
    │   └── submit.zip             # the artifact handed to the user
    └── hand_off.md
```

## File-by-file specs

### `run.yaml` (created at Stage 0 ask, never silently rewritten)

```yaml
contest:
  family: mcm | cumcm | huazhongbei | shumo | other
  variant: MCM | ICM                    # only when family=mcm
  year: 2026
  problem_set: [A, B, C, D]             # the problems offered this year
  organizer_url: https://www.comap.com/...
  language_required: en | zh            # paper output language
created_at_utc: 2026-05-12T08:30:00Z
deadline_utc: 2026-02-09T20:00:00Z      # contest hard deadline
team:
  size: 3
  solo: false
  control_number: "2603956"             # MCM team number; null otherwise
  blind: true                           # must keep paper anonymous
budget:
  total_hours: 96                       # contest length
  per_stage_hours:
    triage: 6
    modeling: 18
    solving: 42
    writing: 24
    buffer: 6
  recompute_on_drift: true              # if a stage overruns, shrink later stages
pause_offset_seconds: 0                 # accumulated PAUSE duration; budget-drift math excludes this
chosen_problem: C | null                # null until Stage 0 finishes
run_slug: mcm-2026-C
supervisor:
  mode: claude-loop | shell-supervisor | manual
  poll_seconds: 1200
  max_runtime_hours: null               # null = run until deadline or STOP (also read by supervisor.sh)
```

### `.heartbeat` (overwritten every tick — user can `cat` it without invoking agent)

```json
{
  "stage": "stage2_solving",
  "substep": "running sensitivity sweep over carbon_price ∈ {50,80,120}",
  "ts_utc": "2026-02-08T14:22:11Z",
  "pid": 47215,
  "agent": "claude-opus-4-7",
  "deadline_remaining_h": 29.6
}
```

### `progress.jsonl` (append-only)

```json
{"ts_utc":"2026-02-08T08:31:02Z","stage":"stage0","event":"problems_indexed","count":4}
{"ts_utc":"2026-02-08T09:14:33Z","stage":"stage0","event":"problem_chosen","problem":"C","reason":"data fully provided, optimization-friendly"}
{"ts_utc":"2026-02-08T10:02:11Z","stage":"stage1","event":"model_committed","family":"MILP+ALNS"}
{"ts_utc":"2026-02-08T15:45:00Z","stage":"stage2","event":"baseline_done","metric":0.7421}
{"ts_utc":"2026-02-09T11:02:55Z","stage":"stage3","event":"abstract_first_draft"}
{"ts_utc":"2026-02-09T18:30:01Z","stage":"stage3","event":"paper_built","pages":24}
{"ts_utc":"2026-02-09T19:05:00Z","stage":"stage3","event":"submission_packaged","zip_bytes":4823420}
```

Resume protocol: read the **last** line per stage to know where to pick up. Always sort by `ts_utc` across stages.

**Completion signals**: a run is "done" when the last `stage3` event is `paper_built` (build passed) or `submission_packaged` (zip ready). The supervisor and orchestrator both treat either as the terminal state and switch into incremental-improvement loop (or idle until deadline).

### `stage0_triage/problem_choice.md`

```markdown
# Problem choice — <run_slug>

## Decision
Problem **C**. Locked at 2026-02-08T09:14Z. Once committed, do not switch — Stage 1+ assume this.

## Why this one
- Data: full dataset shipped (no scraping needed). +2
- Method fit: classical inverse-optimization + light ML — within team strength. +2
- Risk: scoring rubric clear; no ambiguous physical constraint. +1
- Differentiator: room for an attention-mechanism module that judges value. +1

## Why not the others
- A: requires high-fidelity physical simulation; PDE skills weak. −2
- B: open-ended policy essay flavor; harder to defend with numbers. −1
- D: dataset is partial; requires web scraping inside 96h. risky. −1

## Lock-in checklist
- [x] Re-read problem statement end-to-end
- [x] Confirmed data is sufficient
- [x] Confirmed team has at least 1 baseline approach we can implement in 12h
```

### `stage1_modeling/model.md` — required ingredients

A complete model section must, at minimum, contain:

1. **Notation table** — sets, indices, parameters (with values/units), decision variables. No magic numbers in formulas.
2. **Objective(s)** — formula + plain-English statement + units (all costs in the same currency).
3. **Constraints** — grouped (flow, capacity, time, policy, feasibility) and individually numbered for cross-reference.
4. **Derivations** — any non-trivial step shown (e.g. linearization, dual, reformulation).
5. **Why this family** — one paragraph linking back to `candidates.md`.
6. **Known limitations** — what the model does *not* capture, deferred to sensitivity or future work.

### `stage2_solving/runs/<exp_id>/result.json`

```json
{
  "exp_id": "main-v3",
  "config_hash": "8a91…",
  "metric_primary": {"name": "total_cost_yuan", "value": 184320.0, "direction": "min"},
  "metrics_secondary": {"emissions_kg": 1294.1, "rdi": 0.082, "wallclock_s": 412.3},
  "instance": "official-full",
  "seed": 42,
  "git_sha": null,
  "notes": "main run cited as headline number in abstract"
}
```

### `stage3_writing/section_checklist.md`

```markdown
| Section | Required by rubric | Present | File |
|---|---|---|---|
| 摘要 / Abstract | yes (one page, hard numbers) | ✅ | paper/main.tex |
| 问题重述 / Problem Restatement | yes | ✅ | part_1_pre.tex |
| 假设 / Assumptions | yes (numbered, justified) | ✅ | part_1_pre.tex |
| 符号说明 / Notation | yes | ✅ | part_1_pre.tex |
| 数据预处理 / Data Processing | yes | ✅ | part_2_model.tex |
| 模型建立 / Model | yes | ✅ | part_2_model.tex |
| 算法 / Algorithm | yes | ✅ | part_2_model.tex |
| 结果 / Results | yes (with figures) | ✅ | part_2_model.tex |
| 灵敏度 / Sensitivity | yes | ✅ | part_2_model.tex |
| 模型评价 / Strengths & Weaknesses | yes | ✅ | part_3_conclusion.tex |
| 参考文献 / References | yes (real, cited in body) | ✅ | references.bib |
| 附录 / Appendix | yes (code, long tables) | ✅ | part_4_Appendix.tex |
```

## Read-order on resume

When `auto-mm resume <run_slug>` is invoked, the orchestrator reads in this order:

1. `run.yaml` — contest meta, budget, supervisor.
2. `STOP` / `PAUSE` — if present, exit / idle.
3. `progress.jsonl` — last `ts_utc` per stage decides where we are.
4. `.heartbeat` — sanity check: another agent still running?
5. Latest `hand_off.md` of the most-advanced stage — the briefing for what to do next.
6. **Deadline math** — `deadline_utc - now` is the source of truth for budget pressure, not `run.yaml.budget.total_hours`.

If any contract file is missing on resume, the orchestrator escalates to the user **instead of guessing** — see `escalation-policy.md`.

## Hand-off file convention

Every stage's `hand_off.md` answers exactly three questions, in this fixed order, each under a top-level H2 heading. The body under each heading may use prose paragraphs OR bulleted lists OR both — what matters is the **three sections in order**, not the prose style.

```
## What I did
- bulleted list or short paragraph: artifacts written, with paths

## What's true now
- bulleted list or short paragraph: facts the next stage should act on
  (problem, model family, headline number so far, hours remaining, blocking issues)

## What you should do next
- short paragraph or directive bullet: concrete next action for the next stage skill
```

Orchestrator's integrity gate verifies the presence of all three H2 sections (greppable via `grep -c '^## What' hand_off.md` — must equal 3) and that each section is non-empty. Style inside each section is left to the writing skill.

The next stage reads only `hand_off.md` + the structured files it lists.

## Things this contract intentionally does NOT cover

- Where the contest problem PDF *originally* came from. Users drop it into `inputs/problems/`. The skill does not download it.
- Author names, school, advisor — these MUST NOT appear anywhere under `runs/<run_slug>/` because the writing stage greps the final PDF for them.
- Cloud / remote compute. The skill runs on the user's local machine; if heavy compute is needed, the user moves the run to that machine and points the supervisor at the same `runs/` tree.

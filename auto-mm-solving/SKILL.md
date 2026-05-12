---
name: auto-mm-solving
description: >-
  Stage 2 of auto-mm. Implements the formal model from stage1_modeling/model.md
  as runnable code (Python primary, MATLAB if the user has historical scripts),
  runs the required experiment matrix (baseline + main + small-instance exact
  Gap + ≥1 ablation + sensitivity sweeps on to-sweep assumptions), and
  produces publication-quality PDF-vector figures. Validates by Rule 6 (a
  result has at least one of baseline / exact-Gap / ablation / sensitivity).
  Records every experiment under stage2_solving/runs/<exp_id>/result.json so
  the writing stage can quote headline numbers without rerunning. Generates
  figures under stage2_solving/figures/ following the figure-quality rules:
  PDF vectors, restrained palette, captions managed by LaTeX, no orphan labels.
---

# Stage 2 — Solving

The longest stage by clock time and the easiest one to overrun. Discipline here is the time-budget discipline.

## Trigger

- Delegated to by the orchestrator after `stage1_modeling/hand_off.md` is written.
- Can be invoked directly: `auto-mm-solving <run_slug>` to add an experiment, re-run after a model revision, or refresh figures.

The orchestrator will not let this stage run if `stage1_modeling/model.md` is missing or the integrity gate is open.

## Inputs

- `runs/<run_slug>/run.yaml`
- `runs/<run_slug>/stage1_modeling/{model.md, notation.md, assumptions.md, problem_decomposition.md}`
- `runs/<run_slug>/inputs/data/`
- `runs/<run_slug>/stage0_triage/data_recon.md` — the anomaly section dictates pre-processing

## Outputs (the contract)

```
runs/<run_slug>/stage2_solving/
├── pipeline.py | pipeline.m       # entry script
├── src/                           # supporting modules (free-form internal structure)
├── runs/<exp_id>/                 # one folder per experiment
│   ├── config.yaml
│   ├── result.json                # primary metrics
│   ├── tables/                    # CSV/Markdown
│   ├── log.txt
│   └── (artifacts specific to the run: oof.npy, route.json, ...)
├── leaderboard.csv                # rolling: exp_id, primary metric, status
├── figures/                       # PDF vectors, named by paper section
├── validation.md                  # baseline + exact Gap + ablation findings
├── sensitivity.md                 # per-assumption sweep insight
└── hand_off.md
```

## Workflow

### 1. Scaffold the pipeline

Create `pipeline.py` (or `.m` if the user prefers MATLAB) with this top-level structure:

```python
# pipeline.py — entry point for stage2_solving
import argparse, json, time, pathlib, yaml
from src.data import load_inputs
from src.model import build_model      # the implementation of stage1_modeling/model.md
from src.solve import solve            # invokes solver / heuristic
from src.report import write_result    # writes result.json + tables

def main(exp_id, config_path):
    cfg = yaml.safe_load(open(config_path))
    data = load_inputs(cfg['data'])
    model = build_model(data, cfg['model'])
    result = solve(model, cfg['solver'])
    write_result(exp_id, cfg, result)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp", required=True)
    p.add_argument("--config", required=True)
    main(p.parse_args().exp, p.parse_args().config)
```

The skill writes the supporting `src/data.py`, `src/model.py`, `src/solve.py`, `src/report.py` per the chosen model family. See `references/algorithm-selection.md` for which solver wrappers to import.

It also seeds `src/style.py` and `src/__init__.py` so plotting scripts can `from src.style import PALETTE, apply_style`:

```bash
mkdir -p stage2_solving/src
touch stage2_solving/src/__init__.py
# style.py is a thin re-export from the bundled figure_style.py
cp auto-mm-solving/assets/figure_style.py stage2_solving/src/style.py
```

This satisfies the import contract in `figure-prompt-patterns.md`. If the user prefers a single source of truth, they may instead symlink `src/style.py` → `auto-mm-solving/assets/figure_style.py`.

### 2. Run the required experiment matrix

Minimum five runs per Rule 6:

| exp_id pattern | Purpose | Required? |
|---|---|---|
| `baseline-<name>` | Deliberately weak method (greedy, single-fold, no ML, etc.). | yes |
| `main-v1` | First full run of the model in `model.md`. | yes |
| `exact-small` | Solve a sub-problem of ≤15 customers / ≤10 nodes with an exact solver; report Gap. | yes (if model is amenable; else justify) |
| `ablation-<feature>` | Remove the most-important architectural component; rerun. | ≥1 required |
| `sweep-<param>` | Sensitivity on one `to-sweep` parameter. | ≥1 per to-sweep assumption |

Each run writes `runs/<exp_id>/result.json` following the schema in `auto-mm/references/state-contract.md`. Append a row to `leaderboard.csv`.

If an experiment cannot be completed within its budget allocation, write a "incomplete" status row to `leaderboard.csv` and continue with the next — do not get stuck.

### 3. Validate (`validation.md`)

Per `references/validation-protocol.md`, the gate requires **at least 3 of the 4** kinds of validation, with at least one being exact-Gap OR ablation. When the model is not amenable to exact-Gap (inference, open-ended, very-large continuous), substitute with cross-method comparison.

Write `validation.md`. Use any 3+ of the following subsections (skip the inapplicable ones with a one-line "N/A: <reason>"):

```markdown
# Validation — <run_slug>

## Baseline vs Main
- Baseline (`<exp_id>`): primary metric = <value>.
- Main (`main-vN`): primary metric = <value>.
- Improvement: <absolute>, <relative %>.

## Small-instance exact Gap         <!-- include if model is amenable to exact solve -->
- Exact solver: <Gurobi / CP-SAT / branch&bound>.
- Instance size: <e.g. 12 customers, 8 nodes>.
- Exact optimum: <value>.
- Main on same instance: <value>.
- Optimality Gap: <%>.

## Ablation: <feature>
- With <feature>: <value>.
- Without <feature>: <value>.
- Marginal contribution: <absolute>, <relative %>.
- Interpretation: <one paragraph on what this means for the model's claim>.

## Cross-method comparison         <!-- substitute for exact Gap when N/A -->
- Method A (well-known alternative): <metric>.
- Method B (well-known alternative): <metric>.
- Main: <metric>.
- Interpretation: <one paragraph>.
```

The orchestrator's gate checks that **≥3 non-`N/A` subsections** are present, with **at least one of (Exact Gap, Ablation)** materialized. A run that only has Baseline + Sensitivity (no exact Gap, no ablation, no cross-method) fails the gate.

### 4. Sensitivity (`sensitivity.md`)

For each `to-sweep` assumption from `stage1_modeling/assumptions.md`:

1. Define a sweep grid (typically 3-5 points covering low / baseline / high).
2. Run.
3. Plot (figures/sens-<param>.pdf).
4. Write insight, not data dump:

```markdown
## Sensitivity: carbon price $p_c$
- Grid: {30, 50, 80, 120, 200} 元/kg CO₂.
- Main results: <table or sentence with breakeven points>.
- **Insight**: above $p_c \approx 110$ 元/kg the optimal fleet shifts from
  diesel-dominant to electric-dominant. The non-linearity comes from the
  capacity gap between vehicle types.
```

`references/sensitivity-analysis.md` has the recipe in more depth.

### 5. Produce figures (brief → produce → self-check)

Every figure goes through the workflow in `references/figure-workflow.md`. Three channels, one shared spec:

- **`type: data`** — driven by real numbers. Code prompt → `plot.py` (matplotlib) or `tikz.tex` → render against data.
- **`type: schematic`** — concept illustration / flowchart. TikZ code prompt (default) or AI image-gen prompt.
- **`type: sourced`** — real-world image (map, policy doc, device, satellite). **AI must NOT generate this.** Search → download → cite. Full protocol in `references/figure-sourcing.md`.

The catalog of 数模 figure types (≈20 entries: convergence, Pareto, route map, Gantt, heatmap, ROC, model flowchart, region map, policy screenshot, etc.) and which channel each belongs to lives in `references/figure-types-catalog.md`. The quick rule: real numbers from your experiments → `data`; specific real-world place / object / document → `sourced`; otherwise (pure concept) → `schematic`.

Per-figure folder layout (the contract — common files marked ★, channel-specific marked with channel):

```
stage2_solving/figures/
└── <fig_id>/                          # e.g. fig-route-map, fig-model-flowchart, fig-region-map
    ├── brief.md                       ★ Step 1: information document
    │
    ├── prompt.md                      [data + schematic] Step 2: generation prompt
    ├── source/                        [data + schematic]
    │   ├── plot.py | tikz.tex | image_request.json
    │   ├── data_used.csv              [data only] snapshot of numbers used
    │   └── log.txt
    │
    ├── search_queries.md              [sourced] Step 2: the search plan
    ├── sources/                       [sourced] candidate downloads + metadata
    │   ├── candidate_NN.png
    │   └── candidate_NN.meta.json
    ├── attribution.md                 [sourced] citation + license + modifications
    │
    ├── output.pdf | chosen.png        ★ the final artifact (name varies by channel)
    ├── self_check.md                  ★ Step 3: style + claim audit
    └── status                         ★ draft | needs_revision | ready

# after self-check passes, a copy lands at:
└── <fig_id>.<ext>                     # the path LaTeX uses via \includegraphics{img/<fig_id>}
```

Workflow per figure:

1. Write `brief.md` using `figure-brief-template.md`. The brief's `type:` field commits to a channel; the one-sentence claim anchors everything.
2. Channel-specific production:
   - `data` / `schematic`: build `prompt.md` from `figure-prompt-patterns.md`, run the generator. For `data`, snapshot `data_used.csv` for reproducibility.
   - `sourced`: write `search_queries.md`, run `auto-mm-solving/assets/download_image.py` for each candidate, choose, write `attribution.md`. Full protocol in `references/figure-sourcing.md`.
3. Self-check against `figure-quality.md` (universal) + channel-specific checks. If `ready`, copy the final artifact to `figures/<fig_id>.<ext>`. If `needs_revision`, edit `prompt.md` or re-search and try again. Cap at 3 iterations; on the 4th, escalate.

`assets/figure_style.py` provides the matplotlib RC and the PALETTE. The figure-prompt patterns require scripts to import it as `from src.style import PALETTE, apply_style`, so Stage 2 also seeds a `src/style.py` that re-exports from `figure_style.py` (the pipeline-scaffolding step does this; see Step 1 above).

For `sourced` figures, `assets/download_image.py` fetches a candidate and emits a starter `.meta.json` (URL + retrieved_at + dimensions + format). The human fills in `title`, `creator`, `license`, `license_url` from the source page — the script does not guess licenses.

The orchestrator's hand-off gate refuses to advance to Stage 3 if any `figures/<fig_id>/status` is anything other than `ready` (or `dropped` with a logged reason in `self_check.md`).

### 6. Write `hand_off.md`

```markdown
# Stage 2 → Stage 3 hand-off

## What I did
- Implemented pipeline.py for the model in stage1_modeling/model.md.
- Ran <N> experiments: <baseline_id>, <main_id>, <exact_id>, <ablation_ids>, <sweep_ids>.
- Wrote validation.md (baseline gap = X%, exact gap = Y%, ablation delta = Z%).
- Wrote sensitivity.md (<K> assumptions swept; key insight: ...).
- Generated <F> PDF-vector figures under figures/.

## What's true now
- Headline metric for the abstract: <metric> = <value> (from runs/main-vN/result.json).
- Best baseline: <value> (from runs/baseline-.../result.json). Improvement: <%>.
- Small-instance Gap: <%>.
- Figures ready: <list of filenames by paper section>.
- Hours remaining in budget: <H>. Writing budget: <H3>.
- Blocking issues: <none / list>.

## What you should do next
Stage 3: drop the chosen template (mcm-template or cumcm-template) into
stage3_writing/paper/. Wire main.tex to include the figures from
stage2_solving/figures/ (symlink the directory). Fill in part_1_pre.tex
(background, restatement, assumptions, notation), part_2_model.tex (data
processing, model from stage1_modeling/model.md, algorithm from this
stage's pipeline.py prose summary, results from validation.md, sensitivity
from sensitivity.md), part_3_conclusion.tex (strengths, weaknesses, future).
Iterate the abstract 3 times — each pass must keep all hard numbers from
validation.md. Build with xelatex twice. Run anonymity scan. Package
submit.zip.
```

Append `progress.jsonl` event `solving_done`. Exit.

## Idempotency

- Every experiment's `config.yaml` is the input; its hash is the cache key. If an `exp_id` with matching hash already has a `result.json`, skip the run and reuse.
- A user can force a re-run with `--rerun <exp_id>`.
- The leaderboard is rebuilt from `runs/*/result.json` on every Stage 2 invocation — never trust a stale leaderboard.csv.

## Time budget pressure

Stage 2 is the most likely to overrun (`time-budget.md` § "Drift detection"). When the orchestrator signals drift:

- 0.8 ratio → finish the currently-running experiment, then stop spawning new sensitivity points.
- 1.0 ratio → escalate to user. Default if no reply: collapse sensitivity grids to 3 points; drop low-value ablations.
- 1.2 ratio → force-finalize with whatever's on disk. Hand off `hand_off.md` flagged `incomplete: true`.

The orchestrator monitors per-experiment wall time and aborts a run that exceeds 1.5x its config's `expected_wallclock_s`. Aborted runs write `result.json` with `status: aborted` and a partial-metric estimate if available.

## Failure modes

| Symptom | Action |
|---|---|
| Solver crashes (OOM / segfault) | Log to `runs/<exp_id>/log.txt`. Try once with smaller instance; if still crashes, drop the experiment and document. |
| Main metric worse than baseline | This is a finding, not a failure. Investigate; either fix the model or honestly report it (consider revising stage1_modeling). |
| Figures show wrong axes / labels | Re-check `figure-quality.md`. Most often: in-figure title (drop it) or unit mismatch. |
| Sensitivity sweep reveals a chosen baseline is unstable | Re-pick baseline (one parameter from the sweep grid that's representative); update `model.md` baseline values. |
| Exact solver infeasible on small instance | Re-check model formulation — usually a typo in constraints. If genuine infeasibility, the model has a bug. |

## When to load which reference

| File | Load when |
|---|---|
| `references/algorithm-selection.md` | Step 1 — choosing the solver / heuristic wrapper |
| `references/figure-types-catalog.md` | Step 5 — classifying each figure into `data` / `schematic` / `sourced` |
| `references/figure-workflow.md` | Step 5 — for every figure, the brief→produce→self-check pipeline |
| `references/figure-brief-template.md` | Step 5.1 — writing each figure's brief (any channel) |
| `references/figure-prompt-patterns.md` | Step 5.2 — building each figure's prompt (`data` / `schematic` channels) |
| `references/figure-sourcing.md` | Step 5.2 — search → download → cite workflow for the `sourced` channel |
| `references/figure-quality.md` | Step 5.3 — self-check against style rules; also for the orphan-label grep |
| `references/sensitivity-analysis.md` | Step 4 — building sweep grids and writing insight |
| `references/validation-protocol.md` | Step 3 — what counts as adequate validation per Rule 6 |
| `auto-mm-modeling/references/pitfalls-from-experience.md` | Pitfall P10-P12 inform sensitivity and figure choices |
| `auto-mm/references/integrity-rules.md` | Rule 6 enforces validation; Rule 8 enforces figure discipline |
| `auto-mm/references/state-contract.md` | Writing any output file |

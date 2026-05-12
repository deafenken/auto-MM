# Time budget — the only currency that matters

A 数模比赛 is won or lost on time allocation, not on cleverness. The orchestrator treats `deadline_utc - now` as the master clock and pressures every stage against it.

## Default allocations

Computed as fractions of `run.yaml.budget.total_hours`. The orchestrator writes these to `run.yaml.budget.per_stage_hours` at first invocation.

### CUMCM (国赛, 72h)

| Stage | Fraction | Hours | Why this much |
|---|---|---|---|
| triage | 0.07 | 5h | Read 3 problems (A/B/C/D), score them, choose. Includes initial data look. |
| modeling | 0.20 | 14h | Formalization is the highest-leverage step. Cutting here is the most common fatal mistake. |
| solving | 0.42 | 30h | Implementation + validation + sensitivity. Always overruns if not bounded. |
| writing | 0.25 | 18h | National contest paper is shorter than MCM; 18h is enough for a polished 20-page paper. |
| buffer | 0.06 | 5h | Anonymity, packaging, last-mile build failures. |

### MCM/ICM (美赛, 96h)

| Stage | Fraction | Hours | Why |
|---|---|---|---|
| triage | 0.06 | 6h | More problems (A-F), but English problem statements take longer to digest. |
| modeling | 0.19 | 18h | MCM rewards mathematical depth — invest here. |
| solving | 0.44 | 42h | More experimentation and more figures than CUMCM. |
| writing | 0.25 | 24h | 20-25 page English paper with executive memo; non-trivial polish time. |
| buffer | 0.06 | 6h | Buffer is non-negotiable. |

### Short single-day contests (12-24h, e.g. 华中杯单日赛、校赛)

Drop modeling/solving overlap, run them concurrently:

| Stage | Fraction | Hours (24h) |
|---|---|---|
| triage | 0.08 | 2h |
| modeling + solving (interleaved) | 0.55 | 13h |
| writing | 0.30 | 7h |
| buffer | 0.07 | 2h |

## Drift detection

After every micro-step, the orchestrator computes:

```
budget_used   = (now - stage_started_at).total_hours
budget_target = run.yaml.budget.per_stage_hours[current_stage]
drift_ratio   = budget_used / budget_target
```

Behaviors by `drift_ratio`:

| Range | Action |
|---|---|
| < 0.8 | Normal. Continue. |
| 0.8 – 1.0 | Warning logged to `progress.jsonl`. Stage skill is told to start wrapping. |
| 1.0 – 1.2 | Open escalation block in `hand_off.md`. Ask user: cut scope / steal from later stage / extend total. Default after 30 min of no response: cut scope. |
| > 1.2 | Force-finalize the stage with whatever's on disk. The next stage receives a `hand_off.md` flagged `incomplete: true`. |

## Lockdown mode — last 6 hours

When `(deadline_utc - now) ≤ 6h`, the orchestrator enters **lockdown**:

1. Reject any task that adds new modeling or experiments. The user must explicitly type "override lockdown" — even then it's logged with a warning.
2. All remaining time goes to writing, building, anonymizing, packaging.
3. Heartbeat updates every 30 seconds instead of 60.
4. Every 30 minutes, print a status line: hours remaining, sections done, blocking issues.

## Cross-stage rebalancing

If Stage 1 (modeling) overran by 3h, the orchestrator does NOT silently subtract 3h from Stage 2's plan — it asks. The reason: solving usually has hidden parallelism (figures + sensitivity can overlap with main run); writing usually does not. The user is in the best position to say which stage to compress.

When rebalancing is approved, the orchestrator writes the new `per_stage_hours` to `run.yaml` and adds a `progress.jsonl` event `budget_rebalanced` with the before/after.

## What "hours" means

Wall-clock hours from the user's perspective, not agent compute time. If the user steps away for the night, the budget keeps ticking. This is a deliberate choice — the deadline does not pause for sleep. The orchestrator's job is to wake up under a supervisor and continue.

If the user wants to genuinely pause the clock (e.g., they're physically away and unable to be the human-in-loop), they `touch runs/<slug>/PAUSE` and the budget tick freezes until the PAUSE file is removed. This is recorded in `progress.jsonl` for honesty.

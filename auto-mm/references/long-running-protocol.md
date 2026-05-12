# Long-running protocol — surviving 72-96h across crashes and context resets

A 数模 run lives longer than any single Claude Code conversation. The agent process **will** be interrupted (laptop sleep, model context reset, network blip, OOM). Everything must resume from disk.

## Core invariants

1. **All state on disk under `runs/<run_slug>/`.** Nothing important lives only in memory or only in the conversation transcript.
2. **Micro-steps are idempotent.** Re-running a step that already succeeded must re-read disk and continue past it without duplicating side-effects.
3. **Append-only logs.** `progress.jsonl` and any submission-like log is line-appended, never rewritten. Resume reads the tail.
4. **Atomic writes.** Any file the next stage will read is written via `path.tmp` + rename. No partial-file resumes.
5. **Resume is the default.** `auto-mm <run_slug>` always means "continue from disk." A fresh start requires `--restart` and a one-time confirmation.

## Resume algorithm

```
1. Read runs/<run_slug>/run.yaml. Missing → first-invocation flow (see SKILL.md).
2. If STOP exists → exit 0 with "STOPPED, remove the STOP file to resume."
3. If PAUSE exists → exit 0 with "PAUSED."
4. Read .heartbeat. If pid alive AND ts_utc < 5 min old → refuse to start a second agent, exit.
5. Read progress.jsonl tail. Compute last-event per stage by max(ts_utc).
6. Decide dispatch:
   - chosen_problem is null → resume stage0_triage
   - stage0 done, model not committed → resume stage1_modeling
   - model committed, solving incomplete → resume stage2_solving
   - solving has main result, writing incomplete → resume stage3_writing
   - all stages have a hand_off and writing is "build_ok" → loop body: incremental improvement
7. Heartbeat every 60s while running. Final heartbeat at clean exit with stage="idle".
```

## Heartbeat schema

```json
{
  "stage": "stage2_solving",
  "substep": "ALNS iter 1250/3000, current best 184320.0",
  "ts_utc": "2026-02-08T14:22:11Z",
  "pid": 47215,
  "agent": "claude-opus-4-7",
  "deadline_remaining_h": 29.6
}
```

User can `cat runs/<slug>/.heartbeat` any time without interfering with the run.

## STOP and PAUSE semantics

- `touch STOP` — clean exit at next micro-step boundary. The supervisor sees STOP and does not re-invoke. To resume, `rm STOP`.
- `touch PAUSE` — finish current micro-step, then idle. Time budget ticking freezes (see `time-budget.md`). To resume, `rm PAUSE`.
- Both files honored at the top of every micro-step. Never inside a long inner loop — the inner loop must check periodically (every minute) if running >60s.

## Supervisor modes

`run.yaml.supervisor.mode` is one of:

- **`manual`** — the orchestrator never re-invokes itself. The user is expected to re-invoke. Default for first runs while the user is figuring out their workflow.
- **`claude-loop`** — inside Claude Code, the user runs `/loop /auto-mm resume <slug>` and the harness drives re-invocation. The orchestrator's job is just to exit cleanly so /loop fires again.
- **`shell-supervisor`** — outside Claude Code, `bash auto-mm/assets/supervisor.sh <slug>` runs a forever loop with backoff and timeout. The orchestrator's job is the same: exit cleanly.

The supervisor never inspects state itself. It only re-invokes the orchestrator.

## Idempotency examples

| Operation | How it's idempotent |
|---|---|
| Index problems in `inputs/problems/` | Compute file hash; skip files whose hash is already in `problems_index.md`. |
| Run main experiment | Check if `stage2_solving/runs/<exp_id>/result.json` exists and config_hash matches; skip if yes. |
| Compile LaTeX | Re-running `xelatex` is naturally idempotent. Compare timestamp of `main.pdf` vs newest `.tex` — skip if newer. |
| Submit zip | The artifact filename includes a content hash; identical content → identical hash → skip. |

If a step cannot be made idempotent (e.g. external API write), it is escalated rather than retried.

## Things that cross invocations only via disk

| Information | File |
|---|---|
| Chosen problem | `run.yaml.chosen_problem` |
| Latest model formulation | `stage1_modeling/model.md` |
| Best result so far | `stage2_solving/leaderboard.csv` (and per-run `result.json`) |
| Next thing to do | latest stage's `hand_off.md` |
| Hours remaining | computed from `deadline_utc` + clock; do not cache |
| User's last instruction | last `progress.jsonl` event with `source: user` |

Anything not in this table is **derivable** from the others. Never write a state file that just summarizes other state files.

## When the protocol fails

If on resume the orchestrator finds inconsistent state (e.g. `progress.jsonl` says solving finished but `result.json` is missing), it does **not** patch and continue. It writes a `hand_off.md` escalation block listing the inconsistency and exits to the user. See `escalation-policy.md`.

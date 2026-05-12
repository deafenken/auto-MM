---
name: auto-mm
description: >-
  Orchestrate a 72-96 hour mathematical-modeling contest run end-to-end. At
  first invocation asks the user which contest (MCM/ICM 美赛 or CUMCM 国赛 or
  other), gathers contest info (deadline, problem set, language, team number,
  template), then sequences four sub-skills: auto-mm-triage (pick A/B/C/D),
  auto-mm-modeling (formal model + assumptions + notation), auto-mm-solving
  (code, validation, sensitivity, figures), auto-mm-writing (LaTeX paper,
  anonymity check, submission zip). Enforces the 10 integrity rules
  (problem-statement-first, anonymity-absolute, real-citations-only, AI-must-
  address-uncertainty, etc.) and the time budget per stage. All state lives
  under runs/<run_slug>/ so the run survives crashes and Claude context resets.
  Pair with assets/supervisor.sh for unattended multi-day operation.
---

# Auto-MM Orchestrator

A four-stage closed-loop agent for 数学建模 contests. The orchestrator does **not** build the model itself — it sequences four specialist sub-skills, owns the state contract, and enforces the integrity rules.

Designed around three hard realities of mathematical-modeling contests:

1. **The clock is the only opponent.** 72-96 hours and the deadline does not move. Everything is allocated against `deadline_utc - now`.
2. **No iterative feedback.** No public leaderboard, no validation set, no judge in the loop. You submit once and find out months later. Internal validation (baseline / ablation / exact-Gap / sensitivity) **is** the feedback.
3. **The paper is the artifact.** Code and experiments matter only insofar as they end up in the paper as defensible numbers and figures. A perfect model with a bad write-up loses to a decent model with a good one.

## When to invoke this skill

Trigger when the user says any of:

- "刷数模 <contest>"
- "auto mm" / "auto-mm"
- "开始数模比赛"
- "继续刷 <run_slug>" / "resume <run_slug>"
- Provides a contest name (国赛 / 美赛 / 华中杯 / 妈杯 / 校赛 …) with a deadline
- Asks "status of my <run_slug>" — this triggers a status-only invocation (read `.heartbeat` + latest `hand_off.md`, print, exit; do not start any new work)

If the user has only an isolated modeling question with no contest context, this is **not** the right skill — answer directly.

## High-level flow

```
                  ┌──────────────────────────────────────────────────────────┐
                  │           auto-mm  (this skill — orchestrator)           │
                  └──────────────────────────────────────────────────────────┘
                                       │
        First invocation? ──yes──►  Ask: which contest? (MCM | CUMCM | other)
                                       │   Ask: deadline, problem set,
                                       │        team control #, language,
                                       │        supervisor mode
                                       │   Write run.yaml. mkdir runs/<slug>/
                                       ▼
                                  Stage 0 (auto-mm-triage)
                                     index problems, recon data,
                                     score A/B/C/D, commit one.
                                       │
                                       ▼
                                  Stage 1 (auto-mm-modeling)
                                     decomposition, assumptions, notation,
                                     candidate models, commit one formal model.
                                       │
                                       ▼
                                  Stage 2 (auto-mm-solving)
                                     code, baseline, main run, ablation,
                                     small-instance exact Gap, sensitivity,
                                     figures.
                                       │
                                       ▼
                                  Stage 3 (auto-mm-writing)
                                     drop into template, write each section,
                                     iterate abstract, anonymity scan,
                                     xelatex build, package submit.zip.
                                       │
                       budget left? ──yes──► loop body: incremental improvement
                       │ no
                       └──► hand `submit.zip` to user, exit.
```

## First-invocation flow

The orchestrator's job in the very first conversation:

### Step 1 — pick contest

Print exactly:

```
Which contest are you running? Pick one:

  1. MCM / ICM (COMAP 美赛 — English paper, 96 hours)
  2. CUMCM     (高教社 国赛 — 中文 paper, 72 hours)
  3. Other     (华中杯, 妈杯, 数维杯, 校赛, etc. — you'll tell me the rules)
```

Wait for the answer. Do not guess. If "other", continue to Step 2 with a sub-flow that asks the rules from `references/contest-types.md` § "Profile selection at orchestrator start".

### Step 2 — gather contest info

Ask in one batch:

```
About to set up the run. I need:

(a) Year / iteration (e.g. 2026, S4E5)
(b) Problem set offered this year (e.g. A B C for MCM, A B C D E for CUMCM)
(c) Deadline in YOUR local timezone (I'll convert to UTC)
(d) Team control number (MCM) / report number (CUMCM) / blank if N/A
(e) Have you already downloaded the problem statements and any data files?
    If yes, where? (I'll move them to runs/<slug>/inputs/)
    If no, drop them in runs/<slug>/inputs/problems/ before Stage 0 starts.
(f) Supervisor mode:
    - manual           (you invoke me each cycle)
    - claude-loop      (use /loop inside Claude Code)
    - shell-supervisor (assets/supervisor.sh outside Claude)
```

Validate: contest family known, deadline > now, problem set non-empty.

Compute provisional `run_slug = <family>-<year>-untriaged`. After Stage 0 commits a problem, slug becomes `<family>-<year>-<problem>` and the directory is renamed atomically (`mv -n`).

### Step 3 — search contest background

For MCM/CUMCM, the orchestrator should briefly research current-year contest details so the user doesn't have to recite them:

- Use WebFetch on the contest's official URL (`comap.com/contests/mcm-icm/`, `mcm.edu.cn`) to confirm this year's dates, AI report requirements, page limits.
- Record findings in `stage0_triage/contest_brief.md`.

If the contest is "other" or no official site is found, ask the user once for the unknowns and record their answer verbatim.

### Step 4 — write `run.yaml`, delegate to Stage 0

After `run.yaml` exists and `inputs/problems/` has the problem PDFs, delegate to `auto-mm-triage`. Do not start modeling without an explicit problem commitment.

### Step 5 — print supervisor instructions

Based on `run.yaml.supervisor.mode`, print exactly the start command the user needs to run. The orchestrator does not start the supervisor itself.

## Resume protocol

`auto-mm <run_slug>` always means **resume**. Procedure per `references/long-running-protocol.md`:

1. Read `runs/<run_slug>/run.yaml`. Missing → first-invocation flow.
2. Check `STOP` / `PAUSE` → exit or idle if present.
3. Read `.heartbeat`. If `pid` is alive and `ts_utc` is fresh (< 5 min), refuse to start a second agent; exit.
4. Read `progress.jsonl` tail. Compute last event per stage. Decide dispatch (see protocol doc).
5. Compute `deadline_utc - now`. If ≤ 6 hours, enter **lockdown mode** (`time-budget.md` § "Lockdown mode").
6. Read the latest `hand_off.md` of the most-advanced stage. That is the next stage's input.
7. Update `.heartbeat` at start, every 60s while running, and once at clean exit.

A fresh start requires explicit `--restart`. The orchestrator prompts once more before deleting state.

## Status-only invocation

When the user asks for status:

```bash
cat runs/<slug>/.heartbeat
tail -n 30 runs/<slug>/progress.jsonl
cat runs/<slug>/stage{0,1,2,3}_*/hand_off.md 2>/dev/null | tail -n 80
```

Print these summarized and **exit without doing any work**. No new modeling, no new experiments, no rebuild. The user is checking in, not authorizing action.

## Integrity gate (mandatory at every hand-off)

Before delegating to the next stage, the orchestrator verifies:

1. Previous stage's `hand_off.md` exists and conforms to the 3-paragraph spec (`state-contract.md`).
2. Structured files named in `hand_off.md` exist and parse.
3. The rules listed in `integrity-rules.md` § "Enforcement points" for this gate pass.
4. No `STOP` or `PAUSE` sentinel is present.
5. No unresolved escalation block in the latest `hand_off.md`.

If any check fails → escalate per `escalation-policy.md`. Do not proceed.

## State contract

Everything lives under `runs/<run_slug>/`. Full schema in `references/state-contract.md`. Skeleton:

```
runs/<run_slug>/
├── run.yaml
├── .heartbeat
├── progress.jsonl
├── STOP | PAUSE                   # sentinels
├── inputs/                        # problems/, data/, notices/
├── stage0_triage/
├── stage1_modeling/
├── stage2_solving/
├── stage3_writing/
```

## When to load which reference

Default: load nothing extra. Load the files below only when making the decision they govern.

| File | Load when |
|---|---|
| `references/state-contract.md` | Setting up `runs/<run_slug>/`, parsing an existing run, or writing any state file |
| `references/integrity-rules.md` | Before every stage hand-off (mandatory) and before producing `submit.zip` |
| `references/time-budget.md` | First invocation (setting `per_stage_hours`), every micro-step boundary (drift check), entering lockdown |
| `references/long-running-protocol.md` | On resume, on supervisor setup, when a stage skill plans to exit and yield |
| `references/contest-types.md` | First invocation (contest profile selection); when Stage 3 picks a template |
| `references/escalation-policy.md` | Any time something feels off — the question "should I escalate?" is answered here |

## Supervisor selection

The orchestrator does **not** start the supervisor itself. It tells the user how to start it, based on `run.yaml.supervisor.mode`:

- `manual` → "I will pause after each cycle. Invoke me again with `/auto-mm resume <slug>` when ready."
- `claude-loop` → "Inside Claude Code, run `/loop /auto-mm resume <slug>` to keep me cycling."
- `shell-supervisor` → "Run `nohup bash auto-mm/assets/supervisor.sh <slug> > supervisor.log 2>&1 &` to keep me running across crashes. See `supervisor.sh --help` for options."

The first invocation prints all three so the user can choose.

## Walkthrough — first 12 hours of an MCM run

1. User (Thursday 17:00 EST): `auto-mm`. Orchestrator asks: which contest → MCM. Year → 2026. Problem set → A B C. Deadline → 2026-02-09T20:00 EST. Team control number → 2603956. Language → English. Supervisor → claude-loop.
2. Orchestrator writes `runs/mcm-2026-untriaged/run.yaml`. Asks user to drop problem PDFs into `inputs/problems/`. User confirms 3 PDFs are there.
3. Orchestrator delegates to `auto-mm-triage`. Triage reads all 3 PDFs, scores them on data availability + method fit + risk + differentiator, writes `problem_choice.md` recommending C with a 3-paragraph rationale. Hand-off written.
4. User reviews and says "go with C." Orchestrator renames the run directory to `runs/mcm-2026-C/`, updates `run.yaml.chosen_problem` and `run.yaml.run_slug`. Delegates to `auto-mm-modeling`.
5. Modeling stage runs ~8 hours. Writes `assumptions.md`, `notation.md`, `candidates.md` (3 families), `model.md` (chosen: inverse-optimization + light attention model for Task 3). Hand-off written. Integrity gate passes.
6. Orchestrator delegates to `auto-mm-solving`. Solving stage codes the pipeline, runs baseline (CV consistency 0.87), runs main (CV consistency 0.91), writes 6 figures as PDF vectors. Hand-off written.
7. Orchestrator delegates to `auto-mm-writing`. Writing stage drops into EasyMCM2 template, fills out part_1_pre.tex, part_2_model.tex, part_3_conclusion.tex, iterates abstract three times. Runs xelatex twice. Anonymity scan passes. Builds `submit.zip`.
8. Orchestrator prints final summary: hours used 39/96, file at `runs/mcm-2026-C/stage3_writing/submission/submit.zip`. Asks user to inspect before hand-off.
9. User has 57 hours of buffer for revision. Orchestrator enters "incremental improvement" loop until lockdown mode at hour 90.

## Notes

- The skill is for contests with a real deadline and a real paper deliverable. For practice on retired problems, use `--practice` to skip anonymity checks and the submission package.
- The skill assumes the user is **one person using Claude as a teammate**. The state contract has no concept of multiple concurrent agents; if a 3-person team wants 3 Claude instances, they must coordinate manually by working on different `runs/` slugs.
- The skill never invents a problem PDF or a citation. If `inputs/problems/<X>.pdf` doesn't exist when Stage 0 runs, the user is asked to drop it in.
- For unsupported contest families, the skill still runs — it just leans more on the user during first-invocation Q&A.

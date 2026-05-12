# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A library of **five portable skill packages** for Claude Code (and Codex-style agents) that together drive a 72-96-hour mathematical-modeling contest from a single prompt to a packaged `submit.zip`. It is *not* a runnable application — there is no top-level build, no test suite, no `requirements.txt`. The deliverables are markdown + YAML + Python helper scripts + a shell supervisor + a LaTeX template that get copied into `~/.claude/skills/` (or `<project>/.claude/skills/`) and executed by an agent at runtime.

Implication for editing: the "code" here is prompts, workflow contracts, a LaTeX template, and a handful of Python helpers. Changes are validated by reading them and tracing the contract — not by running them inside this checkout. Real runs (contest paper compilation, model code execution) happen on the user's machine.

## The five skills and how they compose

```
auto-mm              ← orchestrator (Stage 0..3 driver, integrity gate, resume protocol)
  ├─ auto-mm-triage      ← Stage 0: pick A/B/C/D after data recon + 5-axis scoring
  ├─ auto-mm-modeling    ← Stage 1: assumptions + notation + formal model + verified citations
  ├─ auto-mm-solving     ← Stage 2: code, baseline, exact-Gap, ablation, sensitivity, figures
  └─ auto-mm-writing     ← Stage 3: LaTeX paper, anonymity scan, submit.zip
```

Each skill folder has the same shape:

- `SKILL.md` — frontmatter (`name`, `description`) + workflow. The description triggers the skill in Claude Code / Codex; keep it under 1024 chars.
- `references/*.md` — load-on-demand reference docs cited from `SKILL.md`'s "When to load which reference" table. Skills should NOT load all references upfront.
- `assets/` — concrete artifacts: helper scripts (`supervisor.sh`, `figure_style.py`, `anonymity_scan.py`), LaTeX templates (`mcm-template/`, `cumcm-template/`).
- `agents/openai.yaml` — Codex-side UI metadata only. Claude Code ignores it. When changing skill metadata, keep `SKILL.md` frontmatter and `openai.yaml` in sync.

The orchestrator never does the modeling itself; it sequences the four sub-skills and enforces the contract between them.

## State contract — do not invent paths

All inter-stage state lives under `runs/<run_slug>/` where `<run_slug>` is built as `<contest>-<year>-<problem>` once Stage 0 commits a problem (provisional: `<contest>-<year>-untriaged`). The full file schema is defined in `auto-mm/references/state-contract.md` — treat that file as authoritative. When editing any skill that reads or writes stage artifacts, cross-check it against `state-contract.md` so the contract stays consistent across all five skills.

Files every stage reads first:

- `runs/<run_slug>/run.yaml` — contest family, year, deadline, time budget, language, team
- `runs/<run_slug>/.heartbeat` — current stage/substep/ts_utc/pid (user can `cat` to peek)
- `runs/<run_slug>/progress.jsonl` — append-only micro-step log; resume reads its tail
- `runs/<run_slug>/stage{N}_*/hand_off.md` — 3-paragraph hand-off from stage N to stage N+1
- `runs/<run_slug>/inputs/problems/<X>.pdf` — the contest problem (user-supplied)

`runs/` is gitignored — never commit experimental output back into this repo.

## The long-running protocol overrides everything

`auto-mm/references/long-running-protocol.md` defines how the skill survives 72-96 hours across invocations:

- All state on disk; no agent memory crosses invocations.
- Idempotent micro-steps; re-running re-reads disk and continues.
- Append-only logs (`progress.jsonl`); never rewritten.
- Atomic file writes via `.tmp` + rename.
- Resume by default; `--restart` required for a fresh start.
- `STOP` / `PAUSE` sentinels in `runs/<run_slug>/` are honored at the top of every micro-step.
- `assets/supervisor.sh` keeps the run alive across crashes from outside Claude Code.
- Lockdown mode (last 6h) rejects new modeling/experiments; only writing/build/anonymity/packaging.

When editing any skill: every new code path must say how it satisfies (or escalates under) the long-running protocol. If a new operation is not idempotent, that is a bug.

## The 10 integrity rules override everything else

`auto-mm/references/integrity-rules.md` defines the non-negotiable rules:

1. Problem statement is authoritative (题面口径优先).
2. Anonymity is absolute (no author/school/path leaks anywhere).
3. Real citations only (every entry verified before lands in `literature.md`).
4. AI/ML modules must address real uncertainty (not replace closed-form computation).
5. Algorithms must be justified by problem structure (no metaheuristic stacking).
6. Validation is part of the deliverable (baseline / exact-Gap / ablation / sensitivity).
7. Time budget is hard (drift > 20% triggers escalation).
8. Figures are evidence, not decoration (every figure is `\ref`ed from body).
9. Abstract carries hard numbers (≥5 unique numerical claims).
10. Submission package hygiene (no `._*`, no `.DS_Store`, decompresses clean).

When editing any skill:

- Do not loosen these rules to make a workflow easier.
- Final submission is always user-driven. The orchestrator builds `submit.zip` and hands it to the user — it does not auto-submit to a portal.
- The integrity-gate checkpoints in `auto-mm/references/escalation-policy.md` are part of the contract — preserve them when touching the orchestration loop.

## Conventions when editing skills

- Keep `SKILL.md` frontmatter `description` within Claude Code's 1024-character limit and unambiguous about when to trigger.
- Examples use absolute dates and absolute UTC timestamps. Never write "today" or "yesterday" — those rot.
- The repo intentionally has both English (`README.en.md`) and Chinese (`README.zh-CN.md`) READMEs; if you change one substantively, mirror the change in the other.
- Helper scripts follow `state-contract.md` for input/output paths. Do not invent new paths.
- `.gitignore` includes `runs/`, `Template.zip`, build intermediates, `__pycache__/`, `._*`. Verify before committing.

## Working in this environment

This machine is shared and resource-constrained — it is for *editing skills and committing*, not for executing them. Do not attempt to invoke a skill end-to-end from this checkout: actual contest runs (xelatex builds, solver invocations) belong on the user's local machine. When the user wants to validate a change, list the commands they should run there rather than running them here.

## Where the experience knowledge came from

The user's prior 数模 contest experience (华中杯 A 题 retrospective) was distilled into:

- `auto-mm-modeling/references/pitfalls-from-experience.md` — the 14 named pitfalls (P1-P14).
- `auto-mm-solving/references/figure-quality.md` — figure design rules (no in-figure titles, PDF vectors, restrained palette).
- `auto-mm-solving/references/sensitivity-analysis.md` — sensitivity for insight, not filler.
- `auto-mm-writing/references/abstract-writing.md` — three-pass abstract protocol with hard-number floor.
- `auto-mm-writing/references/submission-package.md` — macOS metadata filtering, supporting-material layout.

The original retrospective is preserved at `README_数学建模比赛工作流.md` for reference; the references above are the actionable form. If a future contest produces new lessons, distill them back into these references — don't accumulate retrospective files.

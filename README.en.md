# auto-mm — Mathematical-Modeling Contest Automation Skill Suite

A set of Claude Code skills that drive a mathematical-modeling contest from "we have a problem statement" all the way to a packaged `submit.zip`, surviving the full 72-96-hour window. Two contest profiles are wired in: **MCM/ICM** (English, 96h) ships with a bundled EasyMCM2 LaTeX scaffold; **CUMCM** (中文 national contest, 72h) is supported but bring-your-own-template — the 高教社 template changes year to year and license terms vary, so the user drops the year's official template into `auto-mm-writing/assets/cumcm-template/` at first invocation. Derivative profiles (华中杯 / 妈杯 / 数维杯 / campus contests) inherit from the closest match.

## What this is

Not a runnable application, but **five portable skill packages**. Drop them into `~/.claude/skills/` (or `<project>/.claude/skills/`) and Claude Code will execute the contest workflow.

```
auto-mm                ← orchestrator (Stage 0..3 driver, integrity gate, resume protocol)
  ├─ auto-mm-triage      ← Stage 0: pick A/B/C/D after data recon + 5-axis scoring
  ├─ auto-mm-modeling    ← Stage 1: assumptions + notation + formal model + verified citations
  ├─ auto-mm-solving     ← Stage 2: code, baseline, exact-Gap, ablation, sensitivity, figures
  └─ auto-mm-writing     ← Stage 3: LaTeX paper, anonymity scan, submit.zip
```

## Why this exists

Math-modeling contests differ from both Kaggle and research:

| Axis | Kaggle | Research | 数模 contest |
|---|---|---|---|
| Duration | weeks-months | weeks-months | **72-96 hours, hard** |
| Iterative feedback | public LB + daily quota | none | **none** (expert review months later) |
| Deliverable | submission.csv | paper | **paper (template-bound) + supporting material** |
| Problem | 1 fixed | 1 self-chosen | A/B/C/D **pick one** of open-ended real-world questions |

The clock is the only opponent; the paper is the only artifact. This skill suite forces those facts into every stage.

## How to trigger

After copying `auto-MM/` into `~/.claude/skills/`, say one of:

- `刷数模` / `auto mm` / `auto-mm`
- `开始数模比赛` / "start math modeling"
- `继续刷 mcm-2026-C` / `resume <run_slug>`
- `status of my <run_slug>` — read-only status, never triggers new work

First invocation asks:

1. Which contest? (MCM | CUMCM | other)
2. Year, problem set, deadline (your local timezone, converted to UTC)
3. Team control number / 报名号
4. Where are the problem PDFs?
5. Supervisor mode (manual / claude-loop / shell-supervisor)

Then writes `runs/<run_slug>/run.yaml` and begins Stage 0.

## High-level flow

```
                  ┌──────────────────────────────────────────────────────────┐
                  │           auto-mm  (this skill — orchestrator)           │
                  └──────────────────────────────────────────────────────────┘
                                       │
        First invocation? ──yes──►  Ask: contest? (MCM | CUMCM | other)
                                       │   Ask: deadline, problem set, control#, language, supervisor
                                       │   Write run.yaml. mkdir runs/<slug>/
                                       ▼
                                  Stage 0 (auto-mm-triage)
                                     index problems, recon data,
                                     score 5 axes, wait for user lock-in
                                       │
                                       ▼
                                  Stage 1 (auto-mm-modeling)
                                     decomposition, assumptions, notation,
                                     candidate models, commit one formal model
                                       │
                                       ▼
                                  Stage 2 (auto-mm-solving)
                                     pipeline.py, baseline, main run, small-instance
                                     exact Gap, ablation, sensitivity, figures
                                       │
                                       ▼
                                  Stage 3 (auto-mm-writing)
                                     fill the LaTeX template, three-pass abstract,
                                     xelatex × 2, anonymity scan, package submit.zip
                                       │
                                       └──► hand submit.zip + main.pdf to the user
```

## The 10 non-negotiable integrity rules

Defined in `auto-mm/references/integrity-rules.md`, enforced at every stage hand-off:

1. **Problem statement is authoritative** — if the problem says 30 customers, the main model uses 30; the 10 km radius is sensitivity, not main.
2. **Anonymity is absolute** — zero tolerance for author/school/`/Users/<name>` leakage in PDF metadata, body, or source listings.
3. **Real citations only** — every entry in `references.bib` is verified via DOI / arXiv ID / stable URL before it lands.
4. **AI/ML modules must address real uncertainty** — no neural network to "predict" a value the cost function can compute directly.
5. **Algorithms must be justified by problem structure** — no SA+TS+GA+DRL stacking; each component must name the problem feature it addresses.
6. **Validation is part of the deliverable** — baseline + small-instance exact Gap + ablation + sensitivity, at least three of the four.
7. **Time budget is hard** — stage drift > 20% triggers user escalation (cut scope / steal from later stage / extend total).
8. **Figures are evidence, not decoration** — every figure is `\ref`-ed from body text; AI-flavored palettes are flagged.
9. **Abstract carries hard numbers** — ≥5 unique numerical claims; "we built a model and obtained good results" is rejected.
10. **Submission package hygiene** — no `._*`, `.DS_Store`, `~$*`, `__pycache__/` in the zip; decompresses cleanly.

## State contract — the inter-stage interface

Full schema in `auto-mm/references/state-contract.md`. Skeleton:

```
runs/<run_slug>/
├── run.yaml                       # contest meta + time budget + chosen problem
├── .heartbeat                     # JSON: {stage, substep, ts_utc, pid}
├── progress.jsonl                 # append-only micro-step log
├── STOP | PAUSE                   # sentinels
├── inputs/
│   ├── problems/                  # A.pdf B.pdf ...
│   ├── data/                      # attachment data
│   └── notices/                   # organizer errata
├── stage0_triage/
├── stage1_modeling/
├── stage2_solving/
└── stage3_writing/
```

Every stage's `hand_off.md` has the same 3-paragraph structure:
1. **What I did** — artifacts written, with paths.
2. **What's true now** — facts the next stage should act on.
3. **What you should do next** — directive to the next stage skill.

The next stage **only reads** `hand_off.md` + the structured files it cites.

## Long-running protocol — surviving crashes and context resets

`auto-mm/references/long-running-protocol.md`:

- All state on disk; nothing crosses invocations in memory.
- Micro-steps are idempotent — re-running re-reads disk and continues past completed ones.
- Append-only logs (`progress.jsonl`); never rewritten.
- Atomic writes (`.tmp` + rename).
- Resume by default; explicit `--restart` for a fresh start.
- `STOP` / `PAUSE` sentinels checked at the top of every micro-step.
- `assets/supervisor.sh` keeps the run alive outside Claude Code.
- **Lockdown mode** (last 6h): no new modeling/experiments; only writing, building, anonymity, packaging.

## Lessons distilled from past contests

The author's past 华中杯 A 题 retrospective (a private document, not in this repo) was distilled into actionable references:

- `auto-mm-modeling/references/pitfalls-from-experience.md` — 14 named pitfalls P1-P14.
- `auto-mm-solving/references/figure-quality.md` — figure design rules (no in-figure titles, PDF vectors, restrained palette).
- `auto-mm-solving/references/sensitivity-analysis.md` — sensitivity for insight, not figure-padding.
- `auto-mm-writing/references/abstract-writing.md` — three-pass abstract protocol with hard-number floor.
- `auto-mm-writing/references/submission-package.md` — macOS metadata filtering, supporting-material layout.

The retrospective itself is kept locally by the author (gitignored); the references above are the executable form. When a future contest produces new lessons, distill them back into these references — don't accumulate retrospectives.

## File layout

```
auto-MM/
├── README.md  README.en.md  README.zh-CN.md
├── CLAUDE.md  .gitignore
├── auto-mm/                       # orchestrator
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/supervisor.sh
│   └── references/
│       ├── state-contract.md
│       ├── integrity-rules.md
│       ├── time-budget.md
│       ├── long-running-protocol.md
│       ├── escalation-policy.md
│       └── contest-types.md
├── auto-mm-triage/                # Stage 0
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── problem-selection-rubric.md
│       ├── data-recon-checklist.md
│       └── contest-typology.md
├── auto-mm-modeling/              # Stage 1
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── model-zoo.md
│       ├── notation-style.md
│       ├── assumption-writing.md
│       ├── pitfalls-from-experience.md
│       └── citation-discipline.md
├── auto-mm-solving/               # Stage 2
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/figure_style.py
│   └── references/
│       ├── algorithm-selection.md
│       ├── figure-workflow.md
│       ├── figure-brief-template.md
│       ├── figure-prompt-patterns.md
│       ├── figure-quality.md
│       ├── sensitivity-analysis.md
│       └── validation-protocol.md
└── auto-mm-writing/               # Stage 3
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/
    │   ├── mcm-template/          # EasyMCM2 placeholder scaffold (DWTS content stripped)
    │   ├── cumcm-template/        # placeholder — drop the year's template on first run
    │   ├── anonymity_scan.py      # PDF + .tex/.bib forbidden-pattern scanner
    │   └── build.sh               # xelatex two-pass build with structured log
    └── references/
        ├── abstract-writing.md
        ├── section-checklist.md
        ├── anonymity-check.md
        ├── latex-build.md
        ├── submission-package.md
        └── ai-report-mcm.md
```

## Contributing

This repo's content is **prompts + workflow contracts + one LaTeX template**, not executable code. When editing:

- After editing `SKILL.md`, sync `agents/openai.yaml`'s `description`.
- When changing `auto-mm/references/state-contract.md`, cross-check all five skills so the contract stays consistent.
- If you change one language's README, mirror the other.
- To test: copy the skills into `~/.claude/skills/`, open Claude Code, trigger via one of the phrases, and walk a real contest run.

## License

TBD. The EasyMCM2 template's license follows its upstream author.

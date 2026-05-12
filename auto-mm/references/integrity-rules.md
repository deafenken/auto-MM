# Integrity rules — non-negotiable

These are the rules that override convenience, speed, and even the user's in-the-moment request when they conflict. The orchestrator enforces them at every hand-off and refuses to proceed if any is violated.

## Rule 1 — Problem statement is authoritative

If the problem statement says X and a derivation, a clever simplification, or an external source says Y, the paper uses X. Disagreement is recorded in `stage1_modeling/assumptions.md` with an explicit "we adopt the problem-statement value of X; we treat Y as a sensitivity case." Never silently substitute.

This is the most common high-impact mistake. The 华中杯 A 题 retrospective (`README_数学建模比赛工作流.md` §2) calls this out specifically: "30 个绿色区客户" vs "10 km 半径" disagreement → main model follows the problem statement's customer count, the radius case becomes sensitivity analysis.

## Rule 2 — Anonymity is absolute

The submitted PDF, the LaTeX sources, every figure, every embedded code listing, and every PDF metadata field **must contain zero personally-identifying information**. No author names, schools, advisor names, OS usernames in paths, conference team names, or git remote URLs. Stage 3 writing runs the automated anonymity scan from `auto-mm-writing/references/anonymity-check.md` and refuses to produce a `submit.zip` until it passes clean.

A single leaked username in a code-listing path is enough to disqualify. There is no manual override.

## Rule 3 — Real citations only

Every entry in `references.bib` must point to a paper, book, official policy, or dataset that actually exists and is findable via DOI, arXiv ID, or a stable URL. The orchestrator will not let a fabricated citation reach the final paper. If a fact needs support and no real source is found, the fact is removed or restated as the team's own assumption.

Specifically forbidden: hallucinated journal volumes, made-up author lists, "et al." citations to non-existent papers. Real source > weak source > no source > fake source.

## Rule 4 — AI/ML modules must address real uncertainty

A neural network, attention mechanism, gradient-boosted model, etc. is only justifiable if it solves a problem that cannot be solved by exact computation against the model. Predicting a quantity that the cost function can compute directly is not a justification.

Acceptable: predicting next-day demand, classifying ambiguous text intents, learning a heuristic policy where the exact problem is intractable.
Not acceptable: training a classifier to "predict" the value of a closed-form expression.

This is the §6 lesson from the experience README. The orchestrator pings this rule any time `stage1_modeling/candidates.md` proposes deep learning.

## Rule 5 — Algorithms must be justified by problem structure

Stacking SA + TS + GA + DRL without explaining what each component handles is a red flag, not a strength. `stage1_modeling/candidates.md` must list (algorithm) → (specific problem feature it addresses). The orchestrator rejects a `model.md` that names ≥3 metaheuristics without per-component justification.

When in doubt: smaller hammer, stronger ablation.

## Rule 6 — Validation is part of the deliverable, not optional

A `stage2_solving/runs/main/` without at least one of:
- baseline comparison (a deliberately weaker method),
- small-instance exact solve with reported optimality gap,
- ablation on the most important architectural choice,
- sensitivity analysis on the most fragile parameter,

is treated as incomplete. The writing stage will refuse to advertise headline numbers that lack this scaffolding in `validation.md` / `sensitivity.md`.

## Rule 7 — Time budget is a hard constraint

Stage budgets in `run.yaml.budget.per_stage_hours` are not aspirational. When a stage exceeds its budget by >20%, the orchestrator opens an escalation block in `recommendations.md` and asks the user whether to (a) cut scope, (b) re-allocate from a later stage, or (c) extend total budget. The default action on no-response is **cut scope of the current stage**, because writing time is the most unrecoverable.

The final 6 hours before deadline switch into **lockdown mode** — no new modeling, no new experiments, only writing, building, checking, and packaging. This rule overrides any user request for new analysis in the final 6 hours unless the user explicitly types "override lockdown."

## Rule 8 — Figures are evidence, not decoration

Every figure in the paper must be referenced in body text and must answer a question the reader has at that point. Orphan figures (`\includegraphics` with no `\ref` in surrounding text) are blockers in the section checklist. AI-flavored color palettes (high-saturation purple-blue gradients, generic flowchart art) are flagged; PDF vector preferred over PNG.

This rule maps directly to §7 of the experience README. The writing stage's build_log greps for unreferenced `\label{fig:...}`.

## Rule 9 — Abstract carries hard numbers

The abstract must contain (a) one sentence on problem type and overall approach, (b) one short paragraph per sub-problem with model, algorithm, and **concrete results** (numbers, percentages, comparisons), (c) management insight. An abstract that says only "we built a model and achieved good results" is rejected by Stage 3.

## Rule 10 — Submission package hygiene

The final `submit.zip` must:
- contain only the files the contest expects (paper PDF, code, supporting material as the rubric demands),
- exclude `._*`, `.DS_Store`, `~$*`, editor backups, `.git/`, build intermediates,
- decompress without errors on a clean machine,
- be smaller than the contest's max upload size if specified.

The orchestrator runs `unzip -l submit.zip` and a forbidden-pattern scan before declaring done.

---

## Enforcement points

These rules are checked at five gates:

| Gate | Where | Rules checked |
|---|---|---|
| Stage 0 → 1 | `auto-mm-triage` hand-off | 1, 7 |
| Stage 1 → 2 | `auto-mm-modeling` hand-off | 1, 3, 4, 5, 7 |
| Stage 2 → 3 | `auto-mm-solving` hand-off | 6, 7, 8 |
| Stage 3 build | each `xelatex` run | 8 (orphan figs/labels) |
| Stage 3 ship | before writing `submit.zip` | 2, 8, 9, 10 |

When a rule fails, the offending stage's skill writes an `escalation` block into its `hand_off.md` and the orchestrator pauses for user input per `escalation-policy.md`.

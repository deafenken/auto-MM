# Problem selection rubric — 5 axes, scored -2 to +2 each

The triage stage uses this rubric to score every candidate problem. The rubric is intentionally short — too many axes water down the signal.

## Axis 1: Data sufficiency

Does the data shipped with the problem (or trivially obtainable) answer the question?

| Score | Meaning |
|---|---|
| +2 | Data is complete, clean enough, and directly maps to the model's I/O. No external collection needed. |
| +1 | Data is mostly there; one or two derived features or a small external lookup are needed. |
| 0 | Data is partial; need 4-8 hours of cleaning, joining, or external API calls. |
| -1 | Heavy data collection / scraping required; significant risk of running out of time. |
| -2 | Problem essentially asks you to find the data yourself. Avoid in a 72-96h window. |

Common red flags: "based on publicly available sources, …", "you may need to estimate …", "data not provided, identify your own."

## Axis 2: Method fit

Can the user implement a defensible method in the time available?

| Score | Meaning |
|---|---|
| +2 | Maps to a method the user has implemented before; reusable code likely exists. |
| +1 | Maps to a well-documented method; first-time implementation is feasible. |
| 0 | Method is identifiable but non-trivial (e.g., a niche optimization variant, a custom PDE). |
| -1 | Method requires expertise the user is acquiring under deadline pressure. |
| -2 | Method is research-level (e.g., bespoke RL, novel architecture). Demands more than the contest window. |

Don't confuse "method fit" with "easy." A well-fit problem can still be deep — the point is that the path from problem to defensible result is clear.

## Axis 3: Risk

Ambiguity, edge cases, hidden traps. Higher is safer.

| Score | Meaning |
|---|---|
| +2 | Statement is precise; no ambiguous terms; sub-questions are well-isolated. |
| +1 | Mostly clear; one or two clarifications needed but answerable from context. |
| 0 | Some ambiguity in scope or definitions; requires team interpretation. |
| -1 | Multiple terms with no shared definition (e.g., "fairness", "efficiency" undefined). |
| -2 | Trap-laden: contradictory constraints, unstated assumptions, "find a creative approach" tone. |

The 华中杯 retro called out the "30 customers vs 10 km radius" disagreement as a hidden ambiguity. That's a -1 in this axis even if the rest is clean.

## Axis 4: Differentiator

Is there room for a technique that lifts the paper above competent-but-ordinary?

| Score | Meaning |
|---|---|
| +2 | Problem naturally invites a sophisticated method (MILP+ALNS, inverse optimization, attention model with interpretable weights, Bayesian network) that judges value. |
| +1 | Room for one non-obvious twist (e.g. a sensitivity analysis structured as a Pareto front). |
| 0 | Reasonable methods are all standard; the paper will be judged on rigor not novelty. |
| -1 | Hard to differentiate; most teams will produce nearly identical papers. |
| -2 | Problem is so well-defined that the "best" approach is unique; ranking comes down to typography. |

Don't confuse differentiator with "fancy." A simple model defended brilliantly with sensitivity + small-instance exact verification is also a differentiator.

## Axis 5: Team familiarity

Does the user / team have a head start in this domain?

| Score | Meaning |
|---|---|
| +2 | Strong prior context — coursework, internship, or previous contest in the same domain. |
| +1 | Adjacent context (e.g. user is a CS student, problem is a CS-flavored optimization). |
| 0 | Neutral. |
| -1 | Domain is foreign (e.g. epidemiology problem for a non-bio team). |
| -2 | Domain has heavy jargon that takes hours to look up. |

Ask the user explicitly if uncertain. The orchestrator's intuition is not enough — the user knows their team.

## Axis 6: Skill leverage

Does **this skill suite** (auto-mm's model-zoo recipes, the figure pipeline, the integrity gates, the EasyMCM2 scaffold, prior contest pitfalls) give a meaningful edge on this problem? Full evaluation guide in `references/skill-leverage-rubric.md`.

| Score | Meaning |
|---|---|
| +2 | Problem matches a recipe auto-mm has machinery for (MILP+ALNS routing, inverse optimization, forecast→optimize two-stage, attention-for-interpretability). The gates and figure channels carry real weight. |
| +1 | Most of the work is in scope; minor adaptation needed. |
| 0 | Skill is neutral — useful as guard rail, not as engine. Bespoke code dominates. |
| -1 | Skill helps only marginally; domain-specific libraries are not bundled. |
| -2 | Skill is the wrong shape for this problem (essay-style policy, pure literature survey, heavy bespoke domain). Recommend declining. |

This axis is the orchestrator's hat in the ring — it's the difference between "we can finish this" and "we can win something on this."

Ask `skill-leverage-rubric.md` for the per-sub-skill worksheet (4 partials summed and rounded). The worksheet helps avoid scoring on vibes.

## Aggregation

Sum the six axes. Range: -12 .. +12. Tie-break (in order):

1. **Higher Skill-leverage wins** — when two problems are within ±1 of each other on total, the higher-leverage one is the auto-mm pick. This is the rubric's whole point in the v2 form: bias the initial selection toward where the skill earns its medals.
2. Higher Risk axis wins (lower-risk problem preferred).
3. Higher Data Sufficiency wins.
4. Ask the user.

A total ≤ 0 is a warning sign — recommend the least-bad option but flag the risk and ask explicitly.

## What this rubric is NOT

- It is not a guarantee. A +9 problem with a missing data file becomes a -3 next morning. Re-score is allowed within the first 6 hours of the contest.
- It is not a predictor of award tier in isolation. It is a predictor of "can we finish a defensible paper on this AND has this skill suite given us an edge on it." Final award tier still depends on execution.
- It is not weighted by score — each axis is equal-weight to keep the surface readable. Skill-leverage only gets its boost via the tiebreaker, not via a multiplier.

## Example: 2025 MCM Problem A vs B for a 3-person CS team

| Axis | A (transport optimization) | B (epidemic forecast) |
|---|---|---|
| Data sufficiency | +1 (lat/long + flow shipped) | -1 (need WHO data manually) |
| Method fit | +2 (VRP variant, prior code) | -1 (SEIR + Bayesian, first time) |
| Risk | +1 (clear sub-questions) | -1 ("characterize uncertainty" is vague) |
| Differentiator | +1 (ALNS + carbon-aware) | +1 (uncertainty quantification) |
| Team familiarity | +2 (CS) | -1 (no bio context) |
| **Skill leverage** | **+2** (VRP in model-zoo + ALNS scaffold + route-map figure pipeline) | **-1** (PDE + Bayesian recipes are stubs only) |
| **Total** | **+9** | **-4** |

Recommendation: A. Hand off the modeling stage with a hard "do not change to B." The +3 spread on Skill-leverage alone would have flipped the call even if the other axes had been close.

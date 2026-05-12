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

## Aggregation

Sum the five axes. Range: -10 .. +10. Tie-break:

1. Higher Risk axis wins (lower-risk problem preferred).
2. Higher Data Sufficiency wins.
3. Ask the user.

A total ≤ 0 is a warning sign — recommend the least-bad option but flag the risk and ask explicitly.

## What this rubric is NOT

- It is not a guarantee. A +7 problem with a missing data file becomes a -3 next morning. Re-score is allowed within the first 6 hours of the contest.
- It is not a predictor of award tier. It is a predictor of "can we finish a defensible paper on this in time." Award tier depends on execution.
- It is not weighted. Equal-weight is intentional — judging the relative importance of axes adds noise.

## Example: 2025 MCM Problem A vs B for a 3-person CS team

| Axis | A (transport optimization) | B (epidemic forecast) |
|---|---|---|
| Data sufficiency | +1 (lat/long + flow shipped) | -1 (need WHO data manually) |
| Method fit | +2 (VRP variant, prior code) | -1 (SEIR + Bayesian, first time) |
| Risk | +1 (clear sub-questions) | -1 ("characterize uncertainty" is vague) |
| Differentiator | +1 (ALNS + carbon-aware) | +1 (uncertainty quantification) |
| Team familiarity | +2 (CS) | -1 (no bio context) |
| **Total** | **+7** | **-3** |

Recommendation: A. Hand off the modeling stage with a hard "do not change to B."

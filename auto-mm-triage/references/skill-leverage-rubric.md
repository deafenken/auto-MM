# Skill leverage rubric — how much does THIS skill suite tilt this problem toward an award?

The 5-axis rubric measures whether a team *can* finish a defensible paper. This 6th axis measures whether **this particular skill suite (auto-mm + the bundled templates, references, helpers, and prior experience)** gives a meaningful edge on this problem. Two problems with identical 5-axis scores may differ wildly here, and that difference is exactly where the auto-mm wins go to.

This axis is scored -2 to +2 like the others, and contributes to the total. When two candidate problems tie within ±1 on total score, **the higher Skill-leverage problem wins** — it's the tiebreaker the orchestrator applies before falling back on Risk.

## How auto-mm earns leverage (by sub-skill)

| Sub-skill | What it does best | Where leverage is highest |
|---|---|---|
| `auto-mm-triage` | 5+1-axis problem scoring, data recon, locked decision with audit trail | Multi-problem contests (A/B/C/D) where wrong-problem-picked is the dominant failure mode |
| `auto-mm-modeling` | model-zoo (MILP+ALNS, inverse opt, attention-for-interpretability, Bayesian recipes), assumption discipline, notation grep, verified citations | Problems where the model family is in the model-zoo and the math needs to be defended notation-by-notation |
| `auto-mm-solving` | pipeline.py scaffold + baseline + small-instance exact Gap + ablation + sensitivity (3-of-4 enforced), figure pipeline (data + schematic + sourced) | Problems where validation discipline differentiates papers — i.e., almost all of them, but especially optimization variants |
| `auto-mm-writing` | EasyMCM2 scaffold (placeholder), 3-pass abstract with hard-number floor, anonymity scan, submission-package hygiene | All MCM/ICM runs; about half of CUMCM runs (depending on whether the user dropped in a CUMCM template) |

## High-leverage problem patterns (where +1/+2 typically lands)

Problems whose typology (per `contest-typology.md`) and concrete shape match what auto-mm has explicit machinery for:

### Vehicle routing / scheduling with structural constraints
- Tags: `optimization-discrete`, sometimes `mixed` with a forecast component.
- Leverage: `auto-mm-modeling`'s model-zoo (MILP+ALNS recipe) + `auto-mm-solving`'s ALNS scaffold + exact-Gap validation + multi-figure pipeline (route map / Gantt / convergence / sensitivity on cost terms).
- Signal: problem says "schedule", "route", "assign", "min cost", "capacity", with side constraints (time windows, green zones, fleets).
- Indicative score: **+2**.

### Inverse problems — recover latent quantities from observations
- Tags: `inference-statistical` (often mixed with light ML).
- Leverage: `auto-mm-modeling`'s inverse-opt recipe + `auto-mm-solving`'s small-instance recovery validation + the attention-mechanism interpretability recipe for the "explain what we recovered" sub-question.
- Signal: problem says "infer", "estimate hidden", "reconstruct", "given outcomes determine the causes".
- Indicative score: **+2**.

### Forecasting + downstream optimization
- Tags: `forecasting` + `optimization-discrete` (a two-stage problem).
- Leverage: GBM/LightGBM baseline + handoff into MILP. The two-stage stochastic-programming recipe in model-zoo glues forecast → optimization cleanly.
- Signal: "predict next-period demand, then decide", "scenario-based planning".
- Indicative score: **+2**.

### Multi-criteria policy with sensitivity analysis
- Tags: `policy-open` + `optimization-continuous` blend.
- Leverage: MCDA recipe + `auto-mm-solving`'s sensitivity pipeline + the writing stage's executive memo discipline.
- Signal: "evaluate a policy", "recommend with stakeholder trade-offs", "compare alternatives across dimensions".
- Indicative score: **+1** to **+2** (writing-stage memo discipline is a real edge for these).

### Classification on small datasets with cross-validation requirement
- Tags: `classification`.
- Leverage: GBM baseline + calibration plots + cross-validation discipline. The skill enforces the "tabular GBM beats DL on small N" Rule 4 mindset.
- Signal: classify items into known categories, dataset is small to medium.
- Indicative score: **+1**.

## Lower-leverage problem patterns (where 0/-1/-2 land)

Problems where auto-mm's machinery is generic — not actively hurting, but not adding much either:

### Heavy PDE / continuum mechanics
- Tags: `optimization-continuous` with PDE constraints, or pure simulation.
- Leverage drain: model-zoo has only a stub for PDE; the writing stage's typesetting handles equations fine but the modeling and solving stages will need bespoke code most of the way.
- Indicative score: **-1** to **0**.

### Agent-based simulation as the core deliverable
- Tags: `simulation-agent`.
- Leverage drain: `auto-mm-solving` does not bundle SimPy / Mesa templates. The figure pipeline still helps (agent traces, density plots), but the model and solving are mostly bespoke.
- Indicative score: **-1**.

### Pure literature-review or policy-essay-style problem
- Tags: `policy-open` with no quantitative model demanded.
- Leverage drain: the integrity gates fire on "no validation, no sensitivity" repeatedly. The skill is the wrong shape for this.
- Indicative score: **-2**. *Recommend declining or switching to a different problem.*

### Time-series with strict statistical hypothesis-testing focus
- Tags: `forecasting` with required tests (Granger causality, cointegration, structural breaks).
- Leverage drain: model-zoo lists statsmodels but does not bundle test recipes. Writing-stage table formatting is fine. Net: small win.
- Indicative score: **0**.

### Heavy bespoke domain (e.g. specific medical imaging modality, niche financial derivatives)
- Tags: any.
- Leverage drain: domain-specific libraries are not in the scaffold; significant code-from-scratch needed.
- Indicative score: **-1** to **-2** depending on the user's domain background.

## Per-sub-skill leverage worksheet

When scoring, ask one question per sub-skill and sum the partials. Final Skill-leverage axis = round(sum / 4) clamped to [-2, +2].

| Sub-skill | Question | Partial range |
|---|---|---|
| triage | Does the multi-problem decision genuinely help here? (Always +1 for A/B/C/D contests; 0 for single-problem ones since triage is moot.) | 0..+1 |
| modeling | Is the chosen model family already in the model-zoo with a recipe? Are the integrity rules (1, 3, 4, 5) easy to satisfy here? | -2..+2 |
| solving | Will the baseline + exact-Gap + ablation + sensitivity pipeline produce real evidence? Are the figure types covered by the figure-pipeline channels? | -2..+2 |
| writing | Does the EasyMCM2 / CUMCM template structure naturally fit this problem's required sections (abstract with numbers, sensitivity section, AI-report)? | 0..+2 |

Sum / 4 → round → clamp. Example: 1 + 2 + 2 + 1 = 6 / 4 = 1.5 → +2.

## How this axis interacts with the others

- **High leverage + high method fit**: classic green flag; pick it.
- **High leverage + high risk**: still pickable if total ≥ +4. The skill's enforcement gates help bound the risk.
- **High leverage + low team familiarity**: surprisingly OK. The skill carries enough domain prior that an unfamiliar team can still ship — but ramp up will eat 1-2h of buffer.
- **Low leverage + high method fit**: the team knows what they're doing, but the skill won't help as much. Still pickable; the orchestrator's role is more "guard rail" than "engine."
- **Low leverage + low method fit**: skip if there's any alternative.

## Worked re-scoring example (2024 MCM hypothetical)

| Axis | Problem A (transport VRP) | Problem B (epidemic SEIR) | Problem D (medical imaging classification) |
|---|---|---|---|
| Data sufficiency | +1 | -1 | +1 |
| Method fit | +2 | -1 | +1 |
| Risk | +1 | -1 | -1 |
| Differentiator | +1 | +1 | +1 |
| Team familiarity | +2 | -1 | 0 |
| **Skill leverage** | **+2** (VRP is in model-zoo + ALNS scaffold + route-map figure pipeline) | **-1** (SEIR needs PDE + Bayesian recipe stubs) | **0** (GBM baseline OK, but imaging-specific augmentation is not bundled) |
| **Total** | **+9** | **-4** | **+2** |

Recommendation: A. Lock in. The skill-leverage spread between A (+2) and D (0) is what makes A the obvious pick even before counting the other axes.

## Honesty caveat

This rubric is a planning tool, not a guarantee. A +2 Skill-leverage problem with bad execution still loses to a 0-leverage problem with disciplined execution. The point of the axis is to bias the *initial selection* toward problems where the skill suite's gates and recipes pay dividends — not to substitute for the work.

When in doubt: a problem the team can clearly explain to a non-expert wins over a problem with higher Skill-leverage but unclear deliverables. Skill-leverage is a tiebreaker, not a thesis.

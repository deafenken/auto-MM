# Validation protocol — what counts as adequate per Rule 6

A `main` result without validation is a number, not a finding. This file is the minimum bar.

## The four kinds of validation

A `validation.md` must contain **at least three of these four**, with one being either exact-Gap or ablation:

1. **Baseline comparison** — a deliberately weak method shows that the main model is doing nontrivial work.
2. **Small-instance exact Gap** — solve a sub-problem with an exact solver and report the gap to the heuristic's solution.
3. **Ablation** — remove the most-important architectural choice and re-run; the marginal contribution is the ablation delta.
4. **Cross-method comparison** — compare against ≥2 well-known alternatives (e.g., GA, TS, SIH) on the same data.

If the model is not amenable to (2) (e.g., it's an inference problem with no obvious exact comparator), substitute with (4).

## Baseline — design rules

The baseline is **not** a strawman. It should be:

- **Implementable in <1 hour.** If you're spending 4 hours on the baseline, you're not building a baseline.
- **Defensible.** A non-expert reader should understand why this baseline is a reasonable first attempt.
- **The same problem.** Same data, same metric, same constraints — only the method differs.

Common baselines:

| Problem type | Baseline |
|---|---|
| Routing | Greedy nearest-neighbor + 2-opt |
| Scheduling | First-Fit-Decreasing |
| Bin packing | First-Fit-Decreasing |
| Forecasting | Naive (last value), or seasonal mean |
| Classification | Logistic regression with default hyperparameters |
| Inference | MAP with uniform prior |
| Network flow | Single-commodity min-cost flow |

A baseline that scores within 2% of the main result is a problem: either the main model isn't doing much, or the baseline is too good. Investigate.

A baseline 30%+ worse than main is healthy. 5-15% gap is the typical range to report.

## Exact Gap — the gold-standard validation

Pick a sub-problem small enough that an exact solver (Gurobi, CBC, CP-SAT, OR-Tools) can solve to provable optimality in ≤10 minutes:

- VRP / TSP: 10-15 customers.
- Scheduling: 8-12 jobs, 2-3 machines.
- Bin packing: 20-30 items.
- LP / convex: no size limit; solve at full scale.

Run the heuristic on the same instance with the same constraints. Report:

```
Exact optimum:        184320.0 (Gurobi, 47.3s wall)
Heuristic on same:    187214.0 (ALNS 3000 iters, 31.2s wall)
Gap = (187214 - 184320) / 184320 = 1.57%
```

A heuristic Gap of 0-3% on small instances suggests the heuristic is well-designed. 5-10% is acceptable but warrants discussion. >15% is a red flag — the heuristic is likely missing a feature.

## Ablation — choosing the right thing to remove

The ablation matters most when it tests **the model's distinguishing claim**.

If your model is "ALNS with a problem-specific destroy operator," the ablation is:
- Variant A: ALNS without the problem-specific operator (only generic ones).
- Variant B: full ALNS with the problem-specific operator.
- Compare A vs B.

If your model is "attention-based feature interpretation + base regressor," the ablation is:
- Variant A: base regressor alone (no attention).
- Variant B: with attention.
- Compare.

Avoid trivial ablations ("we removed dropout"). The ablation should test a structural choice, not a hyperparameter.

For paper-worthy ablation, run on the **same instance** as the main result so numbers are directly comparable.

## Cross-method comparison

When exact Gap is infeasible (e.g. very large continuous problem, novel inference), compare to ≥2 well-known alternatives:

| Family | Alternatives to compare |
|---|---|
| Routing heuristic | GA, TS, vanilla SA, Solomon's I1 |
| GBM | Logistic regression, random forest, single decision tree |
| Bayesian inference | MAP, MLE with bootstrap |
| Forecasting | ARIMA, ETS, naive |
| Classification (DL) | GBM, logistic regression |

Report the same metric for each. The narrative is: "our method matches/exceeds well-known alternatives in this setting."

## Reporting in `validation.md`

```markdown
# Validation — <run_slug>

## Baseline (greedy nearest-neighbor + 2-opt)
- Instance: official-full (62 customers, heterogeneous fleet).
- Primary metric: total cost = 217,400 元.
- Wallclock: 4.2 s.

## Main (ALNS + problem-specific destroy)
- Same instance.
- Primary metric: total cost = 184,320 元.
- Wallclock: 412.3 s.
- Improvement over baseline: 33,080 元 (15.2%).

## Small-instance exact Gap (Gurobi, 12 customers)
- Exact optimum: 38,720 元 (47.3 s).
- Main on same instance: 39,330 元 (31.2 s).
- Gap: 1.58%.

## Ablation: problem-specific destroy operator
- With operator (main): 184,320 元.
- Without operator (random + worst destroy only): 198,140 元.
- Operator marginal contribution: 13,820 元 (7.5%).
- Interpretation: the green-zone-aware destroy operator unlocks ~half of
  our improvement over baseline, by enabling vehicle-type swaps in the
  policy-constrained region.
```

This is the template. Substitute numbers for the actual problem.

## When validation reveals something bad

If validation shows the main model is worse than baseline, or the ablation says the "core" component contributes nothing — **report it honestly**. Two things can happen:

1. Re-investigate the model (most useful in early hours of Stage 2).
2. Honestly write the negative finding (most useful in late hours; turns into a "limitations" discussion).

Do not hide. The orchestrator's integrity gate does not care about the sign of the result, only that validation was performed and reported.

## When validation is not possible

For some problems (open-ended policy, agent-based simulation), classical validation doesn't apply cleanly. Substitute:

- Stability: re-run with different random seeds; report variance.
- Calibration: simulate with known ground-truth parameters; recover them.
- Cross-validation: standard k-fold for prediction; leave-one-out for small N.
- Expert review (acknowledged limitation): if no quantitative validation is possible, write a "validation strategies considered" subsection acknowledging the gap.

This last case requires escalation to the user — Stage 2 should not silently emit a result with no validation framework. Ask the user whether to (a) reframe the problem to add validation, (b) accept the limitation as a documented weakness, or (c) substitute a related validation (stability sweep, parameter recovery).

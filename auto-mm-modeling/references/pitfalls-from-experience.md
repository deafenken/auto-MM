# Pitfalls from experience — lessons encoded as do/don't rules

Distilled from the author's past 华中杯 A 题 retrospective (kept locally, not in this repo). These are non-trivial mistakes the user has already paid for. Every modeling decision should be cross-checked against this file.

## P1 — Problem statement wins over geometric/intuitive simplification

**Symptom:** Problem says "30 customers in the green zone." Map shows a 10 km radius circle that contains ~25 customers. Team uses 10 km radius because it's "cleaner."

**Rule:** Main model honors the problem statement's wording (30 customers). The geometric interpretation goes into sensitivity analysis.

**Mechanism in code:** When a discrepancy is detected during decomposition, write an explicit `Assumption N: We adopt the problem-statement value of 30; the 10km-radius interpretation is treated as a sensitivity case.` Tag `fixed-by-problem` for the 30, `to-sweep` for the radius.

## P2 — Don't dump every metaheuristic into one solver

**Symptom:** Paper says "we combine SA, TS, GA, and ALNS." Each is named but none is explained as solving a specific feature of the problem.

**Rule (Rule 5):** Each algorithmic component must answer "what problem feature does this address?" If you can't answer for one component, drop it.

**Better composition:**
- ALNS as backbone — adaptive destroy/repair operators.
- SA as the acceptance criterion inside ALNS (controls exploration).
- Add a problem-specific destroy operator (e.g., policy-conditional removal for time-windowed VRP).
- Validate small instances against a MILP exact solve.

That's three components, each with a named role. Reviewers can't fault it.

## P3 — AI/ML modules must address real uncertainty, not compute a closed form

**Symptom:** Team trains a deep net to predict a quantity (e.g., total cost) that is computable in closed form from the model's existing variables.

**Rule (Rule 4):** ML's job is to absorb uncertainty the deterministic model cannot. Acceptable: forecasting future demand, classifying ambiguous text, learning a heuristic where exact is intractable. Not acceptable: replacing a `sum()` with a trained regressor.

**Better placement of an ML module (for a VRP problem):**
- Forecast next-day demand heatmaps (real uncertainty).
- Predict probability of dynamic events per zone (real uncertainty).
- Feed probabilities into a two-stage stochastic program as virtual demand (deterministic-equivalent).

## P4 — When data is single-day / tiny sample, downgrade the language

**Symptom:** Paper claims "our model generalizes to production deployment" based on one CSV with 200 rows.

**Rule:** Match claim strength to evidence strength. If the dataset is small, say "we extract cross-sectional patterns from the closed dataset" or "we estimate a prior over zone hotness" — not "we train a generalizing prediction model."

**Practical write-up:**
- Use the term "preference extractor" or "prior estimator" instead of "predictive model."
- Show cross-validation on the small data and report the bound (e.g., 5-fold CV with 95% CI).
- Concede limits: "production deployment would require a multi-month historical log."

## P5 — Naming hard-coded numbers in formulas

**Symptom:** Formula contains `t_i + 5 + 0.15·w_i ≤ 960`.

**Rule:** Replace each literal with a symbol named in `notation.md`. The formula becomes `t_i + δ_0 + α·w_i ≤ T_lim` with $\delta_0, \alpha, T_\text{lim}$ tabulated.

**Why it matters:** A reviewer rerunning the model with different parameters should only need to change the table. Sensitivity sweeps depend on this discipline.

## P6 — Time-varying network and FIFO

**Symptom:** Speed table changes between time blocks (peak / off-peak). Naive plug-in `t_j = t_i + τ_{ij}(t_i)` can produce FIFO violations: leaving later but arriving earlier.

**Rule:** Introduce a waiting variable $w_i \geq 0$:

$$t_j = t_i + \delta_i + w_i + \tau_{ij}(t_i + \delta_i + w_i)$$

Operationally, $w_i$ is delayed dispatch / driver rest / charging / dispatch-cooling. Cite it explicitly in the model's prose.

## P7 — Order splitting and the Split/Merge trap

**Symptom:** Big orders are pre-split into many sub-tasks to make the routing easier. Result: many small vehicles, no large-truck synergy.

**Rule:** If splitting is needed (because of capacity or vehicle restrictions), pair it with a Split/Merge operator in the heuristic so that large orders can be re-merged when a feasible heavy vehicle is available.

## P8 — Heterogeneous fleets must be heterogeneous in the model

**Symptom:** Problem gives 3 vehicle types with different costs, capacities, energy profiles. Model uses one "average vehicle."

**Rule:** Per-type parameters in the table. Per-type variables ($y_v$ indexed by vehicle, not just count). Per-type results in the paper.

## P9 — Cost normalization

**Symptom:** Paper reports total cost = "fixed cost + carbon + time penalty + …" with each term in a different unit.

**Rule:** Convert every term to a single currency (元). Each conversion factor is a named parameter (e.g., $p_c$ for carbon price 元/kg CO₂). Report the contribution of each term as a percentage in the results.

## P10 — Sensitivity for insight, not for filler

**Symptom:** Paper has 6 sensitivity figures, all showing "cost goes up as parameter goes up." No insight.

**Rule:** Each sensitivity is a hypothesis. Pre-state it: "we expect carbon-price increases to shift the optimal fleet mix toward electric vehicles, beyond a threshold $p^*$." Then test. Report:
- The threshold.
- The before/after shift in qualitative behavior.
- The point at which the model "switches regime."

A good sensitivity figure has a story; a bad one is just a line.

## P11 — Dynamic scheduling: measure disruption, not only cost

**Symptom:** Dynamic re-routing reduces cost vs baseline. Paper claims success.

**Rule:** Also measure disruption to the existing plan (Route Disturbance Index, count of changed assignments, driver-facing churn). A 1% cost reduction with 80% routes re-shuffled is operationally worse than 0.5% reduction with 5% re-shuffle. Report both axes.

## P12 — Figures earn their space

**Symptom:** Paper has 12 figures; some are flowcharts that say the same thing as the prose.

**Rule:** Every figure either (a) shows data the prose cannot, (b) shows a result that needs visual scale, or (c) demonstrates an algorithm trace where the geometry matters. Pure illustrations of "what we did" rarely earn their space.

The figure list to prioritize (VRP example):
1. Data flow / processing diagram (one).
2. Customer spatial distribution (one).
3. Weight-volume scatter (data shape).
4. Time-window heatmap (data shape).
5. Cost breakdown (results).
6. Route map (results).
7. Vehicle Gantt (results).
8. Convergence curve (algorithm).
9. Ablation curve (algorithm).
10. Pareto front (multi-objective).
11. Sensitivity heatmap (sensitivity).
12. Exact-solve Gap (validation).

Twelve in a 25-page paper is the upper end. More requires justification.

## P13 — Last 6 hours: stop adding, start polishing

**Symptom:** Team is still tweaking the model at hour 92 of 96.

**Rule:** Lockdown mode (last 6 hours, enforced by orchestrator). No new modeling, no new experiments. Only writing, building, anonymity, packaging. Override is allowed but logged.

## P14 — Anonymity is not negotiable

**Symptom:** PDF metadata contains the author's macOS username. Slack disqualification risk.

**Rule:** Stage 3's anonymity scan runs every build. It scans the PDF text and metadata for forbidden patterns (姓名, 学校, 指导老师, common given names, schools, advisor titles, `/Users/`, `/Volumes/`, git remotes). One hit blocks `submit.zip`.

---

## How this file is consumed

The modeling stage skill loads this file unconditionally — every model decision should be cross-checked against P1-P14. If a candidate violates one, document the mitigation in `candidates.md` (e.g. "P3: the GBM module forecasts next-period demand, which is a real uncertainty not captured by the deterministic cost model").

The orchestrator does not auto-grep this file — these are guidance, not regexes. But the modeling stage's hand-off must include a one-line "P-check" listing which pitfalls were considered and how each was mitigated or marked N/A.

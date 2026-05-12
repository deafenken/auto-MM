# Contest typology — recognizing the task type from a problem statement

Used in Step 2 of `auto-mm-triage/SKILL.md` to tag each problem in `problems_index.md` with one primary task type. This tag is consumed by Stage 1 to bias the candidate-model search.

Pick exactly one primary type per problem. If two apply equally, pick `mixed` and list both in the notes.

## The 9 primary types

### `optimization-discrete`
Find a feasible plan minimizing / maximizing an objective with combinatorial decisions.
- Signals: "schedule", "route", "assign", "pack", "select k of N", "minimum cost", "shortest path".
- Default candidate models: MILP, integer programming, VRP/TSP variants, constraint programming.
- Default algorithms: exact (small instance) + metaheuristic (ALNS, SA, GA, TS) for full.
- Example: 华中杯 A 题 (绿色配送优化).

### `optimization-continuous`
Decisions are real-valued; objective + constraints involve continuous functions.
- Signals: "design parameters", "control trajectory", "optimal allocation of resources", "PDE-constrained".
- Default candidate models: LP / convex / NLP, sometimes ODE/PDE-based.
- Default algorithms: interior point, SQP, gradient methods.

### `inference-statistical`
Estimate hidden quantities from observations.
- Signals: "estimate", "infer", "calibrate", "reconstruct", "characterize uncertainty".
- Default candidate models: MLE, Bayesian, inverse problems, regularized regression.
- Example: 2026 MCM Problem C — infer fan votes from observed eliminations.

### `forecasting`
Predict future values of a time-indexed quantity.
- Signals: "predict", "next year", "trend", "horizon", "rolling".
- Default candidate models: ARIMA, state-space, GBM, LSTM / Transformer (only if uncertainty is real).
- Watch out: integrity Rule 4 — don't use a NN if a closed-form or classical model suffices.

### `classification`
Map an item to one of K discrete classes.
- Signals: "classify", "detect", "identify (which category)".
- Default candidate models: logistic regression, SVM, GBM, simple NN. Domain-specific (image / NLP) as needed.
- Watch: small samples → simple models with cross-validation.

### `network-graph`
Model entities + relationships; analyze structure or flow.
- Signals: "network", "graph", "centrality", "community", "cascade".
- Default candidate models: graph algorithms, network flow, percolation, SIS/SIR on graphs.

### `simulation-agent`
Simulate emergent behavior of interacting agents / particles / cells.
- Signals: "simulate", "evolve over time", "interaction rules", "emergent".
- Default candidate models: discrete-event simulation, agent-based, cellular automata, system dynamics.
- Heavy compute warning: budget time for many replications.

### `policy-open`
Open-ended policy / strategy question with no single quantitative answer.
- Signals: "design a system", "evaluate a policy", "recommend", "stakeholders".
- Default candidate approach: structured multi-criteria decision analysis (MCDA), scenario simulation, mini-models per stakeholder.
- Highest variance: the differentiator is in the framing and the executive memo, not the math.

### `mixed`
The problem combines two or more types where neither dominates.
- Example: "predict next-year demand AND design the optimal supply schedule" = forecasting + optimization-discrete.
- Note: most CUMCM problems are technically mixed but have one primary backbone — pick the backbone.

## How to tag

Read the problem statement end-to-end. Then ask:

1. **What is the user being asked to produce?** A schedule? An estimate? A forecast? A classification? A recommendation?
2. **Is the decision discrete or continuous?**
3. **Is there ground truth?** (Forecasting / classification need it; inference does not need it directly but needs identifiability.)
4. **Is the answer judged by a single metric or by a story?**

Then map to one of the 9 types. If genuinely 50/50, use `mixed` and call it out — Stage 1 will decompose.

## Why this typology is rough

Real problems straddle types. The point is not surgical precision — it's giving Stage 1 a fast prior on which model families to investigate first. A tag of `optimization-discrete` does not exclude a Bayesian sub-component; it just says "start there."

## Reference table — past contest problems tagged

(Add as we encounter them; this lookup helps recognize variants.)

| Problem | Year | Tag | Notes |
|---|---|---|---|
| MCM C | 2026 | `inference-statistical` + light `classification` | DWTS fan-vote inference; attention-mech for feature interpretation. |
| 华中杯 A | 2025 | `optimization-discrete` | Green-zone VRP with carbon constraints. |
| CUMCM A | 2024 (placeholder) | TBD | Add when we see one. |

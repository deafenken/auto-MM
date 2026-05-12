# Model zoo — candidate families for 数模 problems

A cheat sheet of model families grouped by problem typology. Use this as a starting point for `candidates.md`, not as a script. The point is to surface 2-4 candidates worth comparing, not to enumerate everything.

## For `optimization-discrete`

### MILP (Mixed-Integer Linear Programming)
- Best when constraints are linear, decisions are mostly binary/integer, scale is small-to-medium (≤ 10⁵ variables).
- Solvers: Gurobi (academic license), CPLEX, SCIP, open-source CBC.
- Use for: small-instance exact solve to report optimality Gap; small subproblems inside heuristics.
- Watch out: branch-and-bound explodes on big-M formulations; tighten the LP relaxation first.

### Constraint Programming (CP)
- Strong on scheduling, packing, sequencing with complex side constraints.
- Solvers: Google OR-Tools CP-SAT (free, strong), Choco.
- Often outperforms MILP on logical/disjunctive constraints.

### Metaheuristics (ALNS / SA / TS / GA)
- For large-scale combinatorial problems where exact solve is infeasible.
- **ALNS** (Adaptive Large Neighborhood Search) — current default for VRP/scheduling.
- **SA** (Simulated Annealing) — single-trajectory; pair with another heuristic as acceptance criterion.
- **TS** (Tabu Search) — memory-based; good for permutation problems.
- **GA** (Genetic Algorithm) — when population diversity helps; rarely the strongest alone.
- Rule 5 reminder: each metaheuristic must address a specific feature; don't stack ≥3 without per-component justification.

### Specialized
- VRP / TSP — extensions (VRPTW, VRPPD, EVRP, GVRP).
- Bin packing, knapsack.
- Network flow (min-cost flow, max-flow, multi-commodity).
- Assignment (Hungarian for balanced; auction algorithms for large).

## For `optimization-continuous`

### Linear / Convex
- LP, QP, SOCP, SDP. Off-the-shelf solvers (CVXPY, MOSEK, ECOS).
- Identify convexity early — non-convex requires global solvers (Couenne, BARON).

### NLP / Optimal Control
- IPOPT (interior point), SLSQP (small problems).
- Trajectory optimization: direct collocation, multiple shooting.

### PDE-constrained
- Finite element methods. Heavy compute; only viable if the problem really demands it.

### Gradient-based
- For differentiable objectives; modern frameworks (PyTorch, JAX) double as optimizers.

## For `inference-statistical`

### Maximum Likelihood Estimation
- The default. Specify a likelihood, optimize. Report standard errors.
- Cheap, defensible, well-understood.

### Bayesian Inference
- When prior knowledge matters or uncertainty quantification is the deliverable.
- MCMC (PyMC, Stan) for general posteriors; VI for big problems.
- Cost: development time. Watch out: convergence diagnostics are mandatory; report R̂ and ESS.

### Inverse Optimization
- Given observed decisions, infer the unobserved cost/preference parameters.
- Used in 2026 MCM Problem C: infer fan votes from observed eliminations.
- Formulate as a constrained optimization with the elimination as a feasibility witness.

### Kalman Filter / State-Space
- Hidden state, linear-Gaussian dynamics. Tractable closed-form.
- Particle filter for non-linear/non-Gaussian.

### Identifiability check (mandatory before inference)
- Can the data, in principle, determine the parameters? If not, the inference is meaningless.
- Symbolic Jacobian rank check or simulation-based parameter recovery.

## For `forecasting`

### Classical
- ARIMA / SARIMA — short to medium horizons; well-trusted.
- Exponential smoothing (ETS) — strong baseline.
- Prophet (Facebook) — easy, good with seasonality and holidays.

### State-space + Bayesian
- BSTS, dynamic linear models — when uncertainty bands matter.

### Tree boosting
- LightGBM / XGBoost / CatBoost on engineered lag features. Strong baseline for tabular forecasting.

### Deep learning (carefully — Rule 4!)
- LSTM, Temporal Fusion Transformer, N-BEATS, PatchTST.
- Justified only when (a) sample size is large, (b) classical baselines are clearly inferior, AND (c) the forecast horizon or non-stationarity demands it.
- For 数模, default to GBM unless data demonstrates the need for DL.

## For `classification`

### Tabular
- Logistic regression (interpretable baseline; always include).
- LightGBM / XGBoost / CatBoost — typically the winner.
- SVM — niche, good for small clean datasets.

### Image
- Pre-trained CNN backbone + linear head (transfer learning). ResNet50, EfficientNet.
- Vision Transformer (ViT) if data and compute allow.
- For tiny datasets: feature extraction + classical classifier.

### NLP
- TF-IDF + linear classifier (baseline always).
- Pre-trained BERT / RoBERTa fine-tuning.
- For very small datasets: prompted LLM as zero/few-shot classifier (with caveat).

### Calibration
- Whatever the classifier, report calibration (Brier score, reliability diagram) and ROC/PR curves.

## For `network-graph`

- Graph centrality / community detection (Louvain, Leiden, Girvan-Newman).
- Network flow / cuts.
- Percolation, epidemic models on networks (SIS, SIR with structure).
- Graph neural networks — only justified by Rule 4 (real uncertainty in node features).

## For `simulation-agent`

- Discrete-event simulation (SimPy).
- Agent-based modeling (Mesa, Repast).
- Cellular automata for spatial dynamics.
- System dynamics (Vensim flavor) for stock-and-flow.

Replication count: at least 30-50 per scenario for narrow CIs. Budget compute accordingly.

## For `policy-open`

- Multi-Criteria Decision Analysis (MCDA): AHP, TOPSIS, ELECTRE — give the team a way to weigh stakeholder priorities.
- Scenario analysis: 3-5 distinct futures, run each through a simpler model.
- Cost-benefit analysis with sensitivity on key parameters.
- Game-theoretic mini-models for stakeholder interaction.

The differentiator on policy problems is **the framing and the executive memo**, not the algorithm.

## Hybrid recipes (worth seeing in practice)

- **MILP + ALNS** for VRP variants: ALNS for routing, MILP for small subproblems (validation + verification).
- **Inverse opt + light ML for interpretability** (2026 MCM C pattern): MILP/QP recovers latent quantities; attention or feature-importance explains *which* features matter.
- **Forecast + optimization**: predict next-period demand → feed into a deterministic-equivalent (or two-stage stochastic) optimization.
- **Bayesian + simulation**: posterior over parameters → Monte Carlo over consequences → report quantiles.

These are starting points. Adapt to the specific problem; do not force-fit a recipe.

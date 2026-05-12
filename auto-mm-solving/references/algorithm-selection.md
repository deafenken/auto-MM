# Algorithm selection — picking the solver / heuristic to match the model

Used in Step 1 of `auto-mm-solving/SKILL.md`. The point is to map the model in `stage1_modeling/model.md` to a concrete Python implementation.

## Decision tree

```
What family is in model.md?
├── MILP / LP / QP / convex
│   └── Use a direct solver:
│       - Gurobi (academic license, gold standard for MILP)
│       - CPLEX (alternative, similar tier)
│       - CVXPY + ECOS/SCS (for convex)
│       - OR-Tools CP-SAT (for combinatorial; often beats MILP on side constraints)
│       - SciPy linprog / milp (low-effort baseline)
├── Large-scale combinatorial (routing, scheduling, packing)
│   └── Heuristic backbone:
│       - ALNS (recommended default; flexible neighborhoods)
│       - SA as acceptance criterion inside ALNS
│       - Add a problem-specific destroy operator
│       - Validate with MILP exact on a small instance (mandatory per Rule 6)
├── Continuous nonlinear / optimal control
│   └── IPOPT via Pyomo / CasADi; or SLSQP via SciPy for small problems
├── Inference (MLE / Bayesian / inverse opt)
│   ├── MLE → scipy.optimize.minimize with L-BFGS-B + analytic gradient if possible
│   ├── Bayesian → PyMC (NUTS) or numpyro (NUTS, faster); confirm R̂ < 1.01, ESS > 400
│   └── Inverse opt → constrained QP / KKT formulation; CVXPY
├── Forecasting
│   ├── ARIMA / SARIMA → statsmodels
│   ├── ETS / Prophet → statsmodels / prophet
│   ├── GBM lag features → LightGBM (fastest), XGBoost, CatBoost
│   └── DL → PyTorch (only if Rule 4 passes)
├── Classification
│   ├── Tabular → LightGBM + logistic regression baseline
│   ├── Image → torchvision (resnet18/50 frozen + linear head as baseline)
│   └── NLP → HF transformers (BERT base) for fine-tune; sklearn TF-IDF for baseline
├── Network / graph
│   └── NetworkX (small), igraph (medium), graph-tool (large)
├── Simulation
│   ├── Discrete-event → SimPy
│   ├── Agent-based → Mesa
│   └── System dynamics → custom RK4 in NumPy
└── Mixed
    └── Decompose: solve sub-problems with the matching solver, glue together.
```

## Choosing solvers under license constraint

| Solver | License | Notes |
|---|---|---|
| Gurobi | Academic free; commercial paid | Gold standard MILP. Use if you have a license. |
| CPLEX | Academic free | Similar tier to Gurobi. |
| HiGHS | Open-source | Good free LP/MILP; behind Gurobi by ~2-5x on hard MILP. |
| CBC / SCIP | Open-source | Free fallback; significantly slower. |
| OR-Tools | Open-source | Strong CP-SAT; good MILP wrapper. |
| CVXPY | Open-source | High-level modeling; calls under-the-hood solver. |

If no commercial license is available, default to **HiGHS** (via `scipy.optimize.milp` or directly) for MILP and **CVXPY + ECOS** for convex.

## Implementation pattern — MILP example

```python
# src/model.py
def build_model(data, cfg):
    import gurobipy as gp
    from gurobipy import GRB
    m = gp.Model("vrp_main")
    # decision variables (names match notation.md!)
    x = m.addVars(data['I'], data['I'], data['V'], vtype=GRB.BINARY, name="x")
    t = m.addVars(data['I'], lb=0, name="t")
    y = m.addVars(data['V'], vtype=GRB.BINARY, name="y")
    # objective — every term in 元 per notation.md
    m.setObjective(
        gp.quicksum(data['c_fix'][v]*y[v] for v in data['V']) +
        gp.quicksum(data['c_arc'][i,j]*x[i,j,v] for i,j,v in x),
        GRB.MINIMIZE
    )
    # constraints — grouped per model.md
    add_flow_constraints(m, x, data)
    add_capacity_constraints(m, x, data)
    add_time_window_constraints(m, x, t, data)
    return m
```

Notes:
- Variable names mirror notation.md so debugging the solver's `model.lp` is easier.
- Constraint groups are functions, mirroring model.md's grouping.
- Objective has each term traceable to a parameter in `data`.

## Implementation pattern — ALNS example

```python
# src/solve.py
from alns import ALNS
from alns.accept import SimulatedAnnealing
from alns.select import RouletteWheel
from alns.stop import MaxIterations

def solve(model, cfg):
    alns = ALNS()
    # destroy operators — each addresses a problem feature (Rule 5)
    alns.add_destroy_operator(random_removal)         # exploration
    alns.add_destroy_operator(worst_removal)          # intensify
    alns.add_destroy_operator(green_zone_removal)     # problem-specific
    # repair operators
    alns.add_repair_operator(greedy_insertion)
    alns.add_repair_operator(regret_insertion)
    # acceptance + selection + stop
    accept = SimulatedAnnealing.autofit(initial_obj=model.initial_cost(), worse=0.05, accept_prob=0.5)
    select = RouletteWheel([3,2,1,0.5], 0.8, len(alns.destroy_operators), len(alns.repair_operators))
    stop = MaxIterations(cfg['max_iters'])
    result = alns.iterate(initial_state(model), select, accept, stop)
    return result
```

Each destroy operator's docstring says "this addresses problem feature X" — that satisfies the Rule 5 audit.

## Implementation pattern — inverse optimization

```python
# Recover latent fan votes from observed elimination outcomes
import cvxpy as cp
import numpy as np

def solve_inverse(judges_scores, eliminations, cfg):
    n_weeks, n_contestants = judges_scores.shape
    fan_votes = cp.Variable((n_weeks, n_contestants), nonneg=True)
    # normalization
    cons = [cp.sum(fan_votes, axis=1) == 1]
    # consistency: contestant with lowest combined score must be eliminated
    for w, eliminated_idx in enumerate(eliminations):
        for c in range(n_contestants):
            if c == eliminated_idx: continue
            cons.append(
                cfg['alpha']*judges_scores[w,eliminated_idx] + (1-cfg['alpha'])*fan_votes[w,eliminated_idx]
                <= cfg['alpha']*judges_scores[w,c] + (1-cfg['alpha'])*fan_votes[w,c]
            )
    obj = cp.Minimize(cp.norm(fan_votes - cfg['prior'], "fro"))
    prob = cp.Problem(obj, cons)
    prob.solve(solver=cp.ECOS)
    return fan_votes.value
```

## Anti-patterns

- **Reaching for DL when a 50-line classical model suffices.** Rule 4. Test the classical baseline first.
- **Stacking N metaheuristics without per-component justification.** Rule 5. Each component must answer "what feature does this handle?".
- **Calling the same solver from multiple paths in pipeline.py.** Centralize solver invocation in `src/solve.py`; the rest of the pipeline doesn't know which solver is in use.
- **Treating runtime randomness as a non-issue.** Fix the seed in `config.yaml`. Report it in `result.json`. Sweep seeds (5-10) for results that go into the abstract.

## Solver wallclock budgeting

Each experiment's `config.yaml` declares `expected_wallclock_s` and `max_wallclock_s`. If exceeded, the orchestrator aborts the run (writing partial metrics + `status: aborted` to `result.json`) and proceeds to the next.

Default budgets (override per-problem):

| Run type | expected_wallclock_s | max_wallclock_s |
|---|---|---|
| baseline | 60 | 300 |
| main-v1 | 600 | 1800 |
| exact-small | 60 | 600 |
| ablation | 600 | 1800 |
| sweep-point | 300 | 900 |

A full sweep of 5 points is 5 × the per-point budget, plus overhead. Plan accordingly.

# Notation style — consolidating symbols in `notation.md`

The notation table is read more carefully than the prose. Get it right and the rest of the modeling section flows; get it wrong and the reviewer loses trust.

## Required structure (in this order)

1. **Sets and indices**
2. **Parameters** (input values — grouped by source: problem-given / derived / assumed)
3. **Decision variables**
4. **Auxiliary variables**
5. **Functions and operators**

Each section is a table with three columns minimum: Symbol | Description | Domain/Units.

## Example

```markdown
## Sets and indices
| Symbol | Description | Index |
|---|---|---|
| $I$ | Set of customers | $i \in I$ |
| $V$ | Set of vehicles | $v \in V$ |
| $T$ | Discrete time steps (minutes) | $t \in \{0,1,\dots,T_\text{end}\}$ |
| $A$ | Set of arcs in the road network | $(i,j) \in A$ |

## Parameters (problem-given)
| Symbol | Description | Units | Value / Source |
|---|---|---|---|
| $d_i$ | Demand of customer $i$ | kg | from `customers.csv` |
| $Q_v$ | Capacity of vehicle $v$ | kg | from `vehicles.csv` (heterogeneous) |
| $T_\text{lim}$ | Latest delivery time (16:00) | min from start | 960 (problem §3.2) |

## Parameters (derived)
| Symbol | Description | Units | Definition |
|---|---|---|---|
| $\tau_{ij}(t)$ | Travel time on arc $(i,j)$ starting at time $t$ | min | piecewise-linear interp from `speed_table.csv` |
| $c_v^\text{fix}$ | Fixed cost of dispatching vehicle $v$ | 元 | $c_v^\text{base} + 0.05 \cdot Q_v$ |

## Parameters (assumed; see assumptions.md)
| Symbol | Description | Units | Value | Assumption # |
|---|---|---|---|---|
| $\alpha$ | Per-kg unloading time | min/kg | 0.15 | A4 |
| $p_\text{c}$ | Carbon price | 元/kg CO₂ | 80 | A7 (sensitivity) |

## Decision variables
| Symbol | Description | Domain |
|---|---|---|
| $x_{ijv}$ | 1 if vehicle $v$ traverses arc $(i,j)$ | $\{0,1\}$ |
| $t_i$ | Arrival time at customer $i$ | $\mathbb{R}_{\geq 0}$ |
| $y_v$ | 1 if vehicle $v$ is dispatched | $\{0,1\}$ |

## Auxiliary variables
| Symbol | Description | Domain | Definition |
|---|---|---|---|
| $w_i$ | Waiting time at customer $i$ before service | $\mathbb{R}_{\geq 0}$ | introduced to handle FIFO violations in time-varying network |

## Functions and operators
| Symbol | Description |
|---|---|
| $\delta_i$ | Service time at $i$: $\delta_0 \cdot I_i + \alpha \cdot d_i$ |
```

## Rules

### R1 — One symbol, one meaning
If $c$ means "cost" in one constraint and "capacity" in another, the paper has a bug. Rename.

### R2 — No literals inside formulas
Replace `T = 960` with a named parameter ($T_\text{lim}$) and tabulate the value. Reviewers should be able to change the value in one place and re-derive consistency.

### R3 — Group by source for parameters
"Problem-given" vs "derived from data" vs "team assumption" matters for sensitivity scoring. A parameter from the problem statement is fixed (Rule 1); an assumed parameter goes in `assumptions.md` and is a sensitivity candidate.

### R4 — Index convention is consistent
Pick a convention: $i$ for customers, $j$ for second customer in an arc, $v$ for vehicles, $t$ for time, $k$ for iteration. Stick to it across the paper. Switching $i$ ↔ $j$ between sections costs reader trust.

### R5 — Units in the table, not in the formula
Once a parameter is declared with units, formulas need not repeat them. Inline `[元]` annotations clutter math without adding info.

### R6 — Decision variables are clearly distinct
A reader should be able to count, at a glance, how many decision variables the model has. Put them in their own subsection. Auxiliary variables (introduced for linearization) are separate.

### R7 — Functions get their own subsection
If the model uses $\delta_i, \tau_{ij}(t), \sigma(x), \mathrm{softmax}(\cdot)$ — list them. Define each clearly. Don't make the reader infer.

### R8 — Cross-reference assumptions
Every "assumed" parameter has a column linking to the assumption number in `assumptions.md`. Sensitivity sweeps later vary exactly these.

## Common mistakes (and how to spot them)

- **A symbol appears in a formula but not in the table.** Greppable: extract all `\$[A-Za-z_]+` from `model.md`, compare to symbol column of `notation.md`. Mismatch → fix.
- **The "value" column is missing for problem-given parameters.** Reviewer can't reproduce. Add values + source.
- **Decision variables are mixed with parameters.** The reader can't tell what's chosen vs given. Split.
- **Subscripts are inconsistent: $x_{ij}^v$ vs $x_{ijv}$ vs $x^v_{ij}$.** Pick one form, apply everywhere.
- **A parameter has units `[?]`.** Trace it; if no unit makes sense, the parameter is suspect.

## Greppable invariant for the orchestrator

Before hand-off, the orchestrator's integrity gate runs:

```bash
# extract symbols from model.md
grep -oE '\\\$([A-Za-z_]+[A-Za-z0-9_]*)\\\$' stage1_modeling/model.md \
  | sort -u > /tmp/model_symbols

# extract symbols from notation.md
grep -oE '\$([A-Za-z_]+[A-Za-z0-9_]*)\$' stage1_modeling/notation.md \
  | sort -u > /tmp/notation_symbols

# difference
diff /tmp/model_symbols /tmp/notation_symbols
```

Any symbol in `model.md` but not in `notation.md` blocks the hand-off. The check is intentionally syntactic — the agent can refine the regex per-paper, but a missing symbol is never OK.

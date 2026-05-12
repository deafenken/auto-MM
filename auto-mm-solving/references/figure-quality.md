# Figure quality — looking like a paper, not an AI poster

The experience README §7 is unusually specific about what differentiates a paper figure from an AI-generated infographic. This file is the operationalized version.

## Default style

Use `assets/figure_style.py` at the top of every plotting script. It sets:

- Font family: serif (Times-like) for ticks/labels, sans-serif only for legends if needed.
- Font size: 10 pt for axis labels, 9 pt for ticks, 9 pt for legend.
- Line width: 1.0 default, 1.5 for emphasized.
- Marker size: 4.
- DPI for rasterized layers: 300.
- Palette: restrained — see below.

## Palette

```python
PALETTE = [
    "#2E5E8A",  # deep blue
    "#D87A3D",  # rust orange
    "#5A8A3D",  # olive green
    "#8A2E5E",  # plum
    "#3D8A8A",  # teal
    "#8A8A2E",  # mustard
    "#5A2E8A",  # purple-blue (use sparingly)
]
```

Avoid:
- High-saturation neon (`#FF00FF`, `#00FFFF`).
- Purple-to-blue gradient (the AI tell).
- Rainbow / jet colormap for sequential data — use viridis / plasma instead.

For heatmaps: viridis (default), plasma (alternative), or RdBu_r (diverging around zero).

## Hard rules

### F1 — No in-figure title

The caption is the title. `\caption{Figure 4: convergence of ALNS vs SA over 3000 iterations}` is the label; `plt.title(...)` is removed before saving.

### F2 — PDF vector, not PNG

```python
plt.savefig("figures/fig-name.pdf", bbox_inches="tight", pad_inches=0.05)
```

PNG is acceptable only for genuinely raster content (heatmap with >10k cells, satellite imagery). If you must use PNG, save at ≥ 300 DPI.

### F3 — Labels do not overlap data

After plotting, check:
- Axis tick labels don't run into each other (rotate 30° if needed).
- Legend doesn't sit on top of data points or lines.
- Value annotations on bars don't extend above the axis maximum.

`plt.tight_layout()` helps but is not always enough; manual `ax.legend(loc="upper right", bbox_to_anchor=...)` is sometimes needed.

### F4 — Caption-friendly aspect ratio

Default: 6.4×4.0 inches (matplotlib's default-ish). For wide layouts: 8×3.5. For square: 5×5. Anything wider than 9 inches will be shrunk by LaTeX and become unreadable.

### F5 — Units in axis labels, not in figure title

`Cost (元)`, `Time (min)`, `Customer count` — units in parentheses on the label.

### F6 — Every figure is referenced from prose

Naming convention: `fig-<section>-<short_descriptor>.pdf`. The paper greps for `\includegraphics{<filename>}` and `\ref{fig:<filename>}`. Orphan figures (file exists, no `\ref`) block the build per Rule 8.

### F7 — Mixed-language labels OK, but consistent

For Chinese paper: Chinese axis labels are fine. English short terms for inputs/outputs in flowcharts are acceptable. Do not mix randomly — pick a convention.

## High-value figure types (use these)

In order of "judges will look hard":

1. **Data-flow diagram** — one, near §3 (data processing).
2. **Spatial / structural map of the data** — locations, network topology, time-window distribution.
3. **Headline result** — bar chart or scatter with the main metric for each method.
4. **Algorithm-internal trace** — convergence curve, branch-and-bound progress, ALNS operator selection over iterations.
5. **Ablation comparison** — paired bars or grouped lines.
6. **Sensitivity sweep** — one figure per assumption swept, with the threshold/regime-change marked.
7. **Pareto front** — multi-objective trade-offs.
8. **Validation against exact** — Gap as a function of instance size.

Avoid:

- Generic "system architecture" flowcharts with rounded rectangles and arrows — they say "we have a method" without showing what it does.
- Pie charts (rarely informative).
- 3D bar charts (almost never informative).
- Decorative icons (you are writing a paper, not a slide deck).

## Per-section figure budget

For a 25-page paper, 8-12 figures is the sweet spot. Distribution:

- Background / problem: 1
- Data processing: 1-2
- Model derivation: 1 (sometimes a structural diagram)
- Algorithm trace: 1-2
- Main results: 2-3
- Validation: 1-2
- Sensitivity: 2-3
- Discussion: 0-1

>12 figures: justify each addition; > 15 is rarely a good sign.

## Greppable checks for the orchestrator

Before allowing `submit.zip`:

```bash
# every figure file is referenced
for f in stage3_writing/paper/img/*.pdf stage3_writing/paper/img/*.png; do
  name=$(basename "$f")
  if ! grep -q "$name" stage3_writing/paper/*.tex; then
    echo "ORPHAN FIGURE: $name"
  fi
done

# every \label{fig:...} is \ref{fig:...}-ed or \Cref{fig:...}-ed
grep -hoE '\\label\{fig:[^}]+\}' stage3_writing/paper/*.tex | sort -u | \
  awk -F'[{}]' '{print $2}' | while read label; do
    # use -E (extended regex) and match \ref / \cref / \Cref / \autoref / \pageref
    if ! grep -qE "\\\\(c|C)?ref\{${label}\}|\\\\autoref\{${label}\}|\\\\pageref\{${label}\}" stage3_writing/paper/*.tex; then
      echo "ORPHAN LABEL: $label"
    fi
  done
```

Any orphan → block until resolved or removed.

## Example script

```python
# scripts/make_convergence_figure.py
import matplotlib.pyplot as plt
import numpy as np
from src.style import PALETTE, apply_style

apply_style()  # sets RC params

iters, alns_obj, sa_obj, ts_obj = load_curves("runs/main-v3/log.txt")

fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(iters, alns_obj, label="ALNS",  color=PALETTE[0], lw=1.5)
ax.plot(iters, sa_obj,   label="SA",    color=PALETTE[1], lw=1.0)
ax.plot(iters, ts_obj,   label="TS",    color=PALETTE[2], lw=1.0)
ax.set_xlabel("Iteration")
ax.set_ylabel("Objective (元)")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3, linewidth=0.5)
fig.savefig("figures/fig-convergence-main.pdf", bbox_inches="tight", pad_inches=0.05)
```

Save to `figures/`, reference from the paper, done.

# Sensitivity analysis — turning sweeps into insight

The experience README §9 is unambiguous: sensitivity is for insight, not figure-padding. This file is the protocol.

## What sensitivity is for

Each `to-sweep` assumption in `stage1_modeling/assumptions.md` is a question of the form: "if this assumed parameter were wrong, would our conclusion change?" Sensitivity tests answer that question.

A good sensitivity result either:
1. **Robustness**: the conclusion holds across the sweep range; report the range and the unchanged conclusion. Reader trusts the result more.
2. **Regime change**: the conclusion changes at some threshold $\theta^*$; report the threshold and what changes on each side. This is the most valuable kind of finding.

A bad sensitivity result is "value goes up as parameter goes up" with no interpretation. Don't ship those.

## Sweep design

For each `to-sweep` assumption parameter $\theta$ with baseline $\theta_0$:

### Grid

- **3 points minimum** (low / baseline / high). Use this when compute is tight.
- **5 points typical** (e.g., $0.5\theta_0, 0.75\theta_0, \theta_0, 1.5\theta_0, 2\theta_0$).
- **7-11 points** if you suspect a regime change and need to localize the threshold.

### Bracketing

Choose the low/high endpoints to span the range a reviewer might plausibly suggest. If the assumption is a domain literature value, the bracket should include the literature's reported range. If it's a team judgment, the bracket should include "obviously low" and "obviously high" to demonstrate you considered both.

### Stratification

When sweeping two parameters jointly (e.g., carbon price × time-window slack), use a **5×5 grid** at most. Visualize as a heatmap (`sensitivity.md` → `figures/fig-sens-<a>-vs-<b>.pdf`).

## Writing the insight

For each sweep, `sensitivity.md` contains:

```markdown
## Sensitivity: <parameter name and symbol>

**Range swept**: <grid>.
**Main result behavior**: <one sentence on what happens>.

### Findings
- <one bullet per concrete finding, with numbers>

### Conclusion
- **Type**: <robustness | regime-change | partial>.
- **Interpretation**: <one paragraph for the paper>.

### Threshold (if regime-change)
- $\theta^* \approx <value>$
- Below $\theta^*$: <qualitative behavior>.
- Above $\theta^*$: <qualitative behavior>.
- Mechanism: <one sentence on why this threshold exists>.
```

## Insightful framings (encourage)

- "Carbon price has to exceed 110 元/kg CO₂ before the optimal fleet mix flips from diesel-dominant to electric. Below this, total cost is dominated by fixed dispatch costs; above, emission penalty dominates."
- "Time-window slack of ±15 minutes preserves baseline cost within 2%; beyond ±30 minutes, the model degenerates to a TSP-style heuristic and loses the green-zone advantage."
- "The model is robust to ±20% misspecification of unloading rate α — total cost changes by ≤1.4%. This validates our team-judgment estimate of α=0.15."

## Empty framings (avoid)

- "Total cost increases with $\theta$." (No threshold, no mechanism. Useless.)
- "We swept $\theta$ over five values and obtained the following table." (Data dump.)
- "Sensitivity confirms the model." (Vague; reviewer cannot verify.)

## Figure templates

### Single-parameter sweep

```python
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots(figsize=(6.4, 4.0))
ax1.plot(theta_grid, cost_at_theta, marker="o", color=PALETTE[0])
ax1.set_xlabel(r"Carbon price $p_c$ (元/kg CO$_2$)")
ax1.set_ylabel("Total cost (元)", color=PALETTE[0])
ax2 = ax1.twinx()
ax2.plot(theta_grid, ev_share_at_theta, marker="s", color=PALETTE[1])
ax2.set_ylabel("EV fleet share (%)", color=PALETTE[1])
# threshold marker
if threshold:
    ax1.axvline(threshold, color="gray", ls="--", lw=0.8)
    ax1.text(threshold, ax1.get_ylim()[1]*0.95, fr"$p_c^*\approx{threshold}$", ha="center")
fig.savefig("figures/fig-sens-carbon.pdf", bbox_inches="tight", pad_inches=0.05)
```

### Two-parameter heatmap

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(5.0, 4.5))
sns.heatmap(cost_grid, xticklabels=p_grid, yticklabels=tw_grid,
            cmap="viridis", annot=True, fmt=".0f",
            cbar_kws={"label": "Total cost (元)"})
ax.set_xlabel(r"Carbon price $p_c$")
ax.set_ylabel("Time-window slack (min)")
fig.savefig("figures/fig-sens-carbon-x-tw.pdf", bbox_inches="tight", pad_inches=0.05)
```

## Compute budget

Sensitivity is the first thing trimmed when Stage 2 overruns. Drop order:

1. Drop the 7-point sweeps down to 5.
2. Drop joint 2-parameter heatmaps if they don't show regime structure.
3. Keep the single-parameter sweeps that are tagged `to-sweep` in `assumptions.md` — those are the integrity-committed ones.

If you must drop a `to-sweep` sweep entirely, write a `## Skipped` section in `sensitivity.md` listing it and the reason. Stage 3 will mention it as a future-work item.

## Cross-check at hand-off

Before writing `hand_off.md`, verify:

- [ ] Every `to-sweep` assumption has a corresponding subsection in `sensitivity.md`.
- [ ] Each subsection has a `Conclusion` line that is either `robustness` or `regime-change` (or `partial` with explanation).
- [ ] At least one figure per sweep, in `figures/`, named `fig-sens-*.pdf`.

Missing items → escalate to the user before hand-off.

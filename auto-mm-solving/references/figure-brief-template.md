# `brief.md` — the spec sheet for a single figure

Every figure folder under `stage2_solving/figures/<fig_id>/` starts with a brief. Use this template verbatim and fill every field. Empty fields = unfocused figure = wasted iterations.

## Template

```markdown
# Figure brief — <fig_id>

## Meta
- **fig_id**: <e.g. fig-route-map>
- **type**: <data | schematic>
- **paper_section**: <e.g. "Results §6.2" or "Algorithm §5.1">
- **filename in paper**: img/<fig_id>.pdf
- **revision**: <integer, increments each time the brief is materially edited>

## The one-sentence claim
<One sentence. What does this figure *prove* or *show*? If you can't write
this in one sentence, the figure is unfocused and should be redesigned or
dropped. Examples:
- "The ALNS heuristic converges within 1500 iterations on instances of size ≥40."
- "The optimal fleet mix flips from diesel-dominant to electric-dominant at p_c ≈ 110 元/kg."
- "Our model's end-to-end workflow has 4 stages: data preprocessing, model build, solve, validate.">

## Inputs

### For type=data:
- **Result file(s)**: stage2_solving/runs/<exp_id>/result.json
- **Table(s)**:    stage2_solving/runs/<exp_id>/tables/*.csv
- **Specific columns used**: <list each column by name, with its data file>
- **Aggregation**: <e.g. "mean over 10 seeds with 95% CI", "raw points", "median + IQR">

### For type=schematic:
- **Source section**: stage1_modeling/model.md §<N> | stage1_modeling/notation.md | other
- **Conceptual content**: <bulleted list of what concept is illustrated>

## Content (what MUST appear)
- <Each visual element on its own line. For data figures: axes (with units),
  data series (with labels), annotations, threshold markers. For schematic
  figures: every node (with its label text), every edge (with its label/style),
  any grouping or color coding.>

Examples (`type=data`, convergence curve):
- X axis: iteration number (1..max_iter)
- Y axis: objective value (元)
- Three series: ALNS (PALETTE[0], solid 1.5pt), SA (PALETTE[1], dotted 1pt), TS (PALETTE[2], dashed 1pt)
- Legend in upper-right, no border
- Optional threshold line at the exact-solve optimum (gray dashed)
- Grid at 0.3 alpha

Examples (`type=schematic`, model flowchart):
- Node 1: "Raw data (customers.csv, routes.csv)" — top-left, light gray fill
- Node 2: "Preprocessing (anomaly filter, unit unify)" — below Node 1
- Node 3: "MILP build" — center, blue fill
- Node 4: "ALNS solver (3000 iter)" — right of Node 3
- Node 5: "Validation (exact Gap on 12-customer subset)" — bottom-right
- Edges: 1→2 ("clean"), 2→3 ("features"), 3→4 ("relax"), 4→5 ("verify")
- Arrow style: thin, with arrowhead, label above each arrow

## Style constraints
- Aspect ratio: <e.g. 6.4×4.0 in / 8×3.5 in / 5×5 in>
- Palette: PALETTE indices to use (from auto-mm-solving/assets/figure_style.py)
- Output format: PDF vector (PNG only allowed for heatmaps >10k cells)
- **No in-figure title** (caption is supplied by LaTeX)
- **No author/path leakage** (Rule 2)
- Language for labels: <en | zh | mixed> (mixed = English short terms in flowchart, Chinese in body)

## Reference context (verbatim from the paper)
<Paste the prose sentence(s) that will \ref this figure. This is the
acceptance criterion at review time: the figure must support these
sentences. If you don't have the prose yet, write it now or skip the figure.>

Example:
> "图\ref{fig:convergence-main}所示，ALNS 在第 1340 次迭代收敛至总成本 184320 元，
>  收敛速度优于 SA（第 2200 次）和 TS（未在 3000 次内收敛）。"

## Out of scope (what NOT to put in)
- <Anti-content lines. Saves prompts from over-generating.>

Examples:
- No subtitle, no in-figure caption.
- No 3D rendering.
- No company / school logos.
- No icons of trucks, factories, lightbulbs, gears, or other decorative emojis.
- No purple-to-blue gradient.

## Acceptance signals (what self_check.md should confirm)
- [ ] The claim is visually evident at a glance.
- [ ] Every Content element is present.
- [ ] No element from Out-of-scope is present.
- [ ] Style constraints are met.
- [ ] Reference-context sentences are supported.

---

(Optional) Internal notes / iteration log — visible to reviewer but not to paper:
- 2026-02-08 14:00 v1 — initial brief
- 2026-02-08 14:30 v2 — added threshold line; removed legend border per first review
```

## How the brief evolves

- **v1** — written at Step 1 of the workflow, before any prompt.
- **v2..** — bumped only when the *brief itself* needs to change (claim wrong, content list wrong, style constraint mis-set). Most revisions happen on `prompt.md`, not on `brief.md`. If you find yourself editing the brief on every iteration, the figure is unfocused — go back to the claim sentence.

The reviewer reads the latest brief revision. Old revisions are kept inline (one line each) for audit.

## Anti-patterns

### A1: One-sentence claim is "we show the results."
Too vague. The claim should name the *finding*. "We show that ALNS beats SA by 15% within 1000 iterations" is a claim; "we show results" is filler.

### A2: Content list is "the convergence curves of all algorithms."
Not specific enough. List each algorithm, its color (by PALETTE index), its line style. The prompt later needs this concreteness.

### A3: Reference context is empty.
Then there is no prose anchoring the figure. Per Rule 8, the figure has no integrity-justification. Drop it or write the prose first.

### A4: Style constraints say "match the paper style."
Doesn't help the generator. Be explicit: aspect ratio, palette indices, language, output format. The style file `auto-mm-solving/assets/figure_style.py` sets RC params, but the brief still specifies the figure-level choices.

### A5: Out-of-scope is empty.
Almost every figure has at least one thing to NOT include. List one or two negatives — they save prompt iterations dramatically.

## Worked example — data figure

```markdown
# Figure brief — fig-sens-carbon

## Meta
- fig_id: fig-sens-carbon
- type: data
- paper_section: Sensitivity §7.2
- filename in paper: img/fig-sens-carbon.pdf
- revision: 1

## The one-sentence claim
The optimal fleet's EV share jumps from <20% to >50% as carbon price crosses p_c ≈ 110 元/kg CO₂.

## Inputs (data)
- Result file: stage2_solving/runs/sweep-carbon/result.json
- Table: stage2_solving/runs/sweep-carbon/tables/sweep.csv
- Columns: carbon_price, total_cost, ev_share
- Aggregation: single seed (deterministic optimization)

## Content
- X axis: carbon price p_c (元/kg CO₂)
- Left Y axis: total cost (元), PALETTE[0], solid, markers='o'
- Right Y axis: EV share (%), PALETTE[1], solid, markers='s'
- Vertical dashed line at p_c=110 with text label "p_c* ≈ 110" above
- Legend bottom-left, no border

## Style constraints
- Aspect: 6.4×4.0 in
- Palette: PALETTE[0], PALETTE[1]
- Format: PDF vector
- No in-figure title
- Language: en

## Reference context
> "图\ref{fig:sens-carbon} 显示，当碳价超过约 110 元/kg CO₂ 时，
>  电动车比例从 18% 跃升至 56%，总成本相应进入非线性增长区。"

## Out of scope
- No third Y axis.
- No annotations on individual data points.
- No purple-blue gradient.

## Acceptance signals
- [ ] Threshold p_c* visible
- [ ] Both axes labeled with units
- [ ] No in-figure title
```

## Worked example — schematic figure

```markdown
# Figure brief — fig-model-flowchart

## Meta
- fig_id: fig-model-flowchart
- type: schematic
- paper_section: Our Work §3.4
- filename in paper: img/fig-model-flowchart.pdf
- revision: 1

## The one-sentence claim
Our framework has four stages — preprocessing, MILP build, ALNS solve, validation — connected sequentially with one feedback edge from validation back to MILP build.

## Inputs (conceptual)
- Source: stage1_modeling/model.md §3 and §5
- Reflects the four-stage decomposition.

## Content
- 4 boxes in a horizontal row (left to right):
  1. "Data Preprocessing"  — inputs: raw CSVs
  2. "MILP Formulation"    — inputs: cleaned features, parameters
  3. "ALNS Solver (3000 iter)" — inputs: MILP relaxation
  4. "Validation (Exact Gap, k=12)" — outputs: paper headline
- Arrows: 1→2→3→4 forward
- One backward arrow 4→2 labeled "tighten constraints if Gap > 5%"
- Box fill: PALETTE colors (1 → soft gray, 2-4 → blue tones)
- Text in boxes: English short terms, 10pt
- No icons inside boxes

## Style constraints
- Aspect: 8×3.5 in (horizontal)
- Output format: PDF vector (TikZ preferred over image-gen for text fidelity)
- Language: en
- No in-figure title; LaTeX provides caption

## Reference context
> "Figure \ref{fig:model-flowchart} shows our framework: raw data is preprocessed
>  (§3.1), an MILP is formulated (§4), solved by ALNS (§5), and validated against
>  a small-instance exact solve (§6). A feedback loop tightens constraints when
>  the optimality gap exceeds 5%."

## Out of scope
- No truck / box / gear / lightbulb icons.
- No drop shadows.
- No 3D box rendering.
- No school logos.
- No author names.

## Acceptance signals
- [ ] 4 boxes, correct labels, correct order
- [ ] One forward chain + one feedback edge with the right label
- [ ] PDF vector output
- [ ] All text legible at 100% paper zoom
```

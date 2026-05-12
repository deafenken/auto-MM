# Figure workflow — brief → prompt → generate → self-check

The default way to make a figure in this skill is NOT "ask the assistant to draw it." It is a three-step pipeline with a structured spec sheet, a saved prompt, and a self-check pass against the style rules. The point is to (a) make the figure's purpose explicit before any pixels are drawn, and (b) keep prompts reusable across iterations.

External review is **not** per-figure in this skill. The self-check at Step 4 catches mechanical style-rule violations; aesthetics and "does this figure earn its space" are the writer's judgment at Stage 3, not an automated gate.

## Two figure classes — same pipeline, different prompts

| Class | What it is | Primary prompt target |
|---|---|---|
| **Data figure** (`type: data`) | Driven by real numbers from `stage2_solving/runs/<exp_id>/`. Scatter, bar, heatmap, convergence, Pareto, sensitivity, route map, Gantt. | A code-generation prompt → produces `plot.py` (matplotlib/seaborn) or `tikz.tex`. The figure is built by running the code on real data. |
| **Schematic figure** (`type: schematic`) | Diagrammatic, no real-data dependency. Model flowchart, system architecture, conceptual illustration. | Either a text-to-image prompt (DALL-E / Imagen / Nano Banana / Midjourney) OR a TikZ code-generation prompt. Default to TikZ for anything with text labels (text rendering in image models is unreliable). |

Both classes go through the same three steps.

## Per-figure folder layout (the contract)

Each figure lives in its own folder under `stage2_solving/figures/`:

```
stage2_solving/figures/
└── <fig_id>/                          # e.g. fig-model-flowchart
    ├── brief.md                       # Step 1: information document
    ├── prompt.md                      # Step 2: generation prompt
    ├── source/                        # Step 3: generation artifacts
    │   ├── plot.py                    #   for type=data with matplotlib
    │   │ | tikz.tex                   #   for type=schematic with TikZ
    │   │ | image_request.json         #   for type=schematic with image model
    │   ├── data_used.csv              #   for type=data: snapshot of the numbers
    │   └── log.txt                    #   build log
    ├── output.pdf                     # Step 3 final artifact (or .png if rasterized)
    ├── self_check.md                  # Step 4: short style-rule self-audit
    └── status                         # draft | needs_revision | ready
```

After Step 4 succeeds, a copy/symlink lands at `stage2_solving/figures/<fig_id>.pdf` — that is the path LaTeX references via `\includegraphics{img/<fig_id>.pdf}`.

`<fig_id>` is the same name LaTeX uses (`fig-data-flow`, `fig-route-map`, etc.). One ID = one folder = one figure in the paper.

## Step 1 — Brief (information document)

Template in `figure-brief-template.md`. Required fields:

- **fig_id** — the same letter LaTeX uses.
- **type** — `data` or `schematic`.
- **paper_section** — which §N this figure appears in.
- **claim** — what is the *one* sentence the figure proves? If you can't write this in one sentence, the figure is unfocused.
- **inputs** — for `type=data`: which `runs/<exp_id>/result.json` or `tables/*.csv` feeds it. For `type=schematic`: which `stage1_modeling/model.md` section it depicts.
- **content** — bulleted list of what must appear. Specific.
- **style constraints** — references back to `figure-quality.md` rules.
- **reference context** — verbatim quote of the prose line in the paper that will `\ref{}` this figure.
- **out of scope** — what NOT to put in.

Why this step matters: without a written brief, prompts drift between iterations and you converge after 5 mutually-inconsistent versions instead of 1. The brief is the anchor.

## Step 2 — Prompt

Built *from* the brief, not in place of it. Templates in `figure-prompt-patterns.md`. Three patterns:

- **Code prompt (matplotlib/seaborn)** — for `type=data`. The prompt names: data source, columns, plot kind, color mapping, labels (units), aspect ratio, output path. Output is `plot.py`.
- **Code prompt (TikZ)** — for `type=schematic` where text labels matter. The prompt names: nodes (with text + position), edges (with arrow style + label), palette, output path. Output is `tikz.tex`.
- **Image prompt (text-to-image)** — for `type=schematic` where conceptual aesthetic dominates. The prompt: subject + composition + style cues + negative prompts. Output is `output.png`.

Each prompt is **saved verbatim** to `prompt.md`. If a figure fails self-check, the prompt is the diff target — not the brief.

## Step 3 — Generate

**Code-based (matplotlib / TikZ)**:
```bash
cd stage2_solving/figures/<fig_id>/
python source/plot.py                     # matplotlib path
# or
xelatex source/tikz.tex                   # TikZ path → PDF vector
mv plot.pdf output.pdf
```

Reproducibility: same data + same script + same matplotlib RC → same PDF. Save the data snapshot (`source/data_used.csv`) so the figure can be regenerated without re-running the whole experiment.

**Image-based**:
```bash
# Skill writes image_request.json; user's environment wraps the vendor call.
# output.png lands in the folder.
```

The user's environment dictates the image-gen tool. The skill emits `image_request.json` in a standard schema and lets the user wire up whichever vendor they have access to. See `figure-prompt-patterns.md` § "Vendor adapters."

After generation, set `status: needs_revision` until Step 4 passes.

## Step 4 — Self-check (compliance against the rules, not aesthetics)

This is a fast, mechanical check **done by Claude in the same session** — it is NOT an external review. The point is to catch the obvious style-rule violations before moving on, not to second-opinion the figure's value.

Things checked in self-check (saved to `self_check.md`):

```markdown
# self_check.md — <fig_id>

**Checked**: <UTC timestamp>
**Verdict**: ready | needs_revision

## Mechanical compliance (per figure-quality.md)
- [ ] Output exists at expected path (output.pdf or output.png as allowed).
- [ ] No in-figure title (matplotlib: no plt.title(); TikZ: no \node[title]; image: no rendered text).
- [ ] Output format matches brief (PDF vector unless brief allows PNG).
- [ ] Aspect ratio matches brief (±5% tolerance).
- [ ] All colors via PALETTE (no rogue hex literals outside the palette).
- [ ] No author / school / OS-path text anywhere in the figure (grep the .tex / scan the PDF text).
- [ ] For data figures: data_used.csv exists; plot.py reads from named files (no hardcoded data).
- [ ] For schematic figures: every node from brief.Content is present (check by node-count and label presence).
- [ ] Filename: matches `<fig_id>.pdf` or `<fig_id>.png` after rename.

## Brief-alignment spot-check
- Claim: <restate brief's claim sentence>
- Does the figure visually deliver this? <yes / partial / no>

## Findings
<bulleted list. Empty if all pass.>

## Decision
ready (no findings) | needs_revision (≥1 finding above)
```

If `needs_revision`: read findings, edit `prompt.md` (bump revision), re-run Step 3. Cap at 3 attempts per figure. On the 4th attempt failure, escalate to user — the brief itself may be wrong.

If `ready`: set `status: ready`, copy `output.pdf` to `stage2_solving/figures/<fig_id>.pdf`.

## What self-check is NOT

- It is not an aesthetic judgment ("does this look good"). That is the writer's judgment when fitting the figure into the paper.
- It is not a check that the figure's *claim is correct*. That requires reading `validation.md` and is part of the final review.
- It is not a check for AI-flavored polish (purple-blue gradients, decorative icons). Those are flagged by the project-level review because they need an outside eye.

Self-check catches the **mechanical** mistakes that block compilation or guarantee a low rubric score.

## Iteration discipline

A figure that has been to self-check twice without "ready" is the highest drift signal in Stage 2. Cap at 3 iterations per figure; on the 4th, escalate to user.

## Mass production

For 8-12 figures in a contest paper, the workflow runs in **parallel**:

- Stage 2 batches all `brief.md` writes in one pass.
- Stage 2 batches all prompts in a second pass.
- Generation runs sequentially per figure but can parallelize across CPU cores.
- Self-check runs immediately after each generation.

The orchestrator's time-budget check applies — if figure generation drifts >0.8 of its sub-budget, drop the lowest-claim figures first.

## When to skip the self-check

One case only: **regenerate-only re-runs** where neither the brief nor the prompt changed and the data diff is within ±20% of the previously-passed version. Log the skip reason in `self_check.md`:

```markdown
Skipped: trivial regenerate, data diff within ±5% of previously-ready version (2026-02-08T14:00Z).
```

## Gating into Stage 3

Stage 3 (`auto-mm-writing`) refuses to `\includegraphics{img/<fig_id>.pdf}` if `figures/<fig_id>/status` is anything other than `ready`. This is enforced in the writing stage's pre-build check.

## Integrity rule alignment

This pipeline is the operationalization of Rule 8 ("Figures are evidence, not decoration"). The brief's "claim" field is the integrity-Rule-8 commitment. Self-check enforces the mechanical surface of the rule (palette, format, no decoration); the deeper part (does the figure actually answer the question the prose raises) is the writer's judgment when fitting the figure into the paper at Stage 3.

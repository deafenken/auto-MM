# Figure workflow — brief → produce → self-check

The default way to make a figure in this skill is NOT "ask the assistant to draw it." It is a structured pipeline: write a spec sheet, produce the figure through one of three channels, and self-check against the style rules. The point is to (a) make the figure's purpose explicit before any pixels are drawn, and (b) keep the audit trail intact across iterations.

External review is **not** per-figure in this skill. The self-check catches mechanical style-rule violations; aesthetics and "does this figure earn its space" are the writer's judgment at Stage 3, not an automated gate.

## Three figure channels — same brief, different production

| Channel | What it is | Production tools | Folder extras |
|---|---|---|---|
| **`type: data`** | Driven by real numbers from `stage2_solving/runs/<exp_id>/`. Scatter, bar, heatmap, convergence, Pareto, sensitivity, route map, Gantt, ROC, etc. | matplotlib / seaborn / NetworkX code, or TikZ; runs on the actual data. | `prompt.md` (code prompt) + `source/plot.py` + `source/data_used.csv` + `output.pdf` |
| **`type: schematic`** | Diagrammatic, no real-data dependency. Model flowchart, system architecture, algorithmic structure, conceptual illustration. | TikZ (default, especially with text labels) OR AI text-to-image (DALL-E / Imagen / Midjourney / Nano Banana / SDXL — only when aesthetic dominates and labels are minimal). | `prompt.md` (TikZ or image prompt) + `source/tikz.tex` *or* `source/image_request.json` + `output.pdf` |
| **`type: sourced`** | Must depict a real-world thing (specific city map, satellite imagery, policy screenshot, product photo, historical artifact). **AI must not generate this.** | Web search → download candidates → choose → cite. See `figure-sourcing.md` for the full protocol. | `search_queries.md` + `sources/` (candidate_NN.png + .meta.json) + `chosen.png` + `attribution.md` |

The full catalog of which figure types fall into which channel is in `figure-types-catalog.md`. The quick rule:

1. Real numbers from your experiments → **`data`**.
2. Specific real-world place / object / document → **`sourced`**.
3. Otherwise (pure concept / illustration) → **`schematic`**.

If two channels could apply: `sourced` wins over `schematic`; `data` wins over `schematic`. Never use `schematic` to substitute for a missing real-world artifact — that is fabrication.

## Per-figure folder layout (the contract)

Each figure lives in its own folder under `stage2_solving/figures/`. The common files are the same; the channel-specific files differ.

```
stage2_solving/figures/
└── <fig_id>/                          # e.g. fig-convergence, fig-model-flowchart, fig-region-map
    ├── brief.md                       # ALL channels — the information document (Step 1)
    │
    ├── prompt.md                      # data + schematic — the generation prompt (Step 2a)
    ├── source/                        # data + schematic
    │   ├── plot.py | tikz.tex | image_request.json
    │   ├── data_used.csv              #   data only — snapshot of numbers used
    │   └── log.txt                    #   build / generation log
    │
    ├── search_queries.md              # sourced — the search plan (Step 2b)
    ├── sources/                       # sourced — candidate downloads + metadata
    │   ├── candidate_01.png
    │   ├── candidate_01.meta.json
    │   └── ...
    ├── attribution.md                 # sourced — citation + license + modifications
    │
    ├── output.pdf | output.png | chosen.png   # the final artifact (channel-dependent name)
    ├── self_check.md                  # ALL channels — style + claim audit (Step 4)
    └── status                         # draft | needs_revision | ready
```

After self-check passes, a copy/symlink lands at `stage2_solving/figures/<fig_id>.<ext>` — that is the path LaTeX references via `\includegraphics{img/<fig_id>}`.

`<fig_id>` is the same name LaTeX uses (`fig-data-flow`, `fig-route-map`, `fig-wuhan-zone`, etc.). One ID = one folder = one figure in the paper.

## Step 1 — Brief (information document)

Template in `figure-brief-template.md`. Required fields (every channel):

- **fig_id** — the same letter LaTeX uses.
- **type** — `data` | `schematic` | `sourced`.
- **paper_section** — which §N this figure appears in.
- **claim** — what is the *one* sentence the figure proves? If you can't write this in one sentence, the figure is unfocused.
- **inputs** — channel-dependent:
  - `data`: which `runs/<exp_id>/result.json` or `tables/*.csv` feeds it.
  - `schematic`: which `stage1_modeling/model.md` section it depicts.
  - `sourced`: a one-sentence description of the real-world subject and why a real image is necessary.
- **content** — bulleted list of what must appear. Specific.
- **style constraints** — references back to `figure-quality.md` rules.
- **reference context** — verbatim quote of the prose line in the paper that will `\ref{}` this figure.
- **out of scope** — what NOT to put in.

Why this step matters: without a written brief, prompts drift between iterations and you converge after 5 mutually-inconsistent versions instead of 1. The brief is the anchor.

## Step 2 — Produce (channel-specific)

### 2a. Channel `data` — code prompt → plot.py / tikz.tex → render

Build a code prompt from `figure-prompt-patterns.md` Pattern A (matplotlib) or Pattern B (TikZ). Save verbatim to `prompt.md`. The prompt names: data source, columns, plot kind, color mapping (PALETTE indices), axis labels with units, aspect ratio, output path. Output is `source/plot.py` or `source/tikz.tex`.

```bash
cd stage2_solving/figures/<fig_id>/
python source/plot.py                     # matplotlib path
# or
xelatex source/tikz.tex                   # TikZ path → PDF vector
mv plot.pdf output.pdf
```

Reproducibility: same data + same script + same matplotlib RC → same PDF. Save the data snapshot to `source/data_used.csv` so the figure can be regenerated without re-running the whole experiment.

### 2b. Channel `schematic` — TikZ code prompt OR image-gen prompt → render

For text-heavy diagrams (model flowcharts, system architecture), use Pattern B (TikZ). For aesthetic concept illustrations with no labels, use Pattern C (image-gen). Save the prompt verbatim to `prompt.md`. Output is `output.pdf` (TikZ) or `output.png` (image-gen).

```bash
# TikZ
xelatex source/tikz.tex
mv tikz.pdf output.pdf

# Image-gen — user's environment wraps the vendor call (DALL-E, Imagen, Midjourney, etc.)
# Skill emits image_request.json; the wrapper writes output.png back into the folder.
```

The user's environment dictates the image-gen tool. The skill emits `source/image_request.json` in a standard schema and lets the user wire up whichever vendor they have access to.

### 2c. Channel `sourced` — write `search_queries.md` → download candidates → choose → cite

This channel has no "prompt." Instead, write `search_queries.md` planning the search, run the queries, download candidates with `auto-mm-solving/assets/download_image.py` (which auto-fills a starter `.meta.json`), choose the best candidate, optionally crop / annotate (recording the modification), and write `attribution.md`. Full protocol in `figure-sourcing.md`.

```bash
python auto-mm-solving/assets/download_image.py \
    --url "<URL>" \
    --out runs/<slug>/stage2_solving/figures/<fig_id>/sources/candidate_01.png \
    --note "matches the boundary in the problem statement"
# fill in candidate_01.png.meta.json's TBD fields by reading the source page
```

After choosing: `cp sources/candidate_NN.png chosen.png` (or crop with Pillow / ImageMagick first), write `attribution.md`, then self-check.

After production (any channel), set `status: needs_revision` until self-check passes.

## Step 3 — Self-check (compliance against the rules, not aesthetics)

This is a fast, mechanical check **done by Claude in the same session** — it is NOT an external review. The point is to catch the obvious style-rule violations before moving on, not to second-opinion the figure's value.

Things checked in self-check (saved to `self_check.md`):

```markdown
# self_check.md — <fig_id>

**Checked**: <UTC timestamp>
**Type**: data | schematic | sourced
**Verdict**: ready | needs_revision

## Universal mechanical compliance (per figure-quality.md)
- [ ] Output exists at expected path (output.pdf | output.png | chosen.png).
- [ ] No in-figure title (caption is LaTeX's job).
- [ ] Output format matches brief (PDF vector unless brief allows PNG).
- [ ] Aspect ratio matches brief (±5% tolerance).
- [ ] No author / school / OS-path / git-remote text visible anywhere.
- [ ] Filename matches `<fig_id>.<ext>` after the final rename.

## Channel-specific (fill in only the rows for this figure's type)

### type=data
- [ ] All colors via PALETTE (no rogue hex literals outside the palette).
- [ ] `source/data_used.csv` exists; `plot.py` reads from named files (no hardcoded data).
- [ ] Numeric values in the figure trace to result.json / tables under runs/<exp_id>/.

### type=schematic
- [ ] Every node / box from brief.Content is present (count + label match).
- [ ] If TikZ: source compiles without errors; no \tikzset{shadow, fadings}.
- [ ] If image-gen: no AI tells (purple-blue gradient, decorative icons, drop shadows, neon).
- [ ] No fabricated real-world content (if the figure looks like a real map / device, switch to `sourced`).

### type=sourced
- [ ] `attribution.md` exists with URL + retrieved_at_utc + license + creator.
- [ ] License permits this use (publication, modification if applicable).
- [ ] Modifications listed in attribution.md match what was actually done (no hidden alterations).
- [ ] BibTeX entry in attribution.md is appendable to references.bib without edits.
- [ ] No misleading representation (no relabeling, no false coloration, no fabricated boundary).
- [ ] Image resolution ≥ 1000 px on the long side for print legibility (unless brief explicitly allows smaller).

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

# EasyMCM2 template — bundled with auto-mm

This is the **EasyMCM2** LaTeX template for MCM/ICM, kept here as a static asset that the writing stage copies into `runs/<slug>/stage3_writing/paper/`.

## Files

- `main.tex` — entry point. Configure team number, problem letter, title here.
- `easymcm2.sty` — the style file. Don't edit unless you know what you're doing.
- `new_command.tex` — user-defined macros.
- `part_1_pre.tex` — introduction, problem restatement, assumptions, notation.
- `part_2_model.tex` — data, model, algorithm, results, sensitivity.
- `part_3_conclusion.tex` — strengths, weaknesses, future work.
- `part_4_Appendix.tex` — AI report (mandatory since 2024 MCM).
- `Memo.tex` — the executive memo / non-technical communication.
- `sections/2-Introduction.tex` — extra section sources if any.
- `img/` — figures (kept empty here; the writing stage symlinks `stage2_solving/figures/` into this folder).

## Source

This template is the publicly distributed EasyMCM2 template. The bundled copy is the version dated 2026-05. Update when COMAP updates its requirements (typically once a year, around the previous fall).

## Build

```bash
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex   # second pass for cross-refs
```

Two passes are required because of `cleveref` and `\Cref` cross-references. The writing stage's build helper runs both passes automatically.

## What to customize per run

In `main.tex`:

- Team control number: `\usepackage[<number>]{easymcm2}`.
- Problem letter: `\problem{<A|B|C|D|E|F>}`.
- Title: `\title{...}`.

In `part_1_pre.tex`:

- Background paragraph (rewrite for the specific problem).
- Problem restatement (paraphrase from `inputs/problems/<X>.pdf`).
- Assumptions block (import from `stage1_modeling/assumptions.md`).
- Our work summary.

In `part_2_model.tex`:

- Replace the placeholder DWTS-flavored content with the team's model, algorithm, results.

The writing stage walks these files in order.

## Why the img/ is empty

The Template.zip we received contains the example paper's figures (DWTS example, ~12MB). They're not relevant to your run. Drop the actual figures from `stage2_solving/figures/` into this `img/` directory (or symlink).

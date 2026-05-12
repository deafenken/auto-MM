# AI Report — MCM/ICM requirement since 2024

Since the 2024 contest cycle, COMAP requires every MCM/ICM submission to include an **AI Report** documenting LLM usage. This file is the protocol for generating it.

## What it is

A separate page (or pages) appended after the main paper. **Not** counted against the 25-page main paper limit. Records:

- Which AI tools were used (ChatGPT, Claude, Gemini, GitHub Copilot, Cursor, etc.).
- What each tool was used for (brainstorming, code, debugging, proofreading, generating figures, translation).
- Representative prompts and the resulting outputs (or paraphrases).
- The team's acknowledgment that they remain responsible for the submission's correctness.

## What it is NOT

- A confession that wins or loses sympathy points. It's a factual record.
- A list of every API call (impractical and uninformative).
- An author-attribution section (do not name team members in it).
- A place to advertise novel uses of AI (the paper itself is where novelty is judged).

## Required structure

```markdown
# AI Report

## Tools used

| Tool | Version / Model | Used for |
|---|---|---|
| Claude | Opus 4.7 | High-level planning, draft prose, code review |
| GitHub Copilot | <version> | Inline code completion |
| Wolfram Alpha | n/a | Symbolic algebra verification |

## Use case 1 — Generating the assumption list

**Tool:** Claude Opus 4.7
**Date:** 2026-02-08
**Prompt summary:** "Given the problem statement and the data recon, generate a numbered assumption list with justifications and sensitivity tags."
**Representative output:** The first 5 assumptions in §2 of the main paper were drafted by the assistant; the team edited each to add a specific justification grounded in literature or the problem statement.

## Use case 2 — Code skeleton for ALNS

**Tool:** Claude Opus 4.7 (via auto-mm skill)
**Date:** 2026-02-08
**Prompt summary:** "Implement an ALNS solver scaffold with destroy/repair operators for our VRP variant."
**Representative output:** The pipeline.py file's structure (entry point, src/data, src/model, src/solve, src/report decomposition) was drafted by the assistant. The team specialized the destroy operators to the green-zone problem feature.

## Use case 3 — Sensitivity analysis interpretation

**Tool:** Claude Opus 4.7
**Prompt summary:** "Given the sweep results CSV, identify the threshold and write the regime-change interpretation."
**Representative output:** §6.2's interpretation of the carbon-price threshold.

## Use case 4 — Anonymity scan

**Tool:** auto-mm-writing skill (using Claude Opus 4.7 internally)
**Used for:** Automated scan of PDF metadata and source for identifying information.

## Use case 5 — Proofreading

**Tool:** Claude Opus 4.7
**Used for:** English grammar checking and academic phrasing across all sections.

## Acknowledgment

The team remains fully responsible for the correctness, originality, and
integrity of this submission. AI-generated content was reviewed, edited,
and verified by team members before inclusion.
```

## Quality criteria

A passable AI report:

- Lists every tool that materially contributed (not Microsoft Word's spell-check; do include LLMs that influenced text or code).
- States the date or week of use roughly.
- Distinguishes between (a) AI-generated content the team used, and (b) AI-suggestion the team rejected.
- Acknowledges responsibility.
- Is honest. If 80% of the prose came from an LLM, say so. Reviewers won't dock honesty.

A failing AI report:

- Claims "we did not use AI" if the team did use AI. This is the worst possible outcome — both a Rule 2-adjacent integrity failure and a likely scoring penalty.
- Provides only a tool list with no use cases.
- Pretends every output was reviewed line-by-line if it wasn't.

## How auto-mm generates it

Since the user is running this skill, the auto-mm skill **is** an AI tool. The AI report mentions:

- Tool: Claude Opus 4.7, used via the auto-mm skill.
- Use cases: ideation (Stage 0 problem scoring), modeling (Stage 1 candidates, model derivation), code (Stage 2 pipeline), writing (Stage 3 prose).

The writing stage generates a draft AI report from `progress.jsonl` events:

```python
# scripts/draft_ai_report.py
import json, pathlib
events = [json.loads(l) for l in open(f"runs/{slug}/progress.jsonl")]
# extract use cases from event semantics
# (problem_chosen → ideation; model_committed → modeling; etc.)
```

The skill writes this draft to `paper/ai-report.tex` (or `.md` → converted), then asks the user to read and approve before building.

## Per-contest variations

- **MCM/ICM 2024+**: mandatory, separate AI Report page (see EasyMCM2's `part_4_Appendix.tex` placement after `\setcounter{page}{1}`).
- **CUMCM**: as of 2026 contest cycle, AI usage disclosure is recommended but not formalized. The skill writes a similar but shorter section in the appendix.
- **Other contests**: ask the user from the year's rule PDF; default to including an AI report unless the rules explicitly prohibit it.

## The page-count subtlety (MCM)

The EasyMCM2 template's main.tex has this pattern:

```latex
\input{part_3_conclusion}
\input{Memo.tex}

% 论文正文到此结束（含Memo），共25页；AI Report不计入正文页数
\label{MainLastPage}
\clearpage

% AI Report 单独开页：页码从1开始
\setcounter{page}{1}
\rhead{\small Page \thepage\ of 1}

\input{part_4_Appendix}
```

The `\label{MainLastPage}` and `\setcounter{page}{1}` ensure the AI report has its own page-of-N numbering, not counted in the 25-page main paper. Don't move these.

If the team adds a 2-page AI report (more common in larger submissions), update `\rhead{\small Page \thepage\ of 2}` accordingly.

## Verification

Before ship, the orchestrator checks:

- `ai-report.tex` (or equivalent) exists when family=MCM.
- The compiled main.pdf contains an AI report section (greppable via `\input{part_4_Appendix}` or similar).
- The AI report does not contain author names (Rule 2 still applies).
- The acknowledgment paragraph is present.

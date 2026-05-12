---
name: auto-mm-modeling
description: >-
  Stage 1 of auto-mm. Decomposes the chosen problem into sub-questions Q1..Qk
  (each with explicit inputs, outputs, hard/soft constraints, evaluation
  criterion); writes a numbered assumption list with justification; builds a
  single consolidated notation table; explores 2-4 candidate model families
  with pros/cons and a verdict; commits to one formal model (objective,
  constraints, derivations) in model.md. Enforces the four model-side
  integrity rules: problem-statement-first (Rule 1), real-citations-only
  (Rule 3), AI/ML must address real uncertainty (Rule 4), algorithms must
  be justified by problem structure (Rule 5). Refuses to hand off until the
  notation table is complete and every formula references it.
---

# Stage 1 — Modeling

The highest-leverage stage. Bad modeling cannot be rescued by good solving — and good modeling makes solving and writing dramatically easier.

## Trigger

- Delegated to by the orchestrator after `stage0_triage/hand_off.md` is written and the problem is locked.
- Can be invoked directly: `auto-mm-modeling <run_slug>` to revise the model. Stage 2's existing experiments are NOT invalidated automatically — if the model changes materially, `stage2_solving/` needs re-running and that cost goes against the time budget.

The orchestrator will not let this stage run if `run.yaml.chosen_problem` is null.

## Inputs

- `runs/<run_slug>/run.yaml`
- `runs/<run_slug>/stage0_triage/hand_off.md` + the files it references (`problem_choice.md`, `data_recon.md`)
- `runs/<run_slug>/inputs/problems/<chosen>.pdf` — re-read end-to-end; the problem statement is the authority (Rule 1)

## Outputs (the contract)

```
runs/<run_slug>/stage1_modeling/
├── problem_decomposition.md   # Q1..Qk with I/O, hard/soft constraints, metric
├── assumptions.md             # numbered, justified, with sensitivity tags
├── notation.md                # the single consolidated symbol table
├── candidates.md              # 2-4 candidate families, pros/cons, verdict
├── model.md                   # the chosen formal model (objective, constraints, derivations)
├── literature.md              # real, verifiable references that support the choices
└── hand_off.md
```

Exact schemas in `auto-mm/references/state-contract.md`.

## Workflow

### 1. Re-read the problem statement

This is non-optional. Even if Stage 0 quoted the statement, this stage re-reads it. Identify:

- Every **quantitative constraint** stated in the problem (numbers, thresholds, ranges).
- Every **definitional sentence** ("a customer is considered served if ...", "green zone is defined as ...").
- Every **deliverable** beyond the model (memo, comparison, sensitivity, recommendation).
- Every **ambiguity** that the team must decide.

Write these to a `problem_decomposition.md` "Source of truth" section, with file:line or paragraph references. This becomes the integrity-Rule-1 trace — when the agent later writes a formula, it can cross-check against this list.

### 2. Decompose into sub-questions

For each sub-question Q1..Qk the problem asks:

```markdown
## Q<N> — <one-sentence what>

- **Input**: <which data files / which prior outputs>
- **Output**: <what's produced; format>
- **Hard constraints** (from problem statement):
  - <bulleted, with verbatim quote where ambiguous>
- **Soft constraints / objectives**:
  - <bulleted>
- **Evaluation criterion**:
  - <how the team will judge their own solution: minimize cost? maximize accuracy? Pareto front?>
- **Dependencies**: <which other Q must be done first>
```

If two sub-questions are tightly coupled (Q2's input is Q1's output), say so. If they can be answered independently, say that too — Stage 2 can parallelize.

### 3. Write the assumption list

Each assumption is **numbered** and follows this structure:

```markdown
### Assumption N — <one-line statement>

**Justification:** <1-3 sentences. Cite the problem statement, a real source, or a domain principle.>

**Affects:** <which Q, which formula, which variable>

**Sensitivity tag:** <"baseline" | "to-sweep" | "fixed-by-problem">
```

Use these tags to tell Stage 2 what to vary in sensitivity analysis. "fixed-by-problem" assumptions are NEVER touched in sensitivity (Rule 1).

The experience README §5 calls out specific assumption patterns that go wrong. Don't repeat them:

- Service time `δ_i = δ_0 · I_i + α · w_i` (fixed parking + variable unloading) — if the problem gives both terms, never collapse to one.
- Time-varying network with FIFO violations: introduce a waiting variable; document the operational interpretation (delayed dispatch / driver rest / charging).
- Heterogeneous fleets: assumption must preserve per-vehicle parameters; never flatten to one truck type.

### 4. Build the notation table

A single consolidated `notation.md`. Structure (in this order):

1. **Sets and indices** — e.g. `I` = customers, `V` = vehicles, `T` = time steps.
2. **Parameters (with units!)** — input values; group by source (problem-given vs derived vs assumed).
3. **Decision variables** — what the solver chooses; specify domain.
4. **Auxiliary variables** — intermediates introduced for linearization or readability.
5. **Functions** — any named function `f(·)` used in formulas.

Rules for the notation table:

- Every symbol used in any formula in `model.md` must appear here.
- Every magic number ("16:00", "10 km", "5 vehicles") must be replaced by a symbol with the value as a parameter. The experience README §4 explicitly bans `T_lim=960` literals inside formulas.
- Units matter: cost in 元, distance in km, time in minutes — pick once and convert consistently.

The orchestrator's integrity gate cross-greps formulas against the table. Missing entries block hand-off.

### 5. Propose candidate model families

In `candidates.md`, list **2 to 4** candidate model families. Each entry:

```markdown
## Candidate <N>: <family name>

**Sketch**: <one paragraph: what the model looks like, what the decision variables are.>

**Pros**: <bulleted, ≤4 items>
**Cons**: <bulleted, ≤4 items>
**Implementation cost**: <hours estimate>
**Risk**: <what makes this fragile>

**Justification for problem structure**:
<one paragraph linking the model's strength to a feature of this specific problem.>
```

Then a final section "Verdict": which family wins and why. Document the **deciding factor** — usually one of (implementation cost given remaining hours / data sufficiency / problem-statement compatibility / differentiator value).

Integrity rules at this step:

- **Rule 4 — AI/ML must address real uncertainty.** If a candidate includes a neural network, it must name the real-world uncertainty it absorbs (forecasting future demand, classifying ambiguous intents, learning a heuristic where the exact problem is intractable). "We use a NN for accuracy" is not a justification.
- **Rule 5 — Algorithms justified by problem structure.** If a candidate names ≥3 metaheuristics, each must point to a problem feature it addresses. Otherwise drop one.

If both rules pass for the chosen candidate, mark `integrity_check: ok` at the bottom of `candidates.md`. The orchestrator's gate reads this line.

### 6. Write the formal model

`model.md` — the centerpiece. Structure:

```markdown
# Formal model — <chosen family>

## Decision variables
<short list, referencing notation.md>

## Objective(s)
<formula(s) in LaTeX, plain-English statement after each, units called out>

## Constraints
### (a) <Group name, e.g. flow conservation>
<numbered formulas; one paragraph of explanation after the group>

### (b) <Group name, e.g. capacity>
...

## Derivations
<any non-trivial step: linearization, dualization, reformulation.
Show enough math that a reviewer trusts the chain.>

## Why this family (1 paragraph)
<one paragraph linking back to candidates.md verdict>

## Known limitations
<bulleted list of what the model does NOT capture, deferred to sensitivity or future work>
```

Every formula references symbols from `notation.md`. No literals.

Every constraint group has a 1-paragraph English explanation. The reviewer should be able to read the prose and understand the math without reverse-engineering.

### 7. Find real supporting citations

`literature.md` holds the references that justify modeling choices. Each entry has:

- Author(s), year, title, venue, DOI / arXiv ID / stable URL.
- **One-line relevance**: what this paper supports in `model.md`.

Constraints (Rule 3):

- Use WebSearch / WebFetch to verify each citation exists. Do not write `literature.md` entries from memory of training data.
- If a fact needs a citation and no real one exists, restate the fact as a team assumption in `assumptions.md` or remove the unsupported claim.
- If the contest is CUMCM, prefer Chinese-core or English papers with stable archives; if MCM, English with DOI.

The orchestrator's gate refuses to advance if any entry has `unverifiable: true` set or if a `?` appears in a DOI.

### 8. Write `hand_off.md`

```markdown
# Stage 1 → Stage 2 hand-off

## What I did
- Decomposed Problem <X> into Q1..Q<k>. Each has I/O, constraints, metric.
- <N> numbered assumptions written, tagged by sensitivity role.
- Built notation.md: <S> sets/indices, <P> parameters, <V> decision variables.
- Evaluated <C> candidate model families; committed to <chosen>.
- Wrote model.md with <O> objectives and <C_total> constraints in <G> groups.
- literature.md has <R> verified references.

## What's true now
- Chosen model: <chosen family> in <family taxonomy>.
- Headline objective: <e.g. minimize total cost in 元>.
- Decision-variable size estimate: <O(|V|·|I|·|T|) = ~N variables>.
- Solver candidates flagged for Stage 2: <e.g. Gurobi for MILP small instance + ALNS for full>.
- Open assumptions awaiting sensitivity sweep: <list of Assumption N: name>.
- Hours remaining in budget: <H>. Stage 2 budget: <H2>.

## What you should do next
Stage 2: implement pipeline.py reading from inputs/data/ and writing to
stage2_solving/runs/<exp_id>/result.json. The minimum required runs are:
(1) a baseline (deliberately weak; one of: greedy, single-fold, no-ML);
(2) the main run with the model in model.md;
(3) a small-instance exact solve (≤15 customers / ≤10 nodes) to report
optimality Gap for the main run;
(4) at least one ablation on the most-important architectural choice;
(5) sensitivity sweeps on the assumptions tagged 'to-sweep'.
Figures go to stage2_solving/figures/ as PDF vectors. Reference
auto-mm-solving/references/algorithm-selection.md for the algorithm-to-
structure mapping; reference auto-mm-solving/references/figure-quality.md
before generating any figure.
```

Append `progress.jsonl` event `model_committed`. Exit.

## Idempotency

If `model.md` already exists when this skill runs:

- If `--revise` was passed → re-derive only the section the user named; keep others. Append `model_revised` event.
- Otherwise → log `modeling_skipped` and exit 0. Switching models silently is the worst kind of state corruption — it desyncs Stage 2.

## Failure modes

| Symptom | Action |
|---|---|
| Re-reading the problem reveals a constraint Stage 0 missed | Re-decompose. Update `problem_decomposition.md`. Re-score candidates. |
| Notation table can't fit on one page after consolidation | The model is too complex. Recommend a simplification in `candidates.md`. |
| All candidate families have similar pros / cons | Use the rubric again: prefer lower implementation cost, then higher differentiator. |
| AI/ML candidate cannot name a real uncertainty | Reject the candidate; Rule 4 fail; do not "make up" an uncertainty. |
| Citation lookup keeps returning suspect/fake papers | Drop the supporting claim; restate as a team assumption. |
| Budget pressure: only 4h left in this stage | Cut: stop at 2 candidates, write the model, defer extra derivations to appendix. |

## When to load which reference

| File | Load when |
|---|---|
| `references/model-zoo.md` | Step 5 — generating candidate families |
| `references/notation-style.md` | Step 4 — writing the symbol table |
| `references/assumption-writing.md` | Step 3 — drafting numbered assumptions |
| `references/pitfalls-from-experience.md` | ALWAYS in this stage — these are user-encoded landmines from past contests |
| `references/citation-discipline.md` | Step 7 — building literature.md |
| `auto-mm/references/integrity-rules.md` | Step 5 (Rules 4 & 5), Step 7 (Rule 3) |
| `auto-mm/references/state-contract.md` | Writing any output file |
| `auto-mm/references/escalation-policy.md` | Any failure mode in the table above |

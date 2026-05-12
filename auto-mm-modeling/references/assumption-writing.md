# Assumption writing — making each line defensible

The assumption list is where the paper's modeling chops show. A long list of vague assumptions screams "we didn't think about it"; a short list of specific assumptions with grounded justification reads as careful.

## Template (per assumption)

```markdown
### Assumption <N> — <one-line claim>

**Justification:** <1-3 sentences. One of the four allowed sources below.>

**Affects:** <which sub-question(s), which formula(s), which variable(s) in notation.md>

**Sensitivity tag:** <one of "fixed-by-problem" | "baseline" | "to-sweep">

**If wrong:** <one sentence: how the conclusion changes if this assumption is invalidated>
```

## Allowed justification sources

In rough order of strength:

1. **Problem statement** — quote the verbatim sentence with a paragraph reference.
2. **Empirical fact in the data** — point to a value or distribution in `data_recon.md`.
3. **Cited literature** — reference an entry in `literature.md`.
4. **Domain principle** — a well-known result or standard practice (state it concretely; "physics" is not a justification, "Newton's second law applies to this system" is).

If none of the four applies, the assumption is a **team judgment**. Mark it as `team_judgment: true` and prepare to defend it in writing. Sensitivity should usually sweep these.

## Sensitivity tags — what they mean

- **`fixed-by-problem`** — the problem statement specifies the value. Sensitivity NEVER sweeps these. Doing so would test "what if the problem were a different problem" — useless and a Rule 1 violation.
- **`baseline`** — the value is reasonable; we lock it for the main run. Sensitivity may sweep it as a secondary exercise, not a headline finding.
- **`to-sweep`** — explicit sensitivity target. Stage 2 sweeps these and reports the impact in `sensitivity.md`.

## Anti-patterns to refuse

### Anti-pattern 1: "We assume the data is accurate."
This is filler. Either show that you checked accuracy (`data_recon.md` anomalies section), or treat outliers explicitly (different assumption: "we exclude rows where weight < 0").

### Anti-pattern 2: "We assume the model is correct."
Tautology. The model is what you build; assuming it correct is not an assumption, it's a confession.

### Anti-pattern 3: "We assume normality."
Why? Cite a test (Shapiro-Wilk, QQ plot, sample size + CLT argument). "Just because" is not a justification.

### Anti-pattern 4: "We assume the parameter equals 0.5."
Where does 0.5 come from? Find a source, derive it, or tag the assumption `team_judgment: true` and put 0.5 on a sensitivity sweep.

### Anti-pattern 5: "We assume the problem is well-defined."
Don't even write it. If the problem isn't well-defined, that's a Rule 1 issue and needs an escalation to the user, not an assumption.

## Assumption count discipline

For a 25-page paper:

- 4-8 assumptions: a tight, defensible list. Aim for this range.
- 9-15 assumptions: getting long; check for redundancy.
- 16+: probably padded with anti-patterns. Trim.

The point is not to maximize — it's to surface the assumptions a reviewer would otherwise spot and ask about.

## Cross-stage handoff

For every `to-sweep` assumption, Stage 2 must produce at least 3 points in the sweep (e.g., low / baseline / high) and write a one-paragraph insight in `sensitivity.md`. If Stage 2 cannot sweep an assumption due to compute, escalate to the user rather than silently skipping.

## Worked example (from 华中杯 A 题)

```markdown
### Assumption A4 — Service time has a fixed component plus a per-unit variable component

**Justification:** Real-world unloading involves a fixed setup (park, secure, paperwork) and
variable handling proportional to weight. The literature on green-zone VRP (cite [Dauer2018])
models service time as $\delta_i = \delta_0 + \alpha d_i$ where $\delta_0$ is fixed minutes
and $\alpha$ is per-kg minutes.

**Affects:** Q1 (route planning), Q2 (cost calculation). Formula in §4.2.1. Symbols
$\delta_0, \alpha$ in notation.md.

**Sensitivity tag:** baseline. The problem statement does not fix these; standard literature
values (δ₀=5min, α=0.15min/kg) are used in main run.

**If wrong:** Underestimating service time overstates throughput; total cost would be
underestimated by ~3-7% per the problem's distance distribution.
```

This is what each entry should look like. Specific, traceable, with a "if wrong" sentence that signals "I thought about this."

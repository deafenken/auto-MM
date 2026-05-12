# Escalation policy — when to stop and ask the human

The orchestrator stops and asks the user instead of guessing whenever one of the following is true.

## Hard escalations (always)

| Trigger | What to write | What to wait for |
|---|---|---|
| Problem statement and data disagree (Rule 1) | `escalation: rule1_disagreement` in current `hand_off.md`, quoting both sources verbatim. | User decides which interpretation is "main" and which is "sensitivity." |
| Anonymity scan finds a hit (Rule 2) | `escalation: anonymity_hit` with the exact match string and the file/line. | User confirms it's a true positive and provides the redacted text. |
| A citation cannot be verified (Rule 3) | `escalation: unverifiable_citation` listing the bibkey and the failed lookup. | User provides a real source, restates the claim, or removes it. |
| AI/ML module without uncertainty justification (Rule 4) | `escalation: ai_module_unjustified` quoting `candidates.md`. | User justifies, removes, or accepts the risk in writing. |
| Stage drift > 20% over budget (Rule 7) | `escalation: budget_overrun` with `(stage, used_h, target_h, drift_ratio)`. | User chooses: cut scope, steal from later stage, extend total budget. |
| Resume finds inconsistent state | `escalation: state_inconsistency` listing the conflicting files. | User clarifies which to trust, or runs `--restart-stage <N>`. |
| User-provided input is malformed (problem PDF unreadable, data file corrupt) | `escalation: bad_input` with the parse error. | User fixes or replaces the input. |
| Deadline already passed | Refuse to start. Print "deadline <utc> was at <utc>." | n/a |

## Soft escalations (only outside lockdown mode)

The orchestrator surfaces these but continues with a sensible default if no answer in 30 minutes:

| Trigger | Default action |
|---|---|
| Stage budget hits 80% | Tell current stage to start wrapping. |
| Sensitivity sweep would take longer than remaining solving budget | Halve the sweep grid. |
| Figure count exceeds 25 | Drop the lowest-value ones (no `\ref` from body). |
| Abstract exceeds one page | Shorten the longest sub-problem paragraph. |

In lockdown mode (last 6h), soft escalations are upgraded to hard escalations — every change asks the user.

## How to write an escalation block

Append to the current stage's `hand_off.md` (creating it if needed), under a top-level `## ESCALATION` heading. Format:

```markdown
## ESCALATION — <kind> — <ts_utc>

**What happened:**
<two sentences of context, with file:line references>

**What I think the options are:**
1. <option A> — pros / cons
2. <option B> — pros / cons
3. <option C> — pros / cons

**My recommendation:** <one of the above, with one-sentence reasoning>

**What I will do if you don't reply in 30 minutes:** <only for soft escalations>

**To unblock me, reply with one of:**
- `proceed A` / `proceed B` / `proceed C`
- `proceed custom: <free-text instruction>`
- `pause` (writes PAUSE sentinel)
```

The orchestrator then exits, writing a `.heartbeat` with `stage: awaiting_user`.

## What never escalates

Routine decisions that the agent owns:

- Choice of optimizer flags (Adam vs AdamW etc.)
- Whether to use 5-fold or 10-fold CV
- Color choice in figures (within the style guide)
- LaTeX section ordering as long as the required sections are all present
- Code variable names, file organization within `stage2_solving/`

The principle: escalate when the decision changes the **paper's claims** or the **submission's validity**. Otherwise, decide and move on.

## Don't escalate twice for the same thing

Before opening an escalation, check `progress.jsonl` for an existing `event: escalation, kind: <kind>` in the current stage. If one exists and is unresolved (no subsequent `escalation_resolved` event), do not open a duplicate — re-print the existing block and exit.

## Resolution

When the user replies, append to `progress.jsonl`:

```json
{"ts_utc":"...","stage":"stageN","event":"escalation_resolved","kind":"...","resolution":"proceed B"}
```

Then resume from the micro-step that triggered the escalation, treating the user's choice as input.

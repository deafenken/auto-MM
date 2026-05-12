# Codex audit — 2026-05-12

External code review of the auto-mm skill package performed by OpenAI `codex` CLI (`codex-cli 0.130.0`) in read-only mode. Two passes: initial scan, then a recheck after fixes were applied. The reviewer had no prior context for either pass (separate sessions).

## Round 1 — initial scan (2026-05-12 16:11Z)

Codex identified **22 issues**: 7 Blockers, 11 Important, 4 Minor.

### Blockers (7)

1. **Hand-off contract gate mismatch** — `state-contract.md` required "exactly three short paragraphs" while every `SKILL.md` uses heading + bullets; a literal gate would block every transition.
2. **Stage 3 packaging path inconsistency** — script mixed repo-root paths with relative `paper/` paths; cwd-dependent and broken from any single starting directory.
3. **CUMCM template missing** — advertised as first-class but `cumcm-template/` was a placeholder README only.
4. **MCM template was the DWTS example** — hardcoded team `2603956`, `\problem{C}`, DWTS title/abstract/body. Not a neutral starting scaffold.
5. **Anonymity scan false positives** — scanned `.sty` (catches maintainer GitHub URLs) and treated any non-empty `/Producer` / `/Creator` PDF metadata as a hit; blocked its own template.
6. **Completion event names mismatched** — protocol expected `build_ok`; Stage 3 actually wrote `paper_built` and `submission_packaged`. Supervisor never recognized completion.
7. **Validation requirement conflict** — `auto-mm-solving/SKILL.md` mandated baseline + exact-Gap + ablation; `validation-protocol.md` allowed three-of-four with cross-method substitute. Inference/open-ended problems would be blocked.
8. **Orphan-label grep broken** — used basic `grep` with extended-regex syntax; would miss `\Cref{...}` and falsely flag papers.

### Important (11)

State contract omitted multiple required files; bibliography filename drift (`main.bib` vs `references.bib`); figure-workflow not wired into Stage 2; `from src.style import …` mismatch with bundled `figure_style.py`; helper scripts (`anonymity_scan.py`, `build.sh`) referenced but absent; Rule 5 enforcement target inconsistent; Rule 7 escalation file name wrong (`recommendations.md` not in contract); Stage 0 atomic-write violation; abstract grep too narrow (missed comma-thousands and bare integers); supervisor ignored `max_runtime_hours`; PAUSE vs deadline-as-source-of-truth conflict; undeclared `yq` dependency.

### Minor (4)

READMEs missing the new figure-pipeline files; `review.md` terminology residue from earlier design; anonymity-scan prose overpromised "common Western given names"; macOS sidecar `._*` files in the working tree.

### Overall verdict — Round 1

> *The suite has the right high-level architecture, but the state contract, enforcement gates, figure pipeline, and writing/package pathing are not yet tight enough for a real unattended 72-96 hour contest run. The largest risks are not prose quality; they are contract drift and gates that either are not wired or would falsely block the final package.*

## Round 2 — recheck after fixes (2026-05-12 17:00Z, fresh codex session)

The author addressed all 22 findings; codex recheck reported:

- **20 RESOLVED** (every Blocker except #3 + #5, every Important, every Minor)
- **2 PARTIAL** (B3, B5)

After a follow-up commit addressing the two PARTIALs:

- B3 (CUMCM) — README wording changed from "first-class profiles" to explicit "MCM bundled; CUMCM is supported but bring-your-own-template," with the bundling rationale explained.
- B5 (anonymity docs) — `references/anonymity-check.md` rewritten to match the actual scanner (`/Producer`+`/Creator` excluded; `.sty`/`.cls` not scanned).

### Final verdict

All 22 findings closed. The skill package is ready as a v0.2 reference: MCM path is end-to-end runnable from the bundled scaffold; CUMCM path is wired but requires the user to drop the year's official template in (deliberate — the official template changes annually and license terms vary by distribution channel).

## Reviewer command (for reproduction)

```bash
codex exec --sandbox read-only --skip-git-repo-check --color never \
    -o codex_review.md - < codex_review_prompt.md
```

The exact prompt is available in commit `e1a5b1d`'s parent tree at `/tmp/codex_review_prompt.md` (one-shot; not persisted in this repo to avoid stale prompt drift).

## Files affected by the round-2 fixes

```
auto-mm/SKILL.md
auto-mm/assets/supervisor.sh
auto-mm/references/{state-contract,integrity-rules,long-running-protocol}.md
auto-mm-triage/SKILL.md
auto-mm-solving/SKILL.md
auto-mm-solving/references/{figure-quality,figure-workflow,figure-brief-template,figure-prompt-patterns}.md
auto-mm-writing/SKILL.md
auto-mm-writing/assets/{anonymity_scan.py,build.sh}
auto-mm-writing/assets/mcm-template/{main.tex,Memo.tex,part_1_pre.tex,part_2_model.tex,part_3_conclusion.tex,part_4_Appendix.tex}
auto-mm-writing/references/{abstract-writing,anonymity-check}.md
README.md, README.zh-CN.md, CLAUDE.md, .gitignore
```

Commit landing all 22 fixes: `e1a5b1d`.

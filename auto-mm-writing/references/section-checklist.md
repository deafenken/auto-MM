# Section checklist — per contest family

The writing stage builds `section_checklist.md` for the run by adapting the template here to the contest profile.

## MCM / ICM

| Section | Required | Notes |
|---|---|---|
| Title + team header | yes | from `\title{}` + `easymcm2.sty` automation |
| Summary Sheet (abstract on cover) | yes | one page; hard numbers per Rule 9 |
| Table of Contents | yes | auto from `\tableofcontents` |
| Introduction / Background | yes | restate the problem domain briefly |
| Problem Restatement | yes | paraphrase, not verbatim copy |
| Assumptions + Justifications | yes | numbered, each with a Why |
| Notation table | yes | single consolidated table |
| Data preprocessing | yes if data is given | including anomaly handling |
| Model derivation | yes | grouped constraints, prose explanations |
| Algorithm | yes | per-component justification (Rule 5) |
| Results | yes | with figures and quantitative comparisons |
| Sensitivity analysis | yes | one subsection per to-sweep assumption |
| Strengths & Weaknesses | yes | honest, including known limitations |
| Memo / Letter (non-technical) | yes (when problem asks) | graded separately |
| References | yes | real entries only |
| Appendix: code | yes | machine-readable; or in supporting package |
| **AI Report** (since 2024) | yes | separate page, not in main page count |

Page budget: 25 pages including memo, excluding references/appendix/AI report. The template's `\label{MainLastPage}` ensures the page count is set correctly.

## CUMCM (国赛)

| Section | Required | Notes |
|---|---|---|
| 题目 (title) | yes | |
| 摘要 + 关键词 | yes | 一整页，无图 |
| 问题重述 | yes | |
| 问题分析 | yes | 比 MCM 更重的章节 |
| 模型假设 | yes | numbered, with justifications |
| 符号说明 | yes | 一张表 |
| 模型的建立与求解 | yes | per sub-question |
| 模型的检验 | yes | sensitivity + validation |
| 模型的评价 | yes | 优点 / 缺点 / 推广 |
| 参考文献 | yes | 真实可核查 |
| 附录 | yes | 代码 + 长表 |

Page budget: 25 pages total typical; check the year's official rules.

## 其他赛事 (华中杯, 妈杯, 数维杯, 校赛, etc.)

Inherit from the matching profile (中文 → CUMCM, English → MCM) and override per the year's rule PDF. Common variants:

- **华中杯**: shorter than CUMCM (often 15-20 pages), 1.5x line spacing, similar required sections.
- **妈杯 (五一)**: similar to CUMCM, sometimes drops the 模型评价 section.
- **数维杯 (中国研究生数学建模竞赛)**: similar to CUMCM, often emphasizes 创新性.
- **MathorCup / 高校赛**: similar to CUMCM, often with stricter formatting rubrics.

The user supplies the rule PDF during first-invocation; the writing stage greps for "page", "section", "anonymous" to surface the year's specifics, then asks the user to confirm.

## How the checklist is consumed

For each row marked Required:
- If Present: yes → green check in the rendered `section_checklist.md`.
- If Present: no → blocks the hand-off; orchestrator escalates.

Per-section presence is detected by greppable section commands:

```bash
# Example: detect "## Assumptions" or "\section{Assumptions}"
grep -E '^(##\s+Assumptions|\\section\{Assumptions\}|\\section\{模型假设\})' paper/*.tex
```

The grep patterns are kept in the writing stage's helper script so they evolve with the templates.

## Empty section trap

A section that is "present" but contains only a placeholder (e.g., "TODO: write this") is worse than missing — the orchestrator's gate greps for forbidden tokens:

- `TODO`
- `FIXME`
- `XXX`
- `<placeholder>`
- Lorem-ipsum
- `(rewrite this)`
- empty `\section{...}\n\\section{...}` patterns

Any hit → escalate with the file + line. The user must clear these before ship.

## Per-section size guidance

For a 25-page paper, very approximate:

| Section | Pages |
|---|---|
| Summary / 摘要 | 1 |
| Introduction + Restatement + Our Work | 2-3 |
| Assumptions + Notation | 1-2 (often shared on one page each) |
| Data | 1-2 |
| Model | 4-6 |
| Algorithm | 2-3 |
| Results | 3-4 |
| Sensitivity | 2-3 |
| Strengths/Weaknesses | 1 |
| Memo (MCM) | 1-2 |
| References | ~1 |
| Appendix | as needed |

Hitting these is not a goal; readability is the goal. But significant deviation (e.g. 10-page Model section in a 25-page paper) is a red flag — the section is probably padded.

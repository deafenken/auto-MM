# Contest types — how 国赛 / 美赛 / 其他 differ in this skill's eyes

Different contests have different rubrics, page limits, formatting requirements, and idiom. The orchestrator routes to a contest-specific profile in `run.yaml.contest.family` and `auto-mm-writing` picks the template accordingly.

## MCM / ICM (美赛, COMAP)

- **Org**: COMAP (Consortium for Mathematics and Its Applications).
- **Language**: English, mandatory.
- **Length**: typically 96 hours (Thursday 17:00 EST → Monday 20:00 EST).
- **Problems**: A, B, C are MCM; D, E, F are ICM. Different problem sets, same submission portal.
- **Team**: 3 students, advised by one faculty member. Solo not allowed.
- **Paper**: 25 pages max **including** memo/letter/summary; **excluding** references/appendices/AI report.
- **Required components**:
  - Summary sheet (1 page).
  - Problem restatement.
  - Assumptions with justification.
  - Notation / variable definitions.
  - Model derivation.
  - Algorithms.
  - Results, sensitivity, strengths & weaknesses.
  - Memo / letter / non-technical communication (problem-specific, **graded separately**).
  - References.
  - **AI report** (mandatory since 2024) — separate page after main paper, documents LLM usage.
  - Appendix with code.
- **Style**: Times Roman or Palatino, 12pt. Margins 1 inch. Page numbers required.
- **Template**: EasyMCM2 (`auto-mm-writing/assets/mcm-template/`). The `easymcm2.sty` handles team number, problem letter, page header, summary sheet.
- **Submission**: PDF only, named after team control number.
- **Awards**: Outstanding > Finalist > Meritorious > Honorable Mention > Successful Participant.

### MCM rubric emphases

1. **Modeling sophistication** — judges love clean math, derivations, and clear notation.
2. **Sensitivity & error analysis** — must be present and substantive.
3. **The non-technical "memo"** — graded by separate readers; needs to land for a non-mathematician audience.
4. **Executive summary on page 1** — sometimes the only page a triage judge reads.

## CUMCM (国赛, 全国大学生数学建模竞赛, 高教社杯)

- **Org**: China Society for Industrial and Applied Mathematics (CSIAM) and 高教社.
- **Language**: 中文 (mandatory; English optional supplement for some problem sets).
- **Length**: 72 hours (Thursday 18:00 → Sunday 20:00 Beijing time).
- **Problems**: A, B, C (本科组); D, E (专科组).
- **Team**: 3 students. Solo not allowed.
- **Paper**: typically 25 pages incl. references; appendix with code can extend.
- **Required components** (本科组 standard):
  - 题目 / 摘要 / 关键词 (摘要 = full page, no figures).
  - 问题重述.
  - 问题分析.
  - 模型假设 (numbered, justified).
  - 符号说明 (a single consolidated symbol table).
  - 模型的建立与求解 (per sub-question).
  - 模型的检验 (validation + sensitivity).
  - 模型的评价 (strengths, weaknesses, improvements).
  - 参考文献.
  - 附录 (code, supporting tables).
- **Style**: 宋体正文 + Times New Roman 数字英文, 小四 or 12pt, 1.5x line spacing typical. 公式编号靠右.
- **Template**: 高教社官方模板 `cumcm-template/` (placeholder — add the year's template when starting).
- **Submission**: PDF + 支撑材料 (source code, data, figures) zipped. 论文 PDF 单独提交.
- **Awards**: 全国一等奖 > 全国二等奖 > 省级一等奖 > 省级二等奖 > 省级三等奖 > 成功参赛.

### CUMCM rubric emphases

1. **题意理解准确** — the most common kill is misreading the problem. Top of priority.
2. **模型科学合理** — derivation must be defensible, parameters must have sources.
3. **求解算法合适** — algorithm chosen for the problem, not for showing off.
4. **结果分析充分** — sensitivity, validation, comparison with baseline.
5. **论文规范** — formatting matters more than in MCM; bad typography is penalized.

## 华中杯 / 妈杯 / 五一杯 / 数维杯 / 校赛 etc.

These vary widely. The orchestrator does not have specific profiles for each; instead it treats them as **derivative**:

- If 中文 + 国内 → inherit CUMCM defaults; override page count, deadline, and required sections from `run.yaml.contest`.
- If English → inherit MCM defaults.
- For unfamiliar contests, the orchestrator asks the user during triage to confirm:
  - Page limit
  - Required sections
  - Anonymity rule (most demand blind submission)
  - Whether code goes into the paper appendix or a separate package
  - Submission format (PDF only? PDF + zip of sources? online portal?)

## Profile selection at orchestrator start

```python
contest_family = ask_user_choose([
    "MCM / ICM (美赛, English, 96h)",
    "CUMCM (国赛, 中文, 72h)",
    "Other (you'll tell me the rules)"
])

if contest_family == "MCM":
    profile = load_profile("mcm")
elif contest_family == "CUMCM":
    profile = load_profile("cumcm")
else:
    profile = ask_user_inline_rules()

run_yaml.contest.family = profile.family
run_yaml.contest.variant = profile.variant
run_yaml.contest.year = ask_user_year()
run_yaml.contest.language_required = profile.language
run_yaml.deadline_utc = ask_user_deadline()
run_yaml.budget.total_hours = (deadline - now).total_hours
```

The orchestrator never silently chooses a profile. If the user is on `auto-mm` without saying which contest, the very first question is "which contest are you running?".

## What the profile decides

| Field | MCM | CUMCM | Other |
|---|---|---|---|
| `language_required` | en | zh | ask |
| Paper template | EasyMCM2 | cumcm-template | ask user to drop one |
| Required sections | from MCM list above | from CUMCM list above | ask |
| Default page budget | 25 (incl. memo) | 25 (incl. references) | ask |
| Anonymity scan terms | English names, US schools, advisor titles | 中文姓名、学校、指导老师 | union of both + user-supplied |
| Bibliography style | numbered, IEEE-ish | numbered GB/T 7714 | inherit |
| Figure caption position | below figure | below figure | below |
| AI-report mandatory | yes (since 2024) | no (as of 2026; check rule) | ask |

When in doubt, read the contest's official rule PDF for the current year. Profiles encode the long-stable defaults, not the year-by-year edits.

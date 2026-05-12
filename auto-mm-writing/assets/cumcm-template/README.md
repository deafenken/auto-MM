# CUMCM (国赛) LaTeX template — REQUIRED but not bundled

This directory is intentionally a placeholder. The CUMCM template is **NOT bundled** with this skill because:

1. The official template changes year to year (新的题号样式、字体、页边距).
2. License terms vary by distribution channel; bundling risks shipping something the team is not allowed to use.

**First-invocation behavior**: if `run.yaml.contest.family == "cumcm"` and this directory contains only this README (no `.tex` file), `auto-mm-writing` will block at Step 1 (template copy) with the message:
> "CUMCM template missing. Drop the year's official template files into `auto-mm-writing/assets/cumcm-template/` (or unzip a template archive into that folder), then re-invoke."

Stage 3 cannot proceed without the template.

## Where to get the template

- 高教社官方网站: https://cumcm.cnki.com.cn/ (most reliable).
- 数学中国 / 校内组委会通知 (each year, before the contest).
- Many GitHub mirrors exist; pick one that explicitly says "官方 / official."

## Drop the template here

Once you have the year's official template:

```bash
unzip /path/to/cumcm-template.zip -d auto-mm-writing/assets/cumcm-template/
```

The writing stage's contest profile (`auto-mm/references/contest-types.md`) configures it to copy `assets/cumcm-template/` into `runs/<slug>/stage3_writing/paper/` on Stage 3 entry.

## Expected structure

A typical CUMCM template package contains:

- `main.tex` (or `论文模板.tex`) — entry point.
- A `.sty` file or a `\documentclass` declaration that handles 中文字体 (CJK / xeCJK).
- Section files for: 摘要, 问题重述, 问题分析, 模型假设, 符号说明, 模型建立与求解, 模型检验, 模型评价, 参考文献, 附录.
- A title page template.

If the year's template differs from the above structure, edit `auto-mm-writing/references/section-checklist.md` to match.

## Encoding notes

- Use **xelatex** with UTF-8 encoding. Don't use pdflatex with CJK packages — it's fragile.
- 中文字体: 宋体 for 正文 + Times New Roman for English/numbers, or Source Han Serif if Adobe stack is available.
- 1.5 倍行距 typical.
- 公式编号靠右 (right-aligned).

## What the writing stage does with this

When `run.yaml.contest.family == "cumcm"`:

1. Copy the contents of this directory into `runs/<slug>/stage3_writing/paper/`.
2. Symlink `stage2_solving/figures/` into the paper's image directory (typically `paper/figures/` or `paper/img/`).
3. Walk through the section files and fill them from `stage1_modeling/` + `stage2_solving/`.
4. Build with `xelatex` twice.
5. Run anonymity scan against `auto-mm/references/contest-types.md` § "Anonymity scan terms" for CUMCM (中文 forbidden patterns).

If this directory is empty (no template dropped in), the writing stage escalates and asks the user to drop it in.

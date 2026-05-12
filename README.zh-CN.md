# auto-mm — 数学建模比赛自动化 Skill 套件

一组用于 Claude Code 的 skill，用一个提示词把数学建模比赛从「拿到题面」推进到「打包好的 `submit.zip`」，全程 72-96 小时不掉线。内置两套 contest profile：**MCM/ICM（美赛）** 自带 EasyMCM2 LaTeX 占位 scaffold；**CUMCM（国赛）** 支持但需要自带模板 —— 高教社模板年年变、license 不统一，用户首次启动时把当年官方模板丢到 `auto-mm-writing/assets/cumcm-template/` 即可。华中杯 / 妈杯 / 数维杯 / 校赛等衍生赛事按"就近继承"处理。

## 这是什么

不是一个跑得起来的应用，而是 **五个可移植的 skill 包**：把它们拷到 `~/.claude/skills/`（或 `<project>/.claude/skills/`），Claude Code 就会按比赛节奏自动跑。

```
auto-mm                ← 总调度（Stage 0..3 串接，状态契约，完整性门禁，恢复协议）
  ├─ auto-mm-triage      ← Stage 0: 看 A/B/C/D 题面 + 数据侦察 + 五轴打分 → 选题
  ├─ auto-mm-modeling    ← Stage 1: 假设 + 符号表 + 候选模型 + 形式化模型 + 真citation
  ├─ auto-mm-solving     ← Stage 2: 写代码、跑基线/主结果/小算例精确解/消融/灵敏度 + 出图
  └─ auto-mm-writing     ← Stage 3: 拼 LaTeX，迭代摘要 3 轮，匿名性扫描，submit.zip
```

## 为什么需要它

数模比赛和 Kaggle、科研都不一样：

| 维度 | Kaggle | 科研 | 数学建模 |
|---|---|---|---|
| 时长 | 数周-数月 | 数周-数月 | **72-96 小时硬卡** |
| 中间反馈 | 公榜 + 每日 quota | 无 | **完全无**（赛后专家评审） |
| 产出 | submission.csv | 论文 | **论文（带规定模板）+ 支撑材料** |
| 题目 | 1 个固定 | 1 个自选 | A/B/C/D **多选一**，**开放式现实问题** |

钟表是唯一的对手，论文是唯一的产出。这套 skill 就是把这两个事实硬性贯穿到每个阶段。

## 触发方式

把 `auto-MM/` 拷到 `~/.claude/skills/auto-mm/` 等位置后，在 Claude Code 中说：

- `刷数模` / `auto mm` / `auto-mm`
- `开始数模比赛`
- `继续刷 mcm-2026-C` / `resume <run_slug>`
- `status of my <run_slug>` — 只读状态，不会触发任何新动作

首次启动时会问你：

1. 哪个比赛？(MCM | CUMCM | 其他)
2. 年份、题目集合、截止时间（本地时区，自动转 UTC）
3. 控制号 / 报名号
4. 题面 PDF 在哪
5. supervisor 模式（manual / claude-loop / shell-supervisor）

然后写 `runs/<run_slug>/run.yaml`，开始 Stage 0。

## 高层流程

```
                  ┌──────────────────────────────────────────────────────────┐
                  │           auto-mm  (本 skill — 总调度)                    │
                  └──────────────────────────────────────────────────────────┘
                                       │
        首次? ──yes──►  问比赛 (MCM | CUMCM | other)
                       │   问 deadline、题目集合、控制号、语言、supervisor
                       │   写 run.yaml。mkdir runs/<slug>/
                       ▼
                  Stage 0 (auto-mm-triage)
                     题面索引、数据侦察、五轴打分 A/B/C/D，等用户拍板
                       │
                       ▼
                  Stage 1 (auto-mm-modeling)
                     问题分解、假设、符号、候选模型、形式化 model.md
                       │
                       ▼
                  Stage 2 (auto-mm-solving)
                     pipeline.py、基线、主跑、小算例精确解 Gap、消融、灵敏度、出图
                       │
                       ▼
                  Stage 3 (auto-mm-writing)
                     拼模板、写章节、3 轮摘要、xelatex × 2、匿名性扫描、submit.zip
                       │
                       └──► 交付 submit.zip + main.pdf，由用户人工提交到比赛门户
```

## 10 条不可让步的完整性规则

定义在 `auto-mm/references/integrity-rules.md`，在每个 hand-off 强制执行：

1. **题面口径优先** — 题面说 30 个客户，主模型就是 30 个；10 km 半径只能做敏感性。
2. **匿名性绝对** — PDF 元数据、正文、源码列表里出现任何作者/学校/`/Users/<name>` 都是 0 容忍。
3. **真 citation only** — 每条 `references.bib` 都要 DOI / arXiv ID / 稳定 URL 实时核验。
4. **AI/ML 模块必须服务真实不确定性** — 不允许用 NN 替代闭式可计算的目标函数。
5. **算法要被问题结构证明合理** — 不允许 SA+TS+GA+DRL 全堆，每个组件要回答它解决哪个问题特征。
6. **验证是交付的一部分** — 基线 + 小算例精确解 Gap + 消融 + 灵敏度，至少占三项。
7. **时间预算是硬约束** — 阶段超 20% 触发用户决策（砍 scope / 借时间 / 加总预算）。
8. **图是证据不是装饰** — 每张图都要被正文 `\ref`，AI 风格调色盘被禁。
9. **摘要必须带硬数字** — 至少 5 个可数验的数字，禁止「we built a model and obtained good results」。
10. **提交包卫生** — `._*` / `.DS_Store` / `~$*` / `__pycache__/` 一律不进 zip。

## 状态契约 — 所有阶段共享的硬接口

完整 schema 在 `auto-mm/references/state-contract.md`。骨架：

```
runs/<run_slug>/
├── run.yaml                       # contest 元信息 + 时间预算 + 选定题号
├── .heartbeat                     # JSON: {stage, substep, ts_utc, pid}
├── progress.jsonl                 # append-only 微步骤日志
├── STOP | PAUSE                   # 哨兵文件
├── inputs/
│   ├── problems/                  # A.pdf B.pdf ...
│   ├── data/                      # 附件数据
│   └── notices/                   # 组委会勘误
├── stage0_triage/
├── stage1_modeling/
├── stage2_solving/
└── stage3_writing/
```

每个 `stage{N}_*/hand_off.md` 用三段固定结构：
1. **What I did** — 我写了哪些产物（含路径）。
2. **What's true now** — 下一阶段应当依赖的事实（最佳分数、剩余小时、阻塞项）。
3. **What you should do next** — 给下一阶段的指令。

下一阶段**只读** `hand_off.md` + 它点名的结构化文件。

## 长运行协议 — 跨崩溃、跨 context reset 续跑

`auto-mm/references/long-running-protocol.md`：

- 一切状态写盘，零跨调用记忆。
- 每个微步骤幂等：重新跑会读盘、跳过已完成的、继续未完成的。
- 日志只追加（progress.jsonl），永不重写。
- 文件写入用 `.tmp + rename` 保证原子性。
- 默认行为是 resume；只有显式 `--restart` 才会清状态。
- `STOP` / `PAUSE` 文件在每个微步骤开头检查。
- `assets/supervisor.sh` 在 Claude Code 之外保持长跑。
- **锁定模式**（最后 6h）：禁新建模、禁新实验，只允许写论文、编译、匿名检查、打包。

## 从过往比赛沉淀的踩坑

作者过往一次 华中杯 A 题复盘（私有文档，不入仓库）已经被拆解成可执行的 reference：

- `auto-mm-modeling/references/pitfalls-from-experience.md` — 14 条具名踩坑 P1-P14。
- `auto-mm-solving/references/figure-quality.md` — 图表设计原则（无图内标题、PDF 矢量、克制配色）。
- `auto-mm-solving/references/sensitivity-analysis.md` — 灵敏度要回答洞察，不是凑图。
- `auto-mm-writing/references/abstract-writing.md` — 摘要三轮迭代 + 硬数字下限。
- `auto-mm-writing/references/submission-package.md` — macOS 元数据过滤 + 支撑材料目录结构。

下次再有新教训，按相同方式蒸馏回这些 reference，不要堆复盘文件。

## 文件结构

```
auto-MM/
├── README.md  README.en.md  README.zh-CN.md
├── CLAUDE.md  .gitignore
├── auto-mm/                       # 总调度
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/supervisor.sh
│   └── references/
│       ├── state-contract.md
│       ├── integrity-rules.md
│       ├── time-budget.md
│       ├── long-running-protocol.md
│       ├── escalation-policy.md
│       └── contest-types.md
├── auto-mm-triage/                # Stage 0
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── problem-selection-rubric.md
│       ├── data-recon-checklist.md
│       └── contest-typology.md
├── auto-mm-modeling/              # Stage 1
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── model-zoo.md
│       ├── notation-style.md
│       ├── assumption-writing.md
│       ├── pitfalls-from-experience.md
│       └── citation-discipline.md
├── auto-mm-solving/               # Stage 2
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/figure_style.py
│   └── references/
│       ├── algorithm-selection.md
│       ├── figure-workflow.md
│       ├── figure-brief-template.md
│       ├── figure-prompt-patterns.md
│       ├── figure-quality.md
│       ├── sensitivity-analysis.md
│       └── validation-protocol.md
└── auto-mm-writing/               # Stage 3
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/
    │   ├── mcm-template/          # EasyMCM2 占位 scaffold（DWTS 示例已清空）
    │   ├── cumcm-template/        # 占位：用户首次启动时丢入年度模板
    │   ├── anonymity_scan.py      # PDF + .tex/.bib 匿名扫描器
    │   └── build.sh               # xelatex 两遍编译 + 结构化日志
    └── references/
        ├── abstract-writing.md
        ├── section-checklist.md
        ├── anonymity-check.md
        ├── latex-build.md
        ├── submission-package.md
        └── ai-report-mcm.md
```

## 如何贡献

这个 repo 的内容是 **prompts + 工作流契约 + 一个 LaTeX 模板**，不是可执行程序。修改的时候：

- 编辑 `SKILL.md` 后，记得同步 `agents/openai.yaml` 的 `description`。
- 修改 `references/state-contract.md` 时，跨 5 个 skill 看引用，保持契约一致。
- 改了一种语言的 README，记得同步另一种。
- 测试方式：把 skill 拷到 `~/.claude/skills/`，开 Claude Code，按触发短语调用，跑一遍真实流程。

## 许可

未定。EasyMCM2 模板的 license 跟随其原作者。

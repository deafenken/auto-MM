# Abstract writing — three passes, hard numbers, no filler

The abstract is the single page that determines whether the rest of the paper gets a careful read. For MCM, it's also the Summary Sheet — a separate scored artifact. For CUMCM, the 摘要 占满一页 is a formal requirement.

## Required structure

1. **Opening sentence** — problem type + the overall approach. One sentence.
2. **Per-sub-question paragraph** — for each Q1..Qk in `stage1_modeling/problem_decomposition.md`, one short paragraph with:
   - The modeling approach.
   - The algorithm.
   - **Concrete results** (numbers, percentages, comparisons).
3. **Insight / management implication paragraph** — what this means in the real world. One paragraph.
4. **Keywords line** — 4-6 terms.

## Hard-number floor

A passing abstract contains **at least 5 hard numbers**. Examples of what counts:

- Headline metric value: "total cost 184,320 元", "CV consistency 0.91".
- Comparisons: "15.2% improvement over baseline", "1.58% optimality gap".
- Thresholds: "regime change at $p_c^* \approx 110$ 元/kg CO₂".
- Counts: "62 customers, 7 heterogeneous vehicle types, 5-fold CV".
- Sensitivity claims: "robust to ±20% misspecification of α".

The orchestrator's gate greps for digits in the abstract; <5 unique numbers blocks ship.

## Banned phrases

These signal lazy writing and judges learn to discount the abstract that contains them:

- "We built a model and obtained good results."
- "Our approach is novel/innovative/state-of-the-art."
- "Future work includes..."  (irrelevant in an abstract).
- "It is worth noting that..."  (just say the thing).
- "In this paper..."  (it's an abstract; the reader knows it's the paper).

## Three-pass protocol

### Pass 1 — structural

Get the paragraphs in place. Use placeholders for numbers like `<HEADLINE_COST>` and `<GAP_PCT>`. The point is to land the structure first.

```markdown
# Pass 1
We address [problem type] for the [domain] by [overall approach].

For Task 1, we [model] using [algorithm], yielding [<METRIC>] with [comparison vs baseline].

For Task 2, we [model] ... [<METRIC>] ...
```

### Pass 2 — replace placeholders with verified numbers

Open `stage2_solving/validation.md` and `sensitivity.md`. For every placeholder:

- Replace with the exact number.
- Quote the unit.
- Add the comparison context (e.g. not "184,320 元" but "184,320 元, a 15.2% reduction from the baseline").

Cross-check: every number in the abstract must trace to `validation.md` or `sensitivity.md`. The orchestrator runs:

```bash
# Numbers covered: integers, comma-thousands (184,320), decimals (0.91), percentages (15.2%, 91%).
NUM_RE='[0-9]+(,[0-9]{3})*(\.[0-9]+)?%?'

grep -oE "$NUM_RE" abstract_pass2.md            | sort -u > /tmp/abstract_nums
grep -hoE "$NUM_RE" stage2_solving/validation.md stage2_solving/sensitivity.md \
                                                | sort -u > /tmp/result_nums

# Numbers in the abstract that aren't in any results file = candidates for hallucination
comm -23 /tmp/abstract_nums /tmp/result_nums
```

Numbers like Task labels ("Task 1") and years ("2026") appear in both files and are not flagged. Anything in the abstract but not in the results = hallucinated. Fix.

Floor check: the abstract must contain **≥5 unique numeric tokens** (Rule 9). `wc -l /tmp/abstract_nums` must report ≥5; <5 blocks the integrity gate.

### Pass 3 — length and tone

Compile and check that it fits on one page. If over:

- Shorten the longest sub-question paragraph first (it's usually padded with method description).
- Cut filler words ("approach to", "in order to" → "to", "perform an analysis" → "analyze").
- Don't cut the numbers; they earn their space.

Sample one-page abstract target: ~350-450 English words, or ~600-800 中文字.

## Worked example (English / MCM)

```markdown
We develop a four-stage analytical framework for Dancing with the Stars that
(i) infers latent fan votes via constrained inverse optimization with 91%
elimination consistency, (ii) compares rank-based vs percentage-based
aggregation across 27 seasons, (iii) interprets feature contributions
through multi-head attention, and (iv) proposes a phased hybrid voting
policy.

For Task 1, we formulate the latent-vote recovery as a constrained QP with
elimination-consistency constraints, achieving cross-week stability index
0.87 and recovering total fan votes within ±5% of observed totals. ...

[3 more sub-question paragraphs]

Our analysis suggests the percentage rule better aligns with audience
preference across early-to-mid weeks, but late-season emotional voting
introduces a 12-percentage-point widening between rule outcomes. We
recommend a hybrid: percentage in weeks 1-6, judge-selected bottom-three
elimination from week 7 in a 14-week season.

Keywords: Inverse Optimization; Multi-head Attention; Rule Comparison; Hybrid Policy.
```

Notice: every paragraph carries at least one number; the final paragraph offers a concrete decision rule.

## Worked example (中文 / CUMCM)

```markdown
针对绿色配送区时变路网下的车辆调度问题，我们建立"混合整数线性规划 +
自适应大邻域搜索 (ALNS)"的两层求解框架，并辅以小算例精确解验证。

问题一聚焦于异构车队的成本最优路径规划。我们以 62 个客户、7 类车型
为输入，构造目标函数包含固定成本、行驶成本、碳成本与时间窗惩罚四项。
ALNS 主算法在 412 秒内得到总成本 184320 元的方案，相比贪心 + 2-opt
基线降低 15.2%。在 12 客户子算例上与 Gurobi 精确解对比，最优性间隙
为 1.58%。

...

我们建议：在限行政策长期化的情形下，将电动车在绿色区任务中的承担比例
锁定在 35%-45% 区间；超过 110 元/kg CO₂ 的碳价情境下应当主动重启车队
结构调整。

关键词：异构车队 VRP；自适应大邻域搜索；时变路网；灵敏度分析；混合政策建议。
```

## Things to verify before declaring the abstract done

- [ ] Every number traces to `validation.md` or `sensitivity.md`.
- [ ] At least one comparison (vs baseline / vs alternative method) per sub-question.
- [ ] No banned phrases.
- [ ] One-page when compiled.
- [ ] Keywords line present and ≤ 6 terms.
- [ ] No author/school information.
- [ ] No "future work" sentences.
- [ ] Active voice throughout (with rare passive exceptions for stylistic effect).

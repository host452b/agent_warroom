# aw Strategy Evaluation Plan

> 目的：在把 `dual` strategy 放进 `aw` 默认工作流前，先验证它是否真的比更便宜的 `quick` / `reviewed` strategy 更好。`aw` 的主流程是 Superpowers-first；本评估只决定 multi-agent strategy 的启用范围。

---

## 1. 核心问题

Dual strategy 的每个决策都合理，但还没有实证：

- Claude + Codex 独立思考是否优于单 Agent？
- 第三方合并是否提升质量，还是会折中稀释好答案？
- 交叉 review 是否真的降低盲点，还是只是增加挑刺噪声？
- 3 轮迭代的边际收益是否值得成本？
- 完整 dual strategy `S` 的质量提升能否抵消 5-10 倍 token / 时间成本？

**评估目标不是证明 `S` 更好，而是决定 `aw` 的 strategy router 什么时候该用它。**

---

## 2. “好”的定义

不同优化目标会得到不同结论，评估必须同时报告质量和成本。

| 维度 | 怎么测 | 预期倾向 |
|------|--------|----------|
| 最终代码正确性 | hidden tests 通过率 | 不确定 |
| 边界条件覆盖 | edge case tests 通过率 | dual 可能更强 |
| 一次过率 | 后续 rework 次数 | dual 可能更强 |
| 单位 token 质量 | 质量分 / 总 token | single 可能更强 |
| 响应延迟 | wall clock time | single 更强 |
| 创意广度 | 方案多样性 rubric | dual 可能更强 |
| 跨 run 稳定性 | 多次运行结果方差 | dual 可能更强 |

**必须同时输出：**

- raw quality score
- total calls
- total token estimate
- wall clock time
- quality per 1k token
- quality per minute
- run-to-run variance

---

## 3. 对照组

不能只比较 `S` 和单次调用。否则无法区分“系统设计有效”和“只是花了更多算力”。

| ID | 系统 | 目的 |
|----|------|------|
| B0 | Single Claude 一次成稿 | 最朴素 baseline |
| B1 | Single Claude + 自我 review 迭代 3 轮 | 控制算力，隔离双模型变量 |
| B2 | Single Codex + 自我迭代 3 轮 | 控制算力，观察 Codex 单模型上限 |
| B3 | Claude -> Codex 顺序接力，无独立思考 | 隔离“独立思考”变量 |
| B4 | Dual 但只跑 1 round | 隔离“多轮迭代”变量 |
| B5 | Dual 独立思考 + 合并 + 各自审自己 | 隔离“跨 Agent review”变量 |
| S | 完整 dual strategy：独立思考 + 第三方合并 + 交叉 review + 最多 3 轮 | 待验证策略 |

**最关键对比：`B5 vs S`**

如果 `S` 对 `B5` 没有显著优势，说明“不同模型交叉 review”这个核心假设不成立，`dual` 不应作为默认 strategy。

---

## 4. MVP Eval 范围

前期先做最小可行评估，不上完整 20 题。

```text
任务数: 5 个
系统数: B0, B1, B5, S
每组重复: 3 次
总 run 数: 5 × 4 × 3 = 60 次
评测: 自动指标 + LLM-as-judge 盲审
目标时间: 周末两天内完成
```

MVP 只验证四个 strategy candidates：

- `B0`：最低成本 baseline，对应未来 `quick`
- `B1`：控制算力后的单 Claude baseline，对应未来 `reviewed`
- `B5`：去掉交叉 review 的 dual baseline
- `S`：完整 `dual`

---

## 5. 任务集模板

完整评估建议 10-20 个任务。MVP 先选 5 个混合难度任务。

| 类型 | MVP 数量 | 完整数量 | 评判方式 |
|------|----------|----------|----------|
| 简单 CRUD | 1 | 4 | hidden tests |
| 算法 | 1 | 4 | testcase |
| 调试 | 1 | 4 | 修复后跑测试 |
| 重构 | 1 | 3 | rubric + tests |
| 模糊需求 | 1 | 3 | blind review |
| 系统设计 | 0-1 | 3 | LLM-as-judge + rubric |

### 示例任务 1：简单 CRUD

```markdown
# Task: Todo CLI

Build a small Python todo CLI with:

- add item
- list items
- mark item done
- delete item
- persist data in `todos.json`

Acceptance:

- CLI commands are deterministic.
- Data survives process restart.
- Invalid ids return clear errors.
- Hidden tests will exercise empty list, invalid id, repeated delete, and corrupted JSON.
```

### 示例任务 2：算法

```markdown
# Task: Top K Frequent With Stable Tie Break

Implement `top_k_frequent(items: list[str], k: int) -> list[str]`.

Rules:

- Sort by frequency descending.
- Ties are broken by first appearance in the input.
- If `k <= 0`, return `[]`.
- If `k` exceeds unique count, return all unique items.
```

### 示例任务 3：调试

```markdown
# Task: Fix Rate Limiter

You are given a buggy token bucket rate limiter.

Expected behavior:

- `allow()` returns true while tokens are available.
- Tokens refill over time.
- Burst capacity is capped.
- Time going backwards must not create tokens.

Fix the implementation without changing public method names.
```

### 示例任务 4：重构

```markdown
# Task: Refactor Report Generator

You are given a 300-line function that parses sales rows, aggregates totals, formats Markdown, and writes a file.

Refactor it so that:

- Parsing, aggregation, formatting, and writing are separated.
- Existing behavior remains unchanged.
- New units are testable.
- Public CLI behavior is preserved.
```

### 示例任务 5：模糊需求

```markdown
# Task: Lightweight Personal Finance Tool

Build a small local-first tool to track income and expenses.

User cares about:

- quick entry
- monthly summary
- category breakdown
- simple export

Make reasonable product choices and explain tradeoffs.
```

---

## 6. Baseline 行为定义

### B0：Single Claude 一次成稿

```python
def run_b0(task):
    return call_agent("claude", "b0_claude", build_single_prompt(task))
```

### B1：Single Claude 自我迭代 3 轮

```python
def run_b1(task):
    answer = call_agent("claude", "b1_writer", build_single_prompt(task))
    for round_n in range(1, 4):
        critique = call_agent("claude", "b1_reviewer", review_prompt(answer))
        if "VERDICT: PASS" in critique:
            return answer
        answer = call_agent("claude", "b1_writer", revise_prompt(task, answer, critique))
    return answer
```

### B5：Dual + 合并 + 自审

```python
def run_b5(task):
    history = []
    for round_n in range(1, 4):
        claude = call_agent("claude", "b5_claude_thinker", build_prompt(task, history))
        codex = call_agent("codex", "b5_codex_thinker", build_prompt(task, history))
        merged = call_agent("claude", "b5_synthesizer", merge_prompt(claude, codex))

        claude_crit = call_agent("claude", "b5_claude_self_review", review_prompt(merged))
        codex_crit = call_agent("codex", "b5_codex_self_review", review_prompt(merged))
        if has_consensus(claude_crit, codex_crit):
            return merged

        history.append((merged, claude_crit, codex_crit))
    return merged
```

### S：完整系统

```python
def run_s(task):
    return deliberate(stage="eval_task", input_artifact=task, workdir=current_run_dir)
```

---

## 7. 自动评测

自动评测优先级高于 LLM judge。

| 任务类型 | 自动指标 |
|----------|----------|
| CRUD / CLI | hidden pytest pass rate, exit code, persisted file correctness |
| 算法 | testcase pass rate, edge case pass rate |
| 调试 | original failing tests pass, regression tests pass |
| 重构 | behavior tests pass, complexity delta, public API compatibility |
| 模糊需求 | build/run smoke test, artifact completeness |
| 系统设计 | schema completeness checks, required section checks |

### 结果记录 Schema

```json
{
  "task_id": "todo-cli",
  "system": "S",
  "repeat": 2,
  "status": "completed",
  "auto": {
    "tests_passed": 18,
    "tests_total": 20,
    "build_ok": true,
    "lint_ok": true
  },
  "judge": {
    "correctness": 4,
    "completeness": 5,
    "maintainability": 4,
    "edge_cases": 5,
    "overall": 4.5
  },
  "cost": {
    "calls": 9,
    "tokens_in": 12000,
    "tokens_out": 4800,
    "wall_seconds": 410
  }
}
```

---

## 8. LLM-as-Judge 盲审

裁判必须看不到系统 ID。优先使用第三方模型；如果没有，用全新 Claude session，并且隐藏来源。

### Pairwise Judge Prompt

```text
You are evaluating two anonymous solutions to the same software task.

Do not infer which system produced either solution.
Evaluate only the provided artifacts.

Task:
{task}

Solution A:
{solution_a}

Solution B:
{solution_b}

Rubric:
- Correctness: Does it satisfy explicit requirements?
- Completeness: Does it cover important missing details?
- Maintainability: Is it easy to understand, test, and modify?
- Edge cases: Does it handle boundary conditions?
- Practicality: Would a developer accept this output with minimal rework?

Output strict JSON:
{
  "winner": "A" | "B" | "tie",
  "scores": {
    "A": {
      "correctness": 1-5,
      "completeness": 1-5,
      "maintainability": 1-5,
      "edge_cases": 1-5,
      "practicality": 1-5
    },
    "B": {
      "correctness": 1-5,
      "completeness": 1-5,
      "maintainability": 1-5,
      "edge_cases": 1-5,
      "practicality": 1-5
    }
  },
  "reasoning": [
    "short reason 1",
    "short reason 2"
  ]
}
```

### Judge 防偏规则

- 每个 pair 随机交换 A/B 顺序。
- 同一个任务至少做 3 次 pairwise comparison。
- 裁判 prompt 不出现 `Claude`、`Codex`、`dual`、`single`、`S`、`B5` 等来源信息。
- 自动评测失败的方案仍进入 judge，但标注 build/test 结果。

---

## 9. 统计分析

### 必做分析

- 配对比较：同一个 task 上比较系统，不跨任务乱平均。
- 多次运行：每个 `(task, system)` 至少 3 次，报告均值和方差。
- 成本归一化：报告 raw quality 和 quality/token。
- 任务分层：简单任务、复杂任务、模糊任务分开看。

### 输出表

| task_id | system | repeat | auto_score | judge_score | calls | tokens | seconds | quality_per_1k_token |
|---------|--------|--------|------------|-------------|-------|--------|---------|----------------------|
| todo-cli | B0 | 1 | 0.85 | 3.8 | 1 | 3500 | 45 | 1.09 |
| todo-cli | S | 1 | 0.95 | 4.2 | 9 | 28000 | 420 | 0.15 |

### 图表

- cost-quality scatter：x = token / time，y = quality。
- grouped bar：按任务类型展示各系统平均质量。
- variance plot：展示同系统跨 3 次 run 的稳定性。
- pairwise win matrix：展示 `S` 对 `B0/B1/B5` 的胜率。

---

## 10. 决策门槛

MVP eval 后用这些规则决定下一步。

| 结果 | 决策 |
|------|------|
| `S` 明显优于 `B5`，且复杂任务收益高 | `dual` 可作为复杂任务 strategy |
| `S` 只比 `B5` 小幅更好，但成本高很多 | 降低默认 round，`dual` 仅作为显式选择 |
| `S` 不优于 `B5` | 去掉交叉 review 或重新设计 reviewer |
| `B1` 接近 `S` | `reviewed` 作为默认，`dual` 作为升级路径 |
| `B0` 在简单任务够好 | `quick` 作为简单任务默认 |
| round 2/3 改善很小 | max rounds 降到 2 或自适应停止 |
| 合并器质量下降 | 改为“选择更优方案”而不是强制综合 |

**默认继续条件：**

`S` 在复杂任务上的 judge score 至少高于 `B5` 10%，并且 hidden test pass rate 不低于 `B5`，才值得让 `dual` 进入自动路由。否则 `dual` 只能通过用户显式选择启用。

---

## 11. 前期执行 Checklist

- [ ] 固定 5 个 MVP task。
- [ ] 为每个可自动评测任务写 hidden tests。
- [ ] 实现 `B0`、`B1`、`B5`、`S` 四个 strategy runner。
- [ ] 每个 `(task, system)` 跑 3 次。
- [ ] 记录 calls、tokens、wall clock、artifact path。
- [ ] 跑自动评测。
- [ ] 对每个任务做匿名 pairwise judge。
- [ ] 生成 cost-quality scatter。
- [ ] 生成分层结果表。
- [ ] 做结论：`quick` / `reviewed` / `dual` 的默认路由范围。

---

## 12. 负面发现预案

| 发现 | 调整 |
|------|------|
| 简单任务上 dual 没优势 | 加路由器：简单任务走 B0 |
| iteration 边际收益低 | max rounds 降到 2，或自适应停止 |
| 合并器折中导致质量下降 | 改成“二选一 + 补充缺口” |
| 跨 agent review 假阳性多 | 共识门改宽松，或加权 reviewer |
| dual 方差比 single 大 | 检查 prompt 稳定性和合并规则 |
| `S` 没显著优势 | `dual` 不进默认路由，实现更便宜 baseline |

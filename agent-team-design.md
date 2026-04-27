# aw Superpowers-First Workflow Runner 设计

> `aw` 是一个交互式命令行工具，用 Claude Code CLI + Codex CLI 执行一套可审计、可验证、可恢复的软件开发工作流。它借鉴 `obra/superpowers` 的流程和哲学：先澄清设计，再写可执行计划，再用 TDD 小步实现，最后用证据完成。Multi-agent 不是默认信仰，而是一个可评估、可路由的执行策略。

---

## 1. 项目目标

在 **不调用付费 API**（仅使用 CLI 工具）的前提下，构建一个交互式 agent workflow runner。用户启动 `aw` 后进入持续会话，像使用 Claude Code 或 Codex 一样输入需求、澄清设计、批准 spec、生成计划、执行任务、查看证据、恢复历史 run、打开 dashboard。

**核心转向**

- 旧设计：固定 7 阶段 SDLC pipeline，默认每阶段都用双 Agent 协商。
- 新设计：Superpowers-first workflow，默认以“设计 -> 计划 -> TDD 执行 -> review -> evidence finish”为主线。
- Multi-agent 只作为 execution strategy：在复杂、高风险或 eval 证明有效的场景启用。

**约束条件**

- 仅使用 Claude Code CLI 和 Codex CLI（无 API key）。
- `aw` 主进程是交互式 CLI，不是只跑一次就退出的脚本。
- 文件系统作为 artifact、状态、证据、审计记录的唯一 durable channel。
- 所有完成声明必须有 verification evidence。
- 先跑 `evaluation-plan.md` 的最小评估，再决定 dual strategy 是否进入默认路径。

---

## 2. Superpowers 哲学映射

| Superpowers 原则 | `aw` 中的落地 |
|------------------|---------------|
| 先 brainstorm，不能直接写代码 | 自然语言需求进入 `intake` 后必须经过 clarifying/design gate |
| 设计分段给用户确认 | `aw` 把 design 拆成 architecture / data flow / testing / UX 等 section，逐段 approve |
| 写 design spec | spec 存到 `docs/superpowers/specs/`，并进入 run artifact registry |
| 写具体 implementation plan | plan 存到 `docs/superpowers/plans/`，包含文件、测试、命令、验收 |
| 使用隔离 worktree | implementation 前创建或选择 worktree，记录 baseline verification |
| TDD Red-Green-Refactor | task execution 必须先写 failing test，再最小实现，再验证 |
| Review before finish | 每批任务有 spec compliance review 和 code quality review |
| Evidence over claims | `aw` 只有看到测试/检查/人工 approval 证据后才标记完成 |
| YAGNI / DRY | 默认拒绝未被 spec 或 plan 支撑的扩展 |

## 2.1 Project Rule Skill: Karpathy Philosophy

本 repo 额外定义一个项目级 rule skill：`skills/karpathy-philosophy/SKILL.md`。

它约束所有 `aw` 相关设计和实现：

- **编码前思考**：不要隐藏假设；困惑时停下；存在多种解释时先呈现。
- **简洁优先**：不加未要求功能；不为一次性逻辑创建抽象；避免臃肿架构。
- **精准修改**：每一行修改都必须能追溯到用户请求；不顺手重构相邻代码。
- **目标驱动执行**：先定义可验证成功标准，再循环执行直到满足证据。

这个 rule skill 是 Superpowers 哲学的本项目落地层。Superpowers 提供流程骨架，Karpathy Philosophy 约束单次 agent 行为质量。

---

## 3. CLI 产品形态：aw

### 3.1 主进程

```bash
aw
```

启动后进入 REPL / TUI 风格会话：

```text
aw> build a realtime analytics dashboard
aw> status
aw> approve design
aw> show plan
aw> run next task
aw> open dashboard
aw> finish
aw> resume run-20260427-a8f3c2
```

用户不需要每次构造完整命令，而是在一个持续上下文中和工具协作。

### 3.2 交互式命令

| 命令 | 作用 |
|------|------|
| 自然语言输入 | 创建或继续当前需求 |
| `status` | 查看 run / phase / task / strategy / gate |
| `brainstorm` | 进入需求澄清和方案探索 |
| `approve design` | 批准当前 design section 或完整 spec |
| `write plan` | 从已批准 spec 生成 implementation plan |
| `show spec` | 查看当前 design spec |
| `show plan` | 查看当前 implementation plan |
| `run next task` | 执行计划中的下一项任务 |
| `review` | 运行当前批次 review |
| `evidence` | 查看测试、命令输出、人工 approval 等证据 |
| `finish` | 进入完成分支：merge / PR / keep / discard |
| `runs` | 列出历史 run |
| `resume <run_id>` | 恢复历史 run |
| `abort` | 中止当前 run |
| `open dashboard` | 打开 Web dashboard |
| `help` | 查看可用命令 |
| `exit` | 退出交互式主进程 |

### 3.3 快捷子命令

快捷命令用于自动化和 CI，不是主体验：

```bash
aw run --requirement requirement.md
aw eval --suite mvp
aw status run-20260427-a8f3c2
aw dashboard --runs-dir ./runs --port 8080
aw resume run-20260427-a8f3c2
aw abort run-20260427-a8f3c2
```

---

## 4. 主工作流

`aw` 的默认主线不是“所有阶段都多 Agent”，而是 Superpowers-style workflow。

```text
Intake
  -> Brainstorming
  -> Design Spec
  -> User Approval Gate
  -> Implementation Plan
  -> Worktree Setup
  -> Task Execution (TDD)
  -> Review
  -> Verification Evidence
  -> Finish Decision
```

### 4.1 Phase: Intake

用户输入自然语言需求。`aw` 做三件事：

- 判断是否已有 active run。
- 判断需求是否过大，需要拆成多个 spec。
- 选择初始 execution strategy：`quick`、`reviewed`、`dual` 或 `eval`。

### 4.2 Phase: Brainstorming

目标是把模糊想法变成可批准的设计。

流程：

1. 探查当前 repo / docs / recent commits。
2. 一次只问一个澄清问题。
3. 给出 2-3 个方案和推荐。
4. 按 section 展示设计。
5. 用户逐段确认。

产物：

```text
docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
runs/<run_id>/artifacts/spec.md
runs/<run_id>/decisions.jsonl
```

### 4.3 Phase: Design Approval Gate

没有用户批准，不进入 implementation plan。

Gate 条件：

- spec 无 placeholder。
- spec 内部不矛盾。
- scope 足够小，可以形成一个 implementation plan。
- 用户明确 approve。

### 4.4 Phase: Writing Plan

计划要足够具体，不能只写“实现功能”。

必须包含：

- 文件结构。
- 每个 task 的文件路径。
- 每个 task 的 failing test。
- 运行命令和预期失败/通过结果。
- commit 粒度。
- 验收标准。

产物：

```text
docs/superpowers/plans/YYYY-MM-DD-<feature>.md
runs/<run_id>/artifacts/plan.md
```

### 4.5 Phase: Worktree Setup

进入实现前，`aw` 必须创建或选择隔离 workspace：

- 优先使用 repo-local `.worktrees/` 或 `worktrees/`。
- 如果使用 repo-local worktree，必须确认目录被 `.gitignore` 忽略。
- 自动检测项目 setup 命令。
- 跑 baseline tests，记录结果。

产物：

```text
runs/<run_id>/worktree.json
runs/<run_id>/evidence/baseline-tests.txt
```

### 4.6 Phase: Task Execution

每个 task 采用 TDD：

```text
RED: 写 failing test
VERIFY RED: 确认因为目标行为缺失而失败
GREEN: 写最小实现
VERIFY GREEN: 测试通过
REFACTOR: 清理但不新增行为
COMMIT: 小步提交
```

`aw` 必须记录：

- test command
- expected result
- actual result
- touched files
- commit hash
- reviewer findings

### 4.7 Phase: Review

Review 拆成两层：

1. **Spec compliance review**：实现是否满足 spec / plan。
2. **Code quality review**：是否有 bug、回归、测试缺口、复杂度问题。

critical findings 阻塞 finish；non-critical findings 可以进入 follow-up。

### 4.8 Phase: Finish

只有有证据时才能完成：

- tests passed
- lint/typecheck passed（如果项目有）
- review 无 blocking findings
- working tree 状态清楚

finish options：

- merge
- open PR
- keep branch/worktree
- discard

---

## 5. Execution Strategies

### 5.1 Strategy 不是信仰

`aw` 不默认认为 dual-agent 一定更好。不同任务走不同策略：

| Strategy | 说明 | 默认场景 |
|----------|------|----------|
| `quick` | 单 Agent 一次或少量迭代 | 小改动、低风险文档、简单查询 |
| `reviewed` | 单 Agent + 独立 review | 普通代码改动 |
| `dual` | Claude/Codex 独立思考 + 合并 + 交叉 review | 复杂设计、高风险实现、用户明确要求 |
| `eval` | 同任务跑多个 baseline，对比质量/成本 | 验证策略或重大架构前 |

### 5.2 Dual Strategy

Dual strategy 保留旧设计中有价值的部分，但它是可选 profile。

```text
输入 artifact
  -> Claude independent thinker
  -> Codex independent thinker
  -> Synthesizer
  -> Cross review
  -> Revision loop (max 3)
```

原则：

- thinker 独立，不互看输出。
- synthesizer 不兼任 reviewer。
- review 输出必须结构化 JSON，不能只靠字符串匹配。
- 最多 3 轮，之后记录 dispute。
- 是否默认启用取决于 `evaluation-plan.md` 的结果。

### 5.3 Strategy Router

初始路由规则：

| 条件 | Strategy |
|------|----------|
| 用户只问问题或要求解释 | `quick` |
| 文档轻改、无行为风险 | `quick` |
| 单文件低风险代码改动 | `reviewed` |
| 多模块行为改动 | `reviewed` 或 `dual` |
| 架构设计、失败诊断、高风险重构 | `dual` |
| 验证流程本身是否值得 | `eval` |

路由器必须可被用户覆盖：

```text
aw> use dual for this run
aw> use quick
aw> run eval first
```

---

## 6. 文件协议

### 6.1 Repo-level docs

```text
docs/superpowers/
├── specs/
│   └── YYYY-MM-DD-<topic>-design.md
└── plans/
    └── YYYY-MM-DD-<feature>.md
```

### 6.2 Run-level artifacts

```text
runs/run-{timestamp}/
├── run-manifest.json
├── state.json
├── events.jsonl
├── decisions.jsonl
├── artifacts/
│   ├── requirement.md
│   ├── spec.md
│   ├── plan.md
│   └── final-summary.md
├── tasks/
│   └── task-001/
│       ├── prompt.md
│       ├── red-output.txt
│       ├── green-output.txt
│       ├── touched-files.json
│       └── commit.txt
├── evidence/
│   ├── baseline-tests.txt
│   ├── final-tests.txt
│   └── screenshots/
├── reviews/
│   ├── spec-compliance.json
│   └── code-quality.json
└── metrics.json
```

### 6.3 state.json

```json
{
  "run_id": "run-20260427-a8f3c2",
  "status": "running",
  "phase": "task_execution",
  "strategy": "reviewed",
  "current_gate": "verify_green",
  "current_task": "task-001",
  "worktree": ".worktrees/feature-x",
  "started_at": "2026-04-27T08:00:00Z",
  "updated_at": "2026-04-27T08:12:00Z",
  "artifacts": {
    "spec": "artifacts/spec.md",
    "plan": "artifacts/plan.md"
  },
  "stats": {
    "calls": 8,
    "tokens_in": 12000,
    "tokens_out": 4800,
    "wall_seconds": 720
  }
}
```

### 6.4 events.jsonl

```jsonl
{"ts":"...","event":"phase_started","phase":"brainstorming"}
{"ts":"...","event":"gate_waiting","gate":"design_approval"}
{"ts":"...","event":"gate_approved","gate":"design_approval","by":"user"}
{"ts":"...","event":"task_started","task":"task-001"}
{"ts":"...","event":"test_failed_expected","task":"task-001","phase":"red"}
{"ts":"...","event":"test_passed","task":"task-001","phase":"green"}
{"ts":"...","event":"review_completed","blocking_findings":0}
```

---

## 7. Dashboard

Dashboard 不再只展示 7 个 SDLC stage，而是展示 Superpowers workflow 状态。

顶层布局：

| 区块 | 内容 |
|------|------|
| Header | run id、strategy、status、elapsed |
| Workflow strip | intake / brainstorm / spec / plan / worktree / execute / review / finish |
| Gate panel | 当前等待的 approval、test、review 或 finish decision |
| Task board | plan 中每个 task 的 red / green / refactor / commit 状态 |
| Evidence panel | test output、screenshots、review findings、commit hash |
| Strategy panel | quick / reviewed / dual / eval 的调用与成本 |
| Artifacts panel | requirement、spec、plan、final summary |

现有 `agent-team-dashboard.html` 仍可作为第一版视觉原型；下一版应把 mock state 从 `stages` 改成 `workflow_phases + tasks + gates + evidence`。

---

## 8. Evaluation Gate

`evaluation-plan.md` 是进入完整 dual strategy 前的门禁。

MVP eval：

```text
任务数: 5
系统: B0, B1, B5, S
重复: 每组 3 次
评估: 自动测试 + blind LLM judge + 成本归一化
```

关键判断：

- 如果 `S` 不优于 `B5`，交叉 review 不进入默认路径。
- 如果 `B1` 接近 `S`，默认策略应是 single-agent self-review。
- 如果简单任务 `B0` 够好，`quick` 是默认路径。
- 如果 dual 只在复杂任务上显著更好，则路由器只在复杂任务启用 dual。

---

## 9. 技术栈选型

| 组件 | 选型 | 理由 |
|------|------|------|
| CLI 框架 | Typer / Click | 交互式主进程 + 快捷子命令都容易表达 |
| 交互体验 | prompt-toolkit / Textual（二选一） | 模拟 Claude Code / Codex 的持续会话体验 |
| Agent 适配器 | subprocess + session registry | 只调用 Claude Code CLI / Codex CLI |
| 状态存储 | JSON / JSONL | 可审计、可恢复、易调试 |
| Spec / Plan | Markdown | 可读、可 review、可提交 |
| Schema 校验 | pydantic | state、review、metrics、strategy 输出结构化 |
| Dashboard 后端 | FastAPI | 轻量 HTTP / SSE 服务 |
| Dashboard 前端 | 单页 HTML + markdown-it | 无构建步骤，便于本地打开和嵌入 |

---

## 10. 错误处理与降级

| 故障场景 | 降级策略 |
|----------|----------|
| CLI 进程崩溃 | 记录现场，从 `state.json` + artifact 恢复 |
| Claude session 过期 | 重建 session，注入当前 spec/plan/summary |
| Codex 无 session | 用 role-local history 文件降级 |
| Token 超限 | 生成摘要，缩小 artifact 输入，必要时请求人工裁剪 |
| Failing test 不是预期失败 | 停止 task，要求修正测试 |
| Review blocking findings | 回到对应 task 或 plan 修订 |
| Worktree baseline tests 已失败 | 记录为 pre-existing，询问是否继续 |
| Strategy 成本过高 | 自动建议降级到 `quick` 或 `reviewed` |

---

## 11. 实施路线图

### Phase 0 — Evaluation Harness

- [ ] 固定 `evaluation-plan.md` 的 5 个 MVP task。
- [ ] 实现 `B0/B1/B5/S` runner 骨架。
- [ ] 记录 calls、tokens、wall clock、artifact path。
- [ ] 输出 cost-quality scatter 和分层结果。
- [ ] 决定 dual strategy 是否进入默认路径。

### Phase 1 — File Protocol + Interactive Shell

- [ ] `aw` 交互式主进程。
- [ ] `run-manifest.json` / `state.json` / `events.jsonl` schema。
- [ ] `status` / `runs` / `resume` / `abort`。
- [ ] artifact registry。

### Phase 2 — Brainstorming + Spec + Plan

- [ ] 需求澄清 flow。
- [ ] design section approval gate。
- [ ] 写入 `docs/superpowers/specs/`。
- [ ] 写入 `docs/superpowers/plans/`。

### Phase 3 — Worktree + TDD Task Execution

- [ ] worktree 创建和 ignore 检查。
- [ ] baseline verification。
- [ ] task-level red/green/refactor loop。
- [ ] evidence capture。

### Phase 4 — Review + Finish

- [ ] spec compliance review。
- [ ] code quality review。
- [ ] blocking findings gate。
- [ ] finish options：merge / PR / keep / discard。

### Phase 5 — Strategy Engine

- [ ] `quick` strategy。
- [ ] `reviewed` strategy。
- [ ] `dual` strategy。
- [ ] `eval` strategy。
- [ ] strategy router 和用户 override。

### Phase 6 — Dashboard

- [ ] FastAPI 服务读取 `runs/`。
- [ ] SSE 转发 `events.jsonl`。
- [ ] workflow strip + task board + evidence panel。
- [ ] 历史 run 浏览器。

---

## 12. 关键反模式

| 反模式 | 后果 |
|--------|------|
| 没有 brainstorm 就写代码 | 需求误解，返工变多 |
| 没有 spec approval 就 plan | 计划建立在未确认假设上 |
| plan 只有高层描述 | agent 执行时自由发挥，难验证 |
| 没有 failing test 先写实现 | 无法证明测试覆盖目标行为 |
| 没有证据就宣布完成 | 用户无法信任状态 |
| 默认所有任务都 dual-agent | 成本高，且未证明收益 |
| reviewer 只输出自然语言 | 难以机器 gate，容易漂移 |
| dashboard 只展示漂亮进度 | 无法回答“为什么卡住/凭什么完成” |

---

## 附录 A：Legacy 7-Stage SDLC Profile

旧的 7 阶段 pipeline 可以作为 `dual-sdlc` profile 保留，但不作为默认架构：

```text
Brainstorm -> Plan -> Specs -> Implement -> Review <-> Test -> Retrospective
```

适用场景：

- 用户明确要求完整 SDLC 推演。
- 高风险项目需要更多设计和 review。
- evaluation 证明 dual strategy 在该任务类型上显著优于 cheaper baselines。

每个 stage 可以复用 dual strategy：

```text
Claude thinker + Codex thinker -> Synthesizer -> Cross review -> max 3 rounds
```

---

## 附录 B：未来扩展

- **人工 in-the-loop**：每个 gate 都可要求人工批准。
- **学习与适配**：将 eval 结果转成 strategy router 的规则。
- **Replay 模式**：按 `events.jsonl` 回放一次 run。
- **Policy packs**：不同 repo 可定义自己的 gates、commands、required checks。

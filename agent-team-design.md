# Multi-Agent CLI Team 框架设计

> 用交互式命令行工具 `aw` 编排 Claude Code CLI + Codex CLI，构建一个 SDLC pipeline。每个环节由双 Agent 独立思考、第三方合并、共同 review，最多 3 轮迭代后进入下一阶段。

---

## 1. 项目目标

在 **不调用付费 API**（仅使用 CLI 工具）的前提下，构建一个覆盖软件开发完整生命周期的 Agent Team，从需求 brainstorm 到回溯检查共 7 个阶段。每阶段通过双 Agent 协商机制提升输出质量、消除单模型偏见。

最终产品形态是一个交互式 CLI，命令缩写为 `aw`。用户启动 `aw` 后进入持续会话，像使用 Claude Code 或 Codex 一样直接输入需求、查看 pipeline 状态、批准/中止阶段、恢复历史 run、打开 dashboard。

**约束条件**

- 仅使用 Claude Code CLI 和 Codex CLI（无 API key）
- `aw` 主进程是交互式 CLI，而不是只跑一次就退出的脚本
- 利用 CLI 自带的 session / history 机制管理上下文
- 文件系统作为阶段间 artifact 通道
- 控制总调用次数，适配 CLI 的免费额度

---

## 2. 核心设计原则

### 2.1 双 Agent 独立思考

任何决策前，Claude 和 Codex 必须**独立**思考（互相不可见）。这是为了避免：

- 单模型的 echo chamber
- Anchor bias（先发言者锁死后发言者）
- 系统性盲点（同模型对自己的弱点也盲）

### 2.2 第三方合并

合并器（Synthesizer）是**独立的** Claude session，与 thinker 和 reviewer 角色完全隔离。避免裁判兼运动员。

### 2.3 保守共识

review 通过 = 双方都明确说 PASS。任一方说 NEEDS_REVISION 就回炉。

> 反模式："两边都不太确定但互相点头"。

### 2.4 有界迭代

每个 stage 内部最多 3 轮 deliberation。第 3 轮后强制采纳最新版本并记录分歧。不让 agents 陷入无限来回。

### 2.5 Artifact 文件化

阶段间产物全部以文件形式传递，**绝不**塞 prompt。下游 agent 自己 `cat` 读取。好处：

- 每次调用 prompt 干净
- 可断点续跑
- 人工随时介入修改
- 完整审计轨迹

---

## 3. CLI 产品形态：aw

### 3.1 主进程

`aw` 的核心入口是交互式主进程：

```bash
aw
```

启动后进入一个常驻 REPL / TUI 风格会话：

```text
aw> build a realtime analytics dashboard
aw> status
aw> open dashboard
aw> approve current stage
aw> abort
aw> resume run-20260427-a8f3c2
```

这和 Claude Code / Codex 的使用方式一致：用户不需要每次都构造完整命令，而是在一个持续上下文中和工具协作。

### 3.2 交互式命令

| 命令 | 作用 |
|------|------|
| 自然语言输入 | 创建或继续一个需求任务 |
| `status` | 查看当前 run / stage / round / role |
| `runs` | 列出历史 run |
| `resume <run_id>` | 恢复历史 run |
| `abort` | 中止当前 run |
| `approve` | 人工批准当前 stage |
| `open dashboard` | 打开 Web dashboard |
| `artifacts` | 列出当前 run 的产物 |
| `show <artifact>` | 查看某个产物 |
| `help` | 查看可用命令 |
| `exit` | 退出交互式主进程 |

### 3.3 快捷子命令

这些命令可以作为自动化入口，但不是主产品体验：

```bash
aw run --requirement requirement.md
aw status run-20260427-a8f3c2
aw dashboard --runs-dir ./runs --port 8080
aw resume run-20260427-a8f3c2
aw abort run-20260427-a8f3c2
```

---

## 4. 整体架构

### 4.1 7 阶段 Pipeline（外层）

```text
Brainstorm -> Plan -> Specs -> Implement -> Review <-> Test -> Retrospective
                                           ↓        ↓         ↓
                                           └────────┴─────-> Implement
                                                            (反馈环)
```

| # | 阶段 | 输入 | 产物 | 主 Agent |
|---|------|------|------|---------|
| 1 | Brainstorm | `requirement.md` | `ideas.md` | Claude（+ Gemini 可选） |
| 2 | Plan | `ideas.md` | `plan.md` | Claude |
| 3 | Specs | `plan.md` | `specs.md` | Claude |
| 4 | Implement | `specs.md` | `src/*` | Codex 主 / Claude 备 |
| 5 | Review | `src/* + specs.md` | `review.md` | Claude（≠ 实现者） |
| 6 | Test | `src/* + specs.md` | `tests/*` | Codex 写 + Claude 设计 case |
| 7 | Retrospective | 全部 artifacts | `retro.md` | Gemini / Claude 长 context |

**反馈环**

- Review 不通过 -> 回到 Implement
- Test 不通过 -> 回到 Implement
- Retrospective 发现偏差 -> 回到 Plan / Specs / Implement 任一处

### 4.2 单阶段协商单元（内层）

每个阶段内部都执行以下流程：

```text
              上一阶段产物
                   │
            ┌──────┴──────┐
            ▼             ▼
        Claude         Codex
       独立思考        独立思考
            │             │
            └──────┬──────┘
                   ▼
               合并器
            (Synthesizer)
                   ▼
            共同 review
       Claude 批判 + Codex 批判
                   │
              ┌────┴────┐
              ▼         ▼
            通过      不通过
              │         │
          下一阶段   ↻ 重思考 (≤ 3 轮)
```

每个 cell 单轮 = 5 次调用：

- Claude thinker × 1
- Codex thinker × 1
- Synthesizer × 1
- Claude reviewer × 1
- Codex reviewer × 1

每个 cell 上限 = 5 × 3 = **15 次 LLM 调用**

---

## 5. Agent 分工与 Session 矩阵

### 5.1 角色定义

每个阶段 × 每种角色 = 一个独立 session：

| 角色 | Session 名 | CLI | 职责 |
|------|-----------|-----|------|
| Thinker (Claude) | `{stage}_thinker_claude` | claude | 独立产出方案 A |
| Thinker (Codex) | `{stage}_thinker_codex` | codex | 独立产出方案 B |
| Synthesizer | `{stage}_synthesizer` | claude | 合并双方产出 |
| Reviewer (Claude) | `{stage}_reviewer_claude` | claude | 批判合并版本 |
| Reviewer (Codex) | `{stage}_reviewer_codex` | codex | 批判合并版本 |

**总 session 数**：7 stages × 5 roles = **35 个独立 session**

### 5.2 跨 Agent 反偏置规则

**铁律**：实现者 ≠ Reviewer 模型。

- Stage 4 实现是 Codex -> Stage 5 由 Claude 主导 review
- Stage 4 实现是 Claude -> Stage 5 由 Codex 主导 review

模型对自己产出的盲区也盲，必须靠不同模型交叉验证。

---

## 6. 关键机制

### 6.1 Session 管理

```python
SESSIONS: dict[str, str] = {}    # role_key -> session_id (Claude)
HISTORIES: dict[str, list] = {}  # role_key -> message list (Codex)

def call_agent(cli: str, role: str, prompt: str) -> str:
    """统一接口：自动处理 session 续接和降级。"""

    if cli == "claude":
        sid = SESSIONS.get(role)
        cmd = ["claude", "--output-format", "json"]
        cmd += ["--resume", sid] if sid else ["-p", prompt]
        result = json.loads(
            subprocess.run(cmd, capture_output=True, text=True).stdout
        )
        SESSIONS[role] = result["session_id"]
        return result["result"]

    elif cli == "codex":
        history = HISTORIES.setdefault(role, [])
        history.append(f"User: {prompt}")
        full_prompt = "\n".join(history)
        out = subprocess.run(
            ["codex", "--quiet", full_prompt],
            capture_output=True, text=True
        ).stdout.strip()
        history.append(f"Assistant: {out}")
        return out
```

### 6.2 合并器 Prompt 模板

```text
你是独立的合成员，没有参与之前的思考。请综合以下两份独立产出：

---产出 A（来源: Thinker-Claude）---
{claude_output}

---产出 B（来源: Thinker-Codex）---
{codex_output}

要求：
1. 保留双方都覆盖的核心要点
2. 协调冲突，给出综合判断
3. 标注哪些是双方共识、哪些是单方独有
4. 输出统一格式的合并版本

合并产物：
```

### 6.3 共识判定（AND 门）

```python
def has_consensus(claude_critique: str, codex_critique: str) -> bool:
    return (
        "VERDICT: PASS" in claude_critique
        and "VERDICT: PASS" in codex_critique
    )
```

Reviewer prompt 强制结构化输出：

```text
请批判性审查以下方案。输出格式必须严格如下：

VERDICT: PASS | NEEDS_REVISION
REASONS:
- ...
- ...
SUGGESTIONS (仅当 NEEDS_REVISION):
- ...

待审查方案：
{merged}
```

### 6.4 反馈环与迭代上限

```python
MAX_ROUNDS = 3

def deliberate(stage: str, input_artifact: str, workdir: str) -> str:
    history = []

    for round_n in range(1, MAX_ROUNDS + 1):
        prompt = build_prompt(stage, input_artifact, history)

        claude_out = call_agent("claude", f"{stage}_thinker_claude", prompt)
        codex_out  = call_agent("codex",  f"{stage}_thinker_codex",  prompt)

        merged = call_agent("claude", f"{stage}_synthesizer",
                            merge_prompt(claude_out, codex_out))

        claude_crit = call_agent("claude", f"{stage}_reviewer_claude",
                                  review_prompt(merged))
        codex_crit  = call_agent("codex",  f"{stage}_reviewer_codex",
                                  review_prompt(merged))

        save_round(workdir, stage, round_n, claude_out, codex_out,
                   merged, claude_crit, codex_crit)

        if has_consensus(claude_crit, codex_crit):
            return merged

        history.append({
            "round": round_n,
            "merged": merged,
            "claude_crit": claude_crit,
            "codex_crit": codex_crit,
        })

    log_dispute(workdir, stage, history)
    return history[-1]["merged"]
```

**Round 2/3 的 prompt 增强**：把上轮的 merged + 双方 critique 都喂回去，让 thinker 知道为什么被打回，避免重复犯错。

---

## 7. 数据流转

### 7.1 目录结构

```text
./runs/run-{timestamp}/
├── requirement.md
├── 01-brainstorm/
│   ├── round-1/
│   │   ├── claude.md
│   │   ├── codex.md
│   │   ├── merged.md
│   │   └── critiques.json
│   ├── round-2/
│   │   └── ...
│   └── final.md
├── 02-plan/
│   └── ...
...
└── 07-retrospective/
    └── ...
```

### 7.2 上游产物读取

每个 thinker 的 prompt 引用文件路径，让 agent 自己读：

```bash
claude -p "请读取 ./runs/run-20260427/01-brainstorm/final.md，
基于此为本次需求输出 plan。要求：..."
```

### 7.3 状态文件

```text
./runs/run-{timestamp}/state.json     # 当前 stage、round、session 映射
./runs/run-{timestamp}/events.jsonl   # 实时事件流
./runs/run-{timestamp}/dispute.log    # 3 轮无共识的分歧记录
./runs/run-{timestamp}/cost.json      # 每个 stage 的调用次数和 token 估算
```

---

## 8. 技术栈选型

| 组件 | 选型 | 理由 |
|------|------|------|
| CLI 框架 | Typer / Click | 交互式主进程 + 快捷子命令都容易表达 |
| 交互体验 | prompt-toolkit / Textual（二选一） | 模拟 Claude Code / Codex 的持续会话体验 |
| 编排框架 | LangGraph | 状态机 + conditional edges 表达反馈环 |
| 上下文策略 | JSON + session_id（主）/ 手动 history（备） | Claude 用原生 session，Codex 降级 |
| Artifact 通道 | 文件系统 | 简单、可观测、可回放 |
| 状态持久化 | LangGraph checkpoint | 支持断点续跑 |
| Schema 校验 | pydantic | 确保 reviewer 输出符合 VERDICT 结构 |
| Dashboard 后端 | FastAPI | 轻量 HTTP / SSE 服务 |
| Dashboard 前端 | 单页 HTML + markdown-it | 无构建步骤，便于本地打开和嵌入 |

---

## 9. 顶层代码骨架

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict
import pathlib
import uuid

class TeamState(TypedDict):
    workdir: str
    stage_outputs: dict[str, str]
    review_passed: bool
    test_passed: bool
    retro_verdict: str

def make_stage(name: str, prev: str | None):
    def node(state: TeamState) -> TeamState:
        prev_artifact = (
            state["stage_outputs"][prev] if prev
            else read(f"{state['workdir']}/requirement.md")
        )
        out = deliberate(name, prev_artifact, state["workdir"])
        state["stage_outputs"][name] = out
        write(f"{state['workdir']}/{name}/final.md", out)
        return state
    return node

g = StateGraph(TeamState)

g.add_node("brainstorm",     make_stage("brainstorm",     None))
g.add_node("plan",           make_stage("plan",           "brainstorm"))
g.add_node("specs",          make_stage("specs",          "plan"))
g.add_node("implement",      make_stage("implement",      "specs"))
g.add_node("review",         make_stage("review",         "implement"))
g.add_node("test",           make_stage("test",           "implement"))
g.add_node("retrospective",  make_stage("retrospective",  "test"))

g.add_edge("brainstorm", "plan")
g.add_edge("plan", "specs")
g.add_edge("specs", "implement")
g.add_edge("implement", "review")

g.add_conditional_edges("review",
    lambda s: "test" if s["review_passed"] else "implement")
g.add_conditional_edges("test",
    lambda s: "retrospective" if s["test_passed"] else "implement")
g.add_conditional_edges("retrospective", lambda s: {
    "pass":   END,
    "replan": "plan",
    "respec": "specs",
    "reimpl": "implement",
}[s["retro_verdict"]])

g.set_entry_point("brainstorm")
app = g.compile()

workdir = f"./runs/run-{uuid.uuid4().hex[:8]}"
pathlib.Path(workdir).mkdir(parents=True, exist_ok=True)
app.invoke({
    "workdir": workdir,
    "stage_outputs": {},
    "review_passed": False,
    "test_passed": False,
    "retro_verdict": "",
})
```

---

## 10. 错误处理与降级

| 故障场景 | 降级策略 |
|---------|---------|
| Codex CLI 不支持 session | 自动切换到手动 history（适配器透明处理） |
| Claude session 过期 | 重建 session，注入历史摘要重建上下文 |
| 3 轮无共识 | 采纳最新 merged，写 dispute.log，由 retrospective 重点关注 |
| 单次调用超时 | 重试 3 次，失败 escalate 到人工 |
| Token 超限 | 切换到 Gemini（长 context）作为 fallback |
| 反馈环往返 > 5 次 | 强制 break，标记需人工干预 |
| CLI 进程崩溃 | 记录现场，从 LangGraph checkpoint 恢复 |
| `aw` 交互式主进程退出 | 保留当前 run 状态，允许 `aw` 后 `resume <run_id>` |

---

## 11. Web 可视化前端

长流程 + 多 agent + 多轮迭代 = **必须有可视化**，否则跑几十分钟不知道在做什么、卡在哪、为什么卡。

### 11.1 设计目标

| 目标 | 说明 |
|------|------|
| 实时观测 | 每个 stage 的状态、当前 round、当前调用的 agent |
| 决策追踪 | 任意一轮的 Claude/Codex 独立产物、合并版本、双方 critique 都可回看 |
| 干预入口 | 手动 approve / abort / 修改 artifact（Phase 5+） |
| 成本透明 | 累计调用次数、token 消耗、预计剩余时间 |
| 分歧暴露 | 3 轮强制采纳的 dispute 必须高亮，方便 retrospective 重点关注 |

### 11.2 架构概览

```text
┌──────────────────┐         ┌──────────────────┐
│  aw main process │ ──写───► │  ./runs/run-{ts}/│
│  (interactive)   │         │  state.json      │
└──────────────────┘         │  artifacts/*.md  │
                              │  events.jsonl    │
                              └─────────┬────────┘
                                        │ 读
                              ┌─────────▼────────┐
                              │  FastAPI server  │
                              │  :8080           │
                              └─────────┬────────┘
                       HTTP / SSE       │
                              ┌─────────▼────────┐
                              │  Web Dashboard   │
                              │  单页 HTML       │
                              └──────────────────┘
```

**关键决策：解耦写入和读取**

- `aw` 主进程只负责往 `./runs/run-{ts}/` 目录写文件
- 一个轻量 FastAPI 进程读这个目录，对外暴露 HTTP / SSE
- 前端是一个静态 HTML，无构建步骤，CDN 引入 markdown-it 即可

这样的好处：

- Pipeline 崩溃时仪表板还能查看历史
- 仪表板挂掉不影响 pipeline 运行
- 可以离线分析历史 run

### 11.3 后端 API

```text
GET  /api/runs                  # 列出所有历史 run
GET  /api/runs/{run_id}/state   # 当前完整状态 JSON
GET  /api/runs/{run_id}/artifact?path=02-plan/round-1/merged.md
                                # 读取任意 artifact 内容
GET  /api/runs/{run_id}/events  # SSE 流，实时推送状态变更
POST /api/runs/{run_id}/abort   # 终止运行
POST /api/runs/{run_id}/approve # 手动通过当前 stage（绕过共识）
```

**state.json 结构**

```json
{
  "run_id": "run-20260427-a8f3c2",
  "status": "running",
  "started_at": "2026-04-27T08:00:00Z",
  "current_stage": "review",
  "current_round": 2,
  "current_role": "codex_thinker",
  "stages": {
    "brainstorm": {
      "status": "passed",
      "rounds": [
        {
          "round": 1,
          "verdict": "pass",
          "started_at": "...",
          "ended_at": "...",
          "calls": {
            "claude_thinker": { "tokens_in": 800, "tokens_out": 400, "duration_ms": 1200 },
            "codex_thinker":  { "tokens_in": 800, "tokens_out": 380, "duration_ms": 980 },
            "synthesizer":    { "tokens_in": 1200, "tokens_out": 500, "duration_ms": 1500 },
            "claude_review":  { "tokens_in": 600, "tokens_out": 150, "duration_ms": 700 },
            "codex_review":   { "tokens_in": 600, "tokens_out": 130, "duration_ms": 650 }
          }
        }
      ]
    }
  },
  "stats": {
    "total_calls": 23,
    "total_tokens_in": 28000,
    "total_tokens_out": 12000,
    "disputes": 0
  }
}
```

### 11.4 前端 UI 组件

| 区块 | 内容 |
|------|------|
| Header | run_id、状态徽章、运行时长 |
| Pipeline strip | 7 个圆点连接，颜色编码状态（pending / running / pass / fail / dispute） |
| Current activity | 仅运行时显示：当前 stage 内 4 类调用的实时状态 |
| Stage cards | 每个 stage 一张可展开卡片，展开后显示所有 round 的 tab |
| Stats footer | 累计调用数、时长、平均 round 数、dispute 数、token 消耗 |

**Stage card 展开后的内容**：

```text
┌──────────────────┬──────────────────┐
│ Claude 独立产物   │ Codex 独立产物    │
├──────────────────┴──────────────────┤
│  合并版本 (Merged)                  │
├──────────────────┬──────────────────┤
│ Claude review    │ Codex review     │
│ VERDICT: PASS    │ VERDICT: PASS    │
└──────────────────┴──────────────────┘
```

### 11.5 实时更新机制

**SSE 推送（推荐）**

Pipeline 在每次状态变更时，向 `events.jsonl` 追加一行：

```jsonl
{"ts":"...","event":"stage_started","stage":"review","round":1}
{"ts":"...","event":"role_started","stage":"review","role":"claude_thinker"}
{"ts":"...","event":"role_completed","stage":"review","role":"claude_thinker","duration_ms":1200}
{"ts":"...","event":"round_completed","stage":"review","round":1,"verdict":"fail"}
{"ts":"...","event":"stage_completed","stage":"review","verdict":"pass"}
```

FastAPI 用 `tail -f` 风格读取并通过 SSE 转发给前端。前端不需要轮询，连接断开自动重连。

### 11.6 部署方式

**单机本地运行**

```bash
# Terminal 1: 进入交互式 aw
aw

# aw 内部打开 dashboard
aw> open dashboard

# 或使用快捷命令
aw dashboard --port 8080 --runs-dir ./runs
```

**远程访问**

如果要在多人团队共享，把 FastAPI 部署到内网服务器，运行 pipeline 时挂载共享目录。前端不变。

**鉴权**

- 单机：无需
- 内网：靠网络隔离
- 公网：FastAPI 加 BasicAuth 中间件，或前面套 Caddy + OIDC

### 11.7 高级功能（v2+）

| 功能 | 说明 |
|------|------|
| Diff 视图 | 同 stage 跨 round 对比 merged 版本，看每轮改进了什么 |
| Round-2 prompt 透视 | 展开第 2 轮时，显示喂给 thinker 的完整 prompt（含上轮 critique） |
| 成本预警 | 累计 token 接近限额时浮窗提醒 |
| 历史对比 | 跨 run 对比同一需求的不同跑法，A/B test prompt 模板 |
| Dispute 详情面板 | 点击强制采纳的 stage，专用面板展示 3 轮的演变和最终分歧 |
| Replay 模式 | 选历史 run，按时间轴回放每个事件 |
| 人工 in-the-loop | 在任意 stage 后插入"人工 approve"门，dashboard 上点按钮放行 |

---

## 12. 实施路线图

### Phase 0 — Evaluation Gate（Week 0）

- [ ] 按 `evaluation-plan.md` 跑 MVP eval
- [ ] 对比 `B0`、`B1`、`B5`、`S`
- [ ] 重点验证 `B5 vs S`，确认交叉 review 是否真的带来增益
- [ ] 输出 cost-quality scatter、分层结果和继续/降级决策

### Phase 1 — CLI MVP（Week 1）

- [ ] `aw` 交互式主进程
- [ ] CLI 适配器 `call_agent()`（统一 Claude / Codex 接口）
- [ ] 单 stage deliberation cell（先跑通 brainstorm 一个阶段）
- [ ] 文件系统 artifact 流转
- [ ] 基础日志和成本统计

### Phase 2 — 串联（Week 2）

- [ ] LangGraph 串联 7 个 stage（暂不带反馈环）
- [ ] 每个 stage 的 prompt 模板调优
- [ ] dispute.log 系统
- [ ] `aw status` / `runs` / `show <artifact>`

### Phase 3 — 反馈环（Week 3）

- [ ] review / test / retrospective 的 conditional edges
- [ ] 反馈次数限制和 escalation
- [ ] 失败回滚机制
- [ ] `approve` / `abort` / `resume`

### Phase 4 — 生产化（Week 4）

- [ ] 断点续跑（LangGraph checkpoint）
- [ ] 性能优化（并行 thinker 调用）
- [ ] 完整集成测试

### Phase 5 — 可视化与运维（Week 5）

- [ ] FastAPI 服务读取 `./runs/run-{ts}/` 目录
- [ ] state.json + events.jsonl 输出（pipeline 写入）
- [ ] Web 仪表板单页 HTML（pipeline strip + stage cards + stats）
- [ ] SSE 实时推送
- [ ] 历史 run 浏览器

---

## 附录 A：成本估算

**单次完整流程**

```text
7 stages × 5 roles/round × 平均 1.5 rounds = 52.5 次 LLM 调用
```

**按 Claude Pro 限额估算**

- 限额：约 200 messages / 5h
- 单流程消耗：约 50 messages
- 支撑能力：约 4 个完整流程 / 5h，**约 16 个流程 / 天**

**优化方向**

- Stage 1-3（brainstorm/plan/specs）共识率高，平均 1.2 rounds
- Stage 4-6（implement/review/test）共识率低，平均 2 rounds
- Stage 7（retrospective）通常 1 round 即可

---

## 附录 B：关键反模式

| 反模式 | 后果 |
|--------|------|
| 让 thinker 看到对方的产物 | 破坏独立性，退化成接力 |
| 让合并器同时做 reviewer | 自审无效 |
| 让 reviewer 模型 = 实现模型 | 系统性盲区，关键 bug 逃逸 |
| 把 artifact 全部塞 prompt | Token 爆炸、上下文截断 |
| 无限迭代 | 卡死在某 stage，资源耗尽 |
| 不区分阶段角色，复用同一 session | 角色串味、上下文污染 |
| 用同一 LLM 同一 session 同时做 thinker 和 reviewer | 看不到自己的盲点 |

---

## 附录 C：未来扩展

- **多模型扩容**：引入 Gemini（长 context 任务）、本地 Llama（隐私敏感任务）
- **人工 in-the-loop**：每个 stage 通过后可选人工 approve
- **学习与适配**：dispute.log 自动转化为 fine-tuning 数据，迭代 prompt 模板
- **并行多分支**：同一需求同时跑多个 brainstorm 路径，让 retrospective 选最优

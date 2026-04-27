# Agent Team Dashboard and Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** First define two project artifacts for `aw`, a CLI-first Multi-Agent CLI Team tool: a static HTML dashboard prototype and a canonical Markdown design document.

**Architecture:** This phase is documentation-first. The final product shape is an interactive command-line tool named `aw`, similar in interaction style to Claude Code or Codex CLI. The dashboard is a standalone HTML artifact with mock data and no backend dependency; the design document is the source of truth for the SDLC pipeline, agent roles, artifact flow, dashboard architecture, interactive CLI surface, and roadmap.

**Tech Stack:** Markdown, single-file HTML/CSS/JavaScript, `markdown-it` from CDN for rendering mock Markdown content.

---

## Scope

This plan only defines and creates the first two artifacts:

1. `agent-team-dashboard.html` — static dashboard prototype.
2. `agent-team-design.md` — canonical design document.

This plan does not implement the `aw` executable, FastAPI backend, SSE endpoint, runner integration, LangGraph orchestration, or real Claude/Codex CLI execution.

## File Structure

- Create: `agent-team-dashboard.html`
  - Responsibility: Provide a clickable, single-file UI prototype for visualizing one agent-team run.
  - Contains: header, pipeline strip, current activity panel, expandable stage cards, round tabs, review panels, stats footer, mock state switcher.
  - Data source: local JavaScript mock objects for `running`, `completed`, and `dispute` states.

- Create: `agent-team-design.md`
  - Responsibility: Preserve the product and technical design for the Multi-Agent CLI Team framework.
  - Contains: goals, constraints, principles, CLI command surface, 7-stage pipeline, single-stage deliberation flow, session matrix, consensus rules, artifact layout, dashboard architecture, API sketch, roadmap, cost estimates, anti-patterns, future extensions.

## Deliverable Summary

### Artifact 1: Agent Team Dashboard

**Type:** Code · HTML

**Purpose:** Make the long-running multi-agent pipeline observable before any real backend exists.

**Must Include:**

- Header with run id, status badge, start time, elapsed time.
- Pipeline strip with 7 stages: Brainstorm, Plan, Specs, Implement, Review, Test, Retrospective.
- Status encoding for `pending`, `running`, `passed`, `fail`, and `dispute`.
- Current activity section showing Claude thinker, Codex thinker, synthesizer, and joint review status.
- Expandable stage cards.
- Round tabs inside each stage.
- Per-round grid with five panels:
  - Claude independent output.
  - Codex independent output.
  - Synthesizer merged output.
  - Claude review.
  - Codex review.
- Stats footer for calls, elapsed time, average rounds, disputes, and token estimate.
- Mock state controls for `Running`, `Completed`, and `With dispute`.

**Acceptance Criteria:**

- Opening `agent-team-dashboard.html` directly in a browser shows the dashboard without a dev server.
- Switching mock states updates the header, pipeline strip, stage cards, and stats.
- At least one passed stage, one running state, and one dispute state are visually inspectable.
- Markdown inside panels renders through `markdown-it`.
- Layout remains usable on desktop and mobile widths.

### Artifact 2: Agent Team Design

**Type:** Document · MD

**Purpose:** Make the framework understandable and executable before code implementation starts.

**Must Include:**

- Project goal and constraints:
  - Product is a command-line tool with short command name `aw`.
  - Claude Code CLI + Codex CLI only.
  - No paid API dependency.
  - File-system artifacts as the inter-stage channel.
  - Bounded calls and bounded iteration.
- CLI surface:
  - `aw` starts the interactive main process.
  - Inside `aw`, users can enter requirements, approve stages, abort runs, inspect status, resume runs, and open the dashboard.
  - Shell shortcuts such as `aw run --requirement requirement.md`, `aw status [run_id]`, and `aw dashboard --runs-dir ./runs --port 8080` may exist later, but they are secondary.
- Design principles:
  - Dual-agent independent thinking.
  - Independent synthesizer.
  - Conservative consensus.
  - Maximum 3 rounds per stage.
  - File-based artifacts.
- 7-stage pipeline:
  - Brainstorm.
  - Plan.
  - Specs.
  - Implement.
  - Review.
  - Test.
  - Retrospective.
- Single-stage deliberation unit:
  - Claude thinker.
  - Codex thinker.
  - Synthesizer.
  - Claude reviewer.
  - Codex reviewer.
- Session matrix and anti-bias rules.
- Core mechanisms:
  - `call_agent()`.
  - merge prompt.
  - review prompt.
  - consensus gate.
  - dispute logging.
- Artifact directory layout.
- `state.json`, `events.jsonl`, and cost/stat files.
- Dashboard design:
  - architecture.
  - HTTP endpoints.
  - UI sections.
  - SSE update flow.
  - deployment modes.
- Roadmap:
  - Phase 1 MVP.
  - Phase 2 pipeline.
  - Phase 3 feedback loop.
  - Phase 4 production hardening.
  - Phase 5 visualization and operations.
- Appendices:
  - cost estimate.
  - anti-patterns.
  - future extensions.

**Acceptance Criteria:**

- `agent-team-design.md` can be read standalone without the HTML file.
- It defines `aw` as the interactive CLI command name and treats the web dashboard as a companion surface.
- It explicitly marks implementation details that are skeleton/pseudocode rather than completed code.
- It defines the dashboard as Phase 5 in the roadmap while still allowing the HTML prototype to exist earlier as a planning artifact.
- It preserves the distinction between outer pipeline stages and inner deliberation rounds.
- It documents that 3-round force-pass must record unresolved disputes.

## Tasks

### Task 1: Create Dashboard Artifact

**Files:**

- Create: `agent-team-dashboard.html`

- [x] **Step 1: Add the single-file HTML prototype**

Create `agent-team-dashboard.html` with:

- `<head>` containing responsive viewport meta and a `markdown-it` CDN script.
- CSS variables for light/dark theme, stage status colors, typography, cards, panels, and stats.
- HTML structure for header, pipeline strip, current activity, stage cards, stats footer, and mock controls.
- JavaScript constants for the seven stages.
- JavaScript mock data for running, completed, and dispute states.
- Renderer functions for header, pipeline, activity, stage cards, rounds, and stats.
- Event handlers for expanding stages, switching rounds, and switching mock states.

- [ ] **Step 2: Manually verify static behavior**

Run:

```bash
open agent-team-dashboard.html
```

Expected:

- Browser opens the dashboard.
- `Running` state is selected by default.
- Clicking `Completed` updates all visible status and stats.
- Clicking `With dispute` highlights the implement stage as a dispute.
- Expanding a stage displays round tabs and the five-panel round grid.

- [ ] **Step 3: Commit dashboard artifact**

Run:

```bash
git add agent-team-dashboard.html
git commit -m "docs: add agent team dashboard prototype"
```

Expected:

- Commit succeeds with only `agent-team-dashboard.html` staged.

### Task 2: Create Design Document Artifact

**Files:**

- Create: `agent-team-design.md`

- [x] **Step 1: Add the canonical design document**

Create `agent-team-design.md` with these top-level sections:

```markdown
# Multi-Agent CLI Team 框架设计

## 1. 项目目标
## 2. 核心设计原则
## 3. CLI 产品形态：aw
## 4. 整体架构
## 5. Agent 分工与 Session 矩阵
## 6. 关键机制
## 7. 数据流转
## 8. 技术栈选型
## 9. 顶层代码骨架
## 10. 错误处理与降级
## 11. Web 可视化前端
## 12. 实施路线图
## 附录 A：成本估算
## 附录 B：关键反模式
## 附录 C：未来扩展
```

- [x] **Step 2: Validate document consistency**

Run:

```bash
grep -n "Phase 5" agent-team-design.md
grep -n "aw" agent-team-design.md
grep -n "交互式" agent-team-design.md
grep -n "最多 3 轮" agent-team-design.md
grep -n "state.json" agent-team-design.md
grep -n "events.jsonl" agent-team-design.md
```

Expected:

- Each command prints at least one matching line.
- The dashboard section and roadmap both mention visualization.
- The iteration cap and dispute rule are present.

- [ ] **Step 3: Commit design artifact**

Run:

```bash
git add agent-team-design.md
git commit -m "docs: add multi-agent cli team design"
```

Expected:

- Commit succeeds with only `agent-team-design.md` staged.

## Self-Review

- Spec coverage: The two requested artifacts are both represented as first-class deliverables.
- Placeholder scan: No `TBD`, `TODO`, or undefined future implementation is required for this phase.
- Scope check: Backend API, SSE, runner integration, and LangGraph execution are intentionally deferred.
- Product shape: `aw` is now the reserved command name for the future CLI.
- Naming consistency: The artifact names are stable: `agent-team-dashboard.html` and `agent-team-design.md`.

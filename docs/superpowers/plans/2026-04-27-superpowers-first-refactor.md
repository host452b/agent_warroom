# Superpowers-First Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `aw` from a fixed multi-agent SDLC pipeline design into a Superpowers-first interactive workflow runner.

**Architecture:** `aw` now treats brainstorming, design approval, implementation planning, worktree setup, TDD execution, review, and evidence-based finishing as the default product workflow. Multi-agent execution remains available, but only as a strategy selected by routing rules or evaluation evidence.

**Tech Stack:** Markdown design documents, JSON/JSONL artifact protocol, Claude Code CLI and Codex CLI as execution backends.

---

## File Structure

- Modify: `agent-team-design.md`
  - Reframe the product as a Superpowers-first workflow runner.
  - Move the legacy 7-stage SDLC pipeline into an appendix profile.
  - Define workflow phases, gates, execution strategies, file protocol, dashboard model, roadmap, and anti-patterns.

- Modify: `evaluation-plan.md`
  - Reframe evaluation as strategy validation.
  - Preserve B0/B1/B5/S baselines, but map them to `quick`, `reviewed`, and `dual` strategy decisions.

- Create: `docs/superpowers/plans/2026-04-27-superpowers-first-refactor.md`
  - Record the refactor scope and validation steps.

## Tasks

### Task 1: Rewrite Product Design

- [x] **Step 1: Replace fixed SDLC-first framing**

`agent-team-design.md` now opens with `aw` as a Superpowers-first workflow runner, not a default multi-agent SDLC pipeline.

- [x] **Step 2: Define Superpowers mapping**

The design maps brainstorming, specs, plans, worktrees, TDD, review, and evidence gates to concrete `aw` behavior.

- [x] **Step 3: Define strategy engine**

The design defines `quick`, `reviewed`, `dual`, and `eval`, with `dual` gated by evaluation.

- [x] **Step 4: Preserve legacy SDLC profile**

The 7-stage pipeline remains only as `dual-sdlc` profile guidance in the appendix.

### Task 2: Align Evaluation Plan

- [x] **Step 1: Rename evaluation purpose**

`evaluation-plan.md` now evaluates strategy candidates rather than trying to prove the whole system.

- [x] **Step 2: Map baselines to routing decisions**

`B0`, `B1`, `B5`, and `S` now inform `quick`, `reviewed`, and `dual` routing.

- [x] **Step 3: Tighten default route gate**

`dual` only enters automatic routing if it beats cheaper baselines on complex tasks with cost-aware evidence.

### Task 3: Verify Refactor

- [x] **Step 1: Check Superpowers-first language exists**

Run:

```bash
grep -n "Superpowers-first" agent-team-design.md
grep -n "Execution Strategies" agent-team-design.md
grep -n "Evidence over claims" agent-team-design.md
```

Expected: each command prints at least one matching line.

- [x] **Step 2: Check dual is not default**

Run:

```bash
grep -n "default" agent-team-design.md | grep -i dual
grep -n "dual" evaluation-plan.md | grep -i "默认"
```

Expected: matches describe dual as gated, explicit, or not default unless eval supports it.

- [ ] **Step 3: Commit**

Run:

```bash
git add agent-team-design.md evaluation-plan.md docs/superpowers/plans/2026-04-27-superpowers-first-refactor.md
git commit -m "docs: refactor aw around superpowers workflow"
```

Expected: commit succeeds.

## Self-Review

- Scope coverage: The core product workflow is now Superpowers-first.
- YAGNI: No implementation code was added.
- Consistency: `dual` is consistently described as a strategy, not the default architecture.
- Follow-up: `agent-team-dashboard.html` remains a visual prototype and should be updated later to show workflow phases, tasks, gates, and evidence.

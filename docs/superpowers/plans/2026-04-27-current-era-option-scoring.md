# Current-Era Option Scoring Gate Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a mandatory current-era 3-candidate / 10-dimension scoring gate to both Brainstorming and Planning.

**Architecture:** Brainstorming scores product or architecture directions before design. Planning scores implementation paths before task decomposition. Both gates produce lightweight Markdown artifacts that support user-visible horizontal comparison and top1 selection.

**Tech Stack:** Markdown docs, run-level artifacts, project-local `karpathy-philosophy` rule skill.

---

## File Structure

- Modify: `agent-team-design.md`
  - Add `Current-Era Option Scoring` after Brainstorming.
  - Add `Current-Era Plan Scoring` before worktree setup.
  - Define artifacts: `brainstorm-option-matrix.md` and `plan-option-matrix.md`.

- Modify: `skills/karpathy-philosophy/SKILL.md`
  - Add project rule that Brainstorming and Planning must not choose before scoring and horizontal comparison.

## Tasks

### Task 1: Add Brainstorm Scoring Gate

- [x] **Step 1: Update Brainstorming flow**

Brainstorming now identifies 3 current-era mainstream candidates, defines 10 domain-specific dimensions, scores candidates, calculates top1, then performs horizontal comparison.

- [x] **Step 2: Add artifact**

Brainstorming now writes `runs/<run_id>/artifacts/brainstorm-option-matrix.md`.

### Task 2: Add Plan Scoring Gate

- [x] **Step 1: Update Planning flow**

Planning now compares implementation paths, tool choices, task decomposition, and verification strategies before committing to a plan.

- [x] **Step 2: Add artifact**

Planning now writes `runs/<run_id>/artifacts/plan-option-matrix.md`.

### Task 3: Update Rule Skill

- [x] **Step 1: Add Karpathy rule application**

The project rule skill now states that Brainstorming and Planning must not choose a solution before the scoring and horizontal comparison gate.

### Task 4: Verify

- [x] **Step 1: Check design references**

Run:

```bash
grep -n "Current-Era Option Scoring" agent-team-design.md
grep -n "Current-Era Plan Scoring" agent-team-design.md
grep -n "brainstorm-option-matrix.md" agent-team-design.md
grep -n "plan-option-matrix.md" agent-team-design.md
```

Expected: each command prints at least one match.

- [x] **Step 2: Check rule skill reference**

Run:

```bash
grep -n "3-candidate / 10-dimension" skills/karpathy-philosophy/SKILL.md
```

Expected: prints the Brainstorming and Planning rule.

## Self-Review

- Scope: Adds only selection gates, not a full evaluation harness.
- Simplicity: The scoring matrix is lightweight Markdown and can be skipped only when user explicitly overrides it.
- Precision: Changes only design docs and the project rule skill.
- Verification: Grep checks confirm the workflow and rule references.

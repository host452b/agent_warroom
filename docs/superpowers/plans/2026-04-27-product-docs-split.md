# Product Docs Split Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the monolithic `agent-team-design.md` into product, workflow, and technical design documents.

**Architecture:** `agent-team-design.md` becomes an index. Product concerns live in `docs/product-definition.md`, user workflow and gates live in `docs/product-workflow.md`, and file protocol / schema / implementation design live in `docs/technical-design.md`.

**Tech Stack:** Markdown documentation.

---

## Tasks

### Task 1: Create Product Definition

- [x] **Step 1: Create `docs/product-definition.md`**

Contains positioning, users, pain, current-era 3-option scoring, MVP scope, non-goals, and success criteria.

### Task 2: Create Product Workflow

- [x] **Step 1: Create `docs/product-workflow.md`**

Contains commands, phases, gates, approvals, overrides, and MVP walkthrough.

### Task 3: Create Technical Design

- [x] **Step 1: Create `docs/technical-design.md`**

Contains object model, file protocol, JSON/JSONL schemas, strategy router, adapters, dashboard read model, error handling, and roadmap.

### Task 4: Convert Design Doc To Index

- [x] **Step 1: Rewrite `agent-team-design.md`**

The root design document now links to canonical docs instead of holding all details.

### Task 5: Verify

- [x] **Step 1: Check index links**

Verified `agent-team-design.md` links to Product Definition, Product Workflow, Technical Design, Evaluation Plan, Dashboard Prototype, and Karpathy Philosophy.

- [x] **Step 2: Check topic ownership**

Verified product definition contains positioning/MVP/non-goals, workflow contains commands/gates/walkthrough, and technical design contains file protocol/schema/router/dashboard model.

## Self-Review

- Scope: Documentation split only; no implementation added.
- Simplicity: Four docs, no extra hierarchy beyond `docs/`.
- Precision: Existing canonical content was moved into focused documents.
- Verification: Grep checks confirm document ownership and index links.

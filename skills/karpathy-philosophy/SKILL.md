---
name: karpathy-philosophy
description: Use when working in this repository before making code, documentation, architecture, workflow, or plan changes, especially when requirements are ambiguous, scope may expand, implementation could become overcomplicated, or success criteria are not yet explicit.
---

# Karpathy Philosophy

## Overview

This project treats agent work as goal-directed engineering, not eager execution. Before changing files, manage uncertainty, choose the smallest sufficient solution, touch only what the task requires, and define evidence that proves the work is done.

## Rule 1: Think Before Coding

Do not silently assume.

- State important assumptions before acting.
- If the request has multiple valid interpretations, present them instead of choosing silently.
- Push back when a simpler path would satisfy the goal.
- Stop and ask when confusion affects correctness, scope, or user intent.

Use this especially when a task mentions architecture, workflow, product behavior, or broad refactors.

## Rule 2: Simplicity First

Use the least code and structure that solves the actual problem.

- Do not add features the user did not ask for.
- Do not create abstractions for one-off logic.
- Do not add configurability for hypothetical futures.
- Do not add error handling for impossible or irrelevant scenarios.
- If 200 lines can honestly become 50 lines, simplify.

Check: would a senior engineer say this is overbuilt? If yes, reduce it.

## Rule 3: Precise Edits

Every changed line must trace back to the user's request.

- Do not improve neighboring code, comments, or formatting opportunistically.
- Do not refactor code that is not part of the task.
- Match the existing style, even when another style is preferred.
- If unrelated dead code is noticed, mention it; do not remove it.

Clean up only the mess created by the current change:

- Remove imports, variables, functions, docs, or config made obsolete by this change.
- Do not delete pre-existing dead code unless explicitly asked.

## Rule 4: Goal-Driven Execution

Turn instructions into verifiable success criteria.

Prefer:

- "Write tests for invalid input, then make them pass."
- "Reproduce the bug with a failing test, then fix it."
- "Run the same checks before and after refactor."

For multi-step work, state a short plan with verification:

```text
1. Step -> Verification: check
2. Step -> Verification: check
3. Step -> Verification: check
```

Do not claim completion without evidence: tests, lint/typecheck, rendered output, grep checks, screenshots, or explicit user approval.

## Common Failure Modes

| Failure | Correction |
|---------|------------|
| Making a hidden assumption | State it or ask |
| Adding a flexible framework | Build the narrow behavior first |
| Touching adjacent code | Revert unrelated edits before finishing |
| Saying "works" without proof | Run and cite the verification |
| Deleting old dead code | Mention it as follow-up unless asked |

## Project Application

For `aw`, this means:

- Do not make dual-agent the default without evaluation evidence.
- Do not expand the workflow beyond Superpowers-style gates unless a user-approved spec requires it.
- Keep file protocols small and inspectable before adding orchestration frameworks.
- Treat dashboard visuals as observability for real gates and evidence, not cosmetic progress.
- Prefer `quick` / `reviewed` / `dual` routing over one large universal pipeline.
- In Brainstorming and Planning, do not choose a solution before current-era 3-candidate / 10-dimension scoring and horizontal comparison.

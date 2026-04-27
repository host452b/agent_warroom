# aw Product Definition

## Positioning

`aw` is an interactive CLI for AI coding workflows. It turns Claude Code CLI and Codex CLI from eager coding agents into a process-first, auditable, verifiable, resumable engineering workflow.

It does not try to be a new model, IDE, or cloud PR agent. Its primary value is making agent work trustworthy.

## Product Lock

**One sentence:** `aw` is an interactive workflow runner that helps developers turn agentic coding from chat-driven execution into a clarified, planned, tested, reviewed, and evidence-backed process.

**Core value:** make AI coding work trustworthy.

**Primary interaction:** user starts `aw`, enters a requirement, and stays in a persistent session while the tool guides them through design, planning, execution, review, and finish gates.

## Target Users

### Primary User: Senior Developer / Owner-Engineer

Already uses Claude Code or Codex, but does not trust agents to directly modify code without structure.

Pain points:

- agent misunderstands requirements
- agent overbuilds simple tasks
- agent edits unrelated code
- agent claims completion without evidence
- agent cannot clearly explain what is blocked

### Secondary User: Technical Lead / Reviewer

Wants agent output to fit a reviewable engineering process.

Pain points:

- no durable spec
- no plan tied to files and tests
- no trace from decision to implementation
- no reliable evidence summary
- hard to audit agent-created code

### Exploratory User: Heavy AI Coding User

Runs multiple agent strategies and wants data on quality, cost, latency, and variance.

Pain points:

- cannot compare strategies fairly
- cannot replay previous runs
- cannot know whether multi-agent is worth the cost

## User Pain

`aw` exists because models often:

- make hidden assumptions
- fail to manage confusion
- skip tradeoffs
- overcomplicate code and architecture
- modify unrelated code
- delete things they do not understand
- optimize for passing commands without proving product intent

The product counters those behaviors with:

- thinking before coding
- current-era option scoring
- design approval gates
- concrete implementation plans
- TDD execution
- precise edits
- review gates
- evidence-first completion

## Current-Era Option Scan

Time context: 2026-04-27.

Domain: AI coding workflow tools.

Three dominant product directions:

| Option | Representative Shape | Positioning |
|--------|----------------------|-------------|
| A. Agentic CLI | Claude Code / Codex CLI | Local interactive coding agent that can read/write files and run commands |
| B. Cloud PR Agent | GitHub Copilot coding agent | Async agent that works from issues/PRs in a hosted workflow |
| C. Process-First Workflow Runner | Superpowers-style workflow | Structured agent process: clarify, spec, plan, TDD, review, evidence |

## 10-Dimension Scoring

Scores are 1-5. Weights are equal for product definition.

| Dimension | A. Agentic CLI | B. Cloud PR Agent | C. Workflow Runner |
|-----------|---------------:|------------------:|-------------------:|
| Interaction speed | 5 | 3 | 4 |
| Local code control | 5 | 2 | 5 |
| Auditability | 3 | 4 | 5 |
| Prevents wrong execution | 3 | 4 | 5 |
| Design / planning quality | 3 | 3 | 5 |
| TDD / verification support | 3 | 4 | 5 |
| Low-complexity MVP | 4 | 2 | 4 |
| Resume / replay fit | 3 | 4 | 5 |
| Claude/Codex CLI fit | 5 | 2 | 4 |
| Differentiation | 3 | 2 | 5 |
| **Total** | **37** | **30** | **47** |

## Top1 Result

Top1: **C. Process-First Workflow Runner**.

Rationale:

- It is differentiated from Claude Code and Codex instead of competing directly with them.
- It addresses the hardest trust gap: hidden assumptions, overbuild, unrelated edits, and missing evidence.
- It can still use Claude/Codex as execution backends.
- It creates durable artifacts and gates that are useful even if the underlying model changes.

## MVP Scope

P0 proves one thing: `aw` can turn one agent coding request into a process with requirement, option scoring, spec, plan, gates, evidence, and resumability. It does not need to automatically complete a real software project.

P0 includes:

- interactive `aw` shell
- run/state/events file protocol
- Brainstorming with current-era 3-candidate / 10-dimension scoring
- requirement artifact
- product spec artifact
- plan artifact with plan-level 3-candidate / 10-dimension scoring
- spec and plan approval gates
- at least one evidence command recorded
- `status`
- `show spec`
- `show plan`
- `evidence`
- `resume <run_id>`

P1 can add:

- automatic full TDD task execution
- dashboard SSE
- automatic worktree creation
- review agent
- PR / merge integration
- replay mode
- dual strategy

## MVP Cut Line

P0 stops at:

```text
natural language input
-> requirement.md
-> brainstorm-option-matrix.md
-> spec.md + approval
-> plan-option-matrix.md
-> plan.md + approval
-> one evidence command recorded
-> status/evidence/resume works
```

P0 does not require:

```text
automatic full-code implementation
automatic full test matrix
automatic PR
automatic multi-agent
complex dashboard
LangGraph orchestration
```

## Demo Scenario

Use a deliberately small demo task:

```text
build a local-first note taking CLI
```

Successful demo path:

1. `aw` creates a run.
2. `aw` asks one clarification question.
3. `aw` outputs 3-candidate / 10-dimension brainstorm scoring.
4. `aw` generates `spec.md`.
5. user approves spec.
6. `aw` outputs 3-candidate / 10-dimension plan scoring.
7. `aw` generates `plan.md`.
8. user approves plan.
9. `aw` records one evidence command, such as `pytest -q`.
10. `status` and `evidence` explain the current state.

## Non-Goals

MVP does not include:

- new foundation model
- general IDE
- cloud PR agent
- default multi-agent execution
- autonomous large-scale code changes
- automatic full-code implementation
- automatic PR
- complex dashboard
- LangGraph orchestration
- bypassing user approval
- plugin marketplace
- complex orchestration framework before file protocol is stable

## Success Criteria

MVP is successful when:

- a run can start from natural language and produce `spec.md`
- spec is preceded by `brainstorm-option-matrix.md`
- plan is preceded by `plan-option-matrix.md`
- at least one task records RED/GREEN evidence
- `status` accurately reports current phase, gate, and missing evidence
- `evidence` explains why a step is considered complete
- exiting and resuming restores the run
- completion is impossible without evidence or explicit override

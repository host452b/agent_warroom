# aw Design Index

`aw` is a Superpowers-first interactive workflow runner for AI coding. It wraps Claude Code CLI and Codex CLI in a product flow that emphasizes clarification, option scoring, planning, TDD, review, evidence, and resumability.

## Canonical Docs

- [Product Definition](docs/product-definition.md): product positioning, target users, value proposition, MVP scope, and non-goals.
- [Product Workflow](docs/product-workflow.md): interactive commands, workflow phases, gates, approvals, overrides, and status/evidence examples.
- [Technical Design](docs/technical-design.md): object model, file protocol, JSON/JSONL schemas, strategy router, dashboard read model, and implementation roadmap.
- [Evaluation Plan](evaluation-plan.md): strategy validation for `quick`, `reviewed`, and `dual`.
- [Dashboard Prototype](agent-team-dashboard.html): static HTML prototype for visualizing agent runs.

## Project Rules

- [Karpathy Philosophy Rule Skill](skills/karpathy-philosophy/SKILL.md): mandatory project rule for thinking before coding, simplicity, precise edits, and evidence-driven execution.

## Current Product Lock

- Product shape: interactive CLI named `aw`.
- Core positioning: process-first workflow runner, not another coding model or cloud PR agent.
- Default workflow: `Intake -> Brainstorming -> Option Scoring -> Spec -> Plan -> Plan Scoring -> Worktree -> TDD Execution -> Review -> Evidence -> Finish`.
- Strategy model: `quick`, `reviewed`, `dual`, `eval`; `dual` is not default until evaluation proves value.


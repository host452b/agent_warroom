# Agent Warroom (`aw`)

`aw` is an interactive CLI workflow runner for AI coding. It turns agentic coding from ad hoc chat execution into a clarified, planned, auditable, and evidence-backed process.

The current implementation is the P0 skeleton: local file-backed runs, deterministic workflow artifacts, approval gates, and command evidence. It does not yet run Claude/Codex automatically or execute a full coding plan.

## What P0 Does

- Starts an interactive `aw` shell.
- Captures a natural-language requirement.
- Writes a resumable run under `runs/run-*`.
- Creates:
  - `artifacts/requirement.md`
  - `artifacts/brainstorm-option-matrix.md`
  - `artifacts/spec.md`
  - `artifacts/plan-option-matrix.md`
  - `artifacts/plan.md`
- Records user approvals in `evidence/approvals.jsonl`.
- Records command evidence in `evidence/commands.jsonl`.
- Supports `help`, `status`, `resume`, `show`, `write`, and `evidence` commands.

## Quick Start

From the repository root:

```bash
python -m aw.cli
```

Example interactive flow:

```text
aw> help
aw> build a local-first note taking CLI
aw> status
aw> show spec
aw> approve
aw> write plan
aw> show plan
aw> record-evidence pytest -q
aw> runs
aw> resume run-YYYYMMDD-HHMMSS
aw> evidence
aw> exit
```

Use the printed run id when calling direct commands:

```bash
python -m aw.cli start "build a local-first note taking CLI"
python -m aw.cli runs
python -m aw.cli status run-YYYYMMDD-HHMMSS
python -m aw.cli resume run-YYYYMMDD-HHMMSS
python -m aw.cli show spec run-YYYYMMDD-HHMMSS
python -m aw.cli approve run-YYYYMMDD-HHMMSS
python -m aw.cli write plan run-YYYYMMDD-HHMMSS
python -m aw.cli record-evidence run-YYYYMMDD-HHMMSS "pytest -q" --status passed --output "tests passed"
python -m aw.cli evidence run-YYYYMMDD-HHMMSS
```

## Run Protocol

Each run is stored as plain files:

```text
runs/run-{timestamp}/
├── run-manifest.json
├── state.json
├── events.jsonl
├── decisions.jsonl
├── artifacts/
│   ├── requirement.md
│   ├── brainstorm-option-matrix.md
│   ├── spec.md
│   ├── plan-option-matrix.md
│   └── plan.md
└── evidence/
    ├── approvals.jsonl
    └── commands.jsonl
```

This keeps the workflow inspectable, resumable, and easy to debug.

## Verification

Run the current test suite with:

```bash
python -m pytest -q
```

## Project Docs

- [Design Index](agent-team-design.md)
- [Product Definition](docs/product-definition.md)
- [Product Workflow](docs/product-workflow.md)
- [Technical Design](docs/technical-design.md)
- [Evaluation Plan](evaluation-plan.md)
- [Dashboard Prototype](agent-team-dashboard.html)
- [Karpathy Philosophy Rule Skill](skills/karpathy-philosophy/SKILL.md)

## Scope Boundaries

P0 intentionally does not include automatic multi-agent orchestration, LangGraph, dashboard SSE, automatic PR integration, or full TDD execution across arbitrary repositories. Those belong to later phases after the file protocol and approval/evidence loop are stable.

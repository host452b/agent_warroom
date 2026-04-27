# aw Technical Design

## Architecture

`aw` is a local interactive CLI with durable file-backed state.

Core modules:

- interactive shell
- run manager
- artifact registry
- gate engine
- evidence recorder
- dashboard read model
- strategy router
- Claude/Codex adapters

P0 only requires the first five modules plus enough status/resume support to read file-backed state. Strategy router and Claude/Codex adapters can be thin placeholders until P1.

No database is required for MVP. JSON/JSONL files are the durable protocol.

## Object Model

| Object | Minimum Fields |
|--------|----------------|
| `Run` | `run_id`, `status`, `created_at`, `updated_at`, `current_phase`, `strategy` |
| `Phase` | `name`, `status`, `started_at`, `ended_at` |
| `Gate` | `gate_id`, `phase`, `status`, `required_evidence`, `approved_by` |
| `Artifact` | `key`, `path`, `kind`, `created_at` |
| `Evidence` | `key`, `path`, `kind`, `command`, `status` |
| `Strategy` | `quick`, `reviewed`, `dual`, `eval` |
| `Task` | `task_id`, `title`, `files`, `verification`, `status` |
| `Decision` | `decision_id`, `context`, `options`, `selected`, `reason` |

Run status enum:

```text
draft | running | waiting_user | blocked | completed | aborted
```

Phase status enum:

```text
pending | active | waiting_gate | passed | failed | skipped
```

Task status enum:

```text
pending | red | green | review | done | blocked
```

## File Protocol

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
│   ├── plan.md
│   └── final-summary.md
├── tasks/
│   └── task-001/
│       ├── task.json
│       ├── red-output.txt
│       ├── green-output.txt
│       ├── review.json
│       └── commit.txt
└── evidence/
    ├── approvals.jsonl
    ├── commands.jsonl
    ├── tests.jsonl
    └── screenshots/
```

Rules:

- `state.json` is a mutable snapshot.
- `events.jsonl`, `decisions.jsonl`, and `evidence/*.jsonl` are append-only.
- Markdown artifacts are for humans.
- JSON/JSONL files are for machines and dashboard.
- Dashboard must not infer business logic; it reads state, events, artifacts, and evidence.

P0 required files:

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
    └── commands.jsonl
```

## run-manifest.json

```json
{
  "run_id": "run-20260427-153000",
  "created_at": "2026-04-27T15:30:00+08:00",
  "updated_at": "2026-04-27T15:42:10+08:00",
  "workspace": "/path/to/repo",
  "worktree": ".worktrees/run-20260427-153000",
  "requirement": "build a local-first note taking CLI",
  "strategy": "reviewed",
  "status": "running"
}
```

## state.json

```json
{
  "run_id": "run-20260427-153000",
  "status": "waiting_user",
  "current_phase": "spec",
  "current_gate": {
    "gate_id": "spec_section_approval",
    "phase": "spec",
    "status": "waiting",
    "required": ["user approval"],
    "evidence": ["artifacts/spec.md"],
    "missing": ["user approval for Product Scope section"]
  },
  "current_task": null,
  "strategy": "reviewed",
  "artifacts": {
    "requirement": "artifacts/requirement.md",
    "brainstorm_matrix": "artifacts/brainstorm-option-matrix.md",
    "spec": "artifacts/spec.md"
  },
  "stats": {
    "agent_calls": 4,
    "tokens_in_est": 8200,
    "tokens_out_est": 3100,
    "elapsed_seconds": 730
  }
}
```

## events.jsonl

```jsonl
{"ts":"2026-04-27T15:30:00+08:00","event":"run_created","run_id":"run-20260427-153000"}
{"ts":"2026-04-27T15:31:10+08:00","event":"phase_started","phase":"brainstorm"}
{"ts":"2026-04-27T15:35:00+08:00","event":"artifact_written","artifact":"brainstorm_matrix","path":"artifacts/brainstorm-option-matrix.md"}
{"ts":"2026-04-27T15:38:00+08:00","event":"gate_waiting","gate":"spec_section_approval"}
{"ts":"2026-04-27T15:39:00+08:00","event":"gate_approved","gate":"spec_section_approval","by":"user"}
```

## decisions.jsonl

```jsonl
{"ts":"2026-04-27T15:34:20+08:00","phase":"brainstorm","decision":"select_product_direction","selected":"plain_markdown_folder","options":["plain_markdown_folder","sqlite_cli","git_backed_workspace"],"reason":"highest weighted score and lowest MVP risk"}
{"ts":"2026-04-27T15:40:10+08:00","phase":"plan","decision":"select_implementation_path","selected":"full_command_parser_with_tests","options":["minimal_cli","full_parser_tests","plugin_ready_architecture"],"reason":"best balance of testability and MVP scope"}
```

## Task JSON

```json
{
  "task_id": "task-001",
  "title": "Add CLI add/list commands",
  "status": "green",
  "files": [
    "src/aw_notes/cli.py",
    "tests/test_cli.py"
  ],
  "verification": {
    "red_command": "pytest tests/test_cli.py::test_add_and_list -v",
    "green_command": "pytest tests/test_cli.py::test_add_and_list -v"
  },
  "evidence": {
    "red_output": "tasks/task-001/red-output.txt",
    "green_output": "tasks/task-001/green-output.txt"
  },
  "commit": "abc1234"
}
```

## Evidence

`evidence/tests.jsonl`:

```jsonl
{"ts":"2026-04-27T15:50:00+08:00","task_id":"task-001","phase":"red","command":"pytest tests/test_cli.py::test_add_and_list -v","status":"failed_expected","output":"tasks/task-001/red-output.txt"}
{"ts":"2026-04-27T15:55:00+08:00","task_id":"task-001","phase":"green","command":"pytest tests/test_cli.py::test_add_and_list -v","status":"passed","output":"tasks/task-001/green-output.txt"}
```

`evidence/approvals.jsonl`:

```jsonl
{"ts":"2026-04-27T15:39:00+08:00","gate":"spec_section_approval","artifact":"artifacts/spec.md","approved_by":"user","note":"Product Scope locked"}
```

## Strategy Router

| Condition | Strategy |
|-----------|----------|
| question or explanation only | `quick` |
| low-risk docs | `quick` |
| single-file low-risk code | `reviewed` |
| multi-module behavior change | `reviewed` or `dual` |
| architecture, debugging, high-risk refactor | `dual` |
| strategy validation | `eval` |

User override:

```text
aw> use dual for this run
aw> use quick
aw> run eval first
```

## Claude/Codex Adapter

MVP adapter rules:

- invoke Claude Code CLI and Codex CLI through subprocess.
- preserve role-local session/history.
- never hide raw command failures.
- write all prompts and outputs to run artifacts when they affect decisions.
- do not make `dual` default until `evaluation-plan.md` supports it.

## Dashboard Read Model

Dashboard reads:

- `state.json`
- `events.jsonl`
- `decisions.jsonl`
- `artifacts/*.md`
- `evidence/*.jsonl`
- `tasks/*/task.json`

Dashboard displays:

- current phase and gate
- missing evidence
- task red/green/review state
- artifacts
- decisions and overrides
- final evidence summary

## Error Handling

| Failure | Response |
|---------|----------|
| CLI process crash | recover from `state.json` and append event |
| session expires | recreate session from spec/plan/current summary |
| Codex has no session | use role-local history |
| token limit | summarize and shrink artifact input |
| RED test fails for wrong reason | stop and fix test |
| GREEN does not pass | keep task blocked |
| review has blocking finding | return to task or plan revision |
| baseline tests already fail | record as pre-existing and ask user |

## Roadmap

### Phase P0 — Product Workflow Skeleton

- interactive `aw` shell
- create/resume run directory
- write `run-manifest.json`, `state.json`, `events.jsonl`
- write `artifacts/requirement.md`
- generate or capture `brainstorm-option-matrix.md`
- write `spec.md` and approve gate
- generate or capture `plan-option-matrix.md`
- write `plan.md` and approve gate
- record one evidence command
- `status`, `show spec`, `show plan`, `evidence`, `resume`

### Phase 0 — Evaluation Harness

- fixed MVP task suite
- `B0/B1/B5/S` runner skeletons
- cost-quality output
- strategy routing decision

### Phase 1 — File Protocol + Shell

- interactive `aw`
- `run-manifest.json`, `state.json`, `events.jsonl`
- `status`, `runs`, `resume`, `abort`
- artifact registry

### Phase 2 — Brainstorm + Spec + Plan

- clarification flow
- brainstorm option scoring
- spec approval gate
- plan option scoring
- plan artifact

### Phase 3 — Worktree + TDD

- worktree setup
- baseline verification
- red/green task loop
- evidence capture

### Phase 4 — Review + Finish

- spec compliance review
- code quality review
- finish options

### Phase 5 — Strategy Engine

- `quick`
- `reviewed`
- `dual`
- `eval`
- router and user override

### Phase 6 — Dashboard

- FastAPI reader
- SSE events
- workflow strip
- task board
- evidence panel

# aw Product Workflow

## Default Flow

```text
Intake
  -> Brainstorming
  -> Current-Era Option Scoring
  -> Design Spec
  -> User Approval Gate
  -> Implementation Plan
  -> Current-Era Plan Scoring
  -> Worktree Setup
  -> Task Execution (TDD)
  -> Review
  -> Verification Evidence
  -> Finish Decision
```

## P0 Flow

P0 implements a narrower path:

```text
Natural language input
  -> requirement.md
  -> brainstorm-option-matrix.md
  -> spec.md
  -> spec approval
  -> plan-option-matrix.md
  -> plan.md
  -> plan approval
  -> record one evidence command
  -> status / evidence / resume
```

## Interactive Commands

| Command | Purpose |
|---------|---------|
| natural language input | create or continue the current run |
| `status` | show current run, phase, gate, and missing evidence |
| `brainstorm` | enter clarification and option scoring |
| `approve` | approve the current user gate |
| `show spec` | show current spec |
| `write plan` | generate implementation plan and plan scoring |
| `show plan` | show current plan |
| `run next` | execute the next task |
| `evidence` | show evidence for current run or task |
| `review` | run or show review results |
| `finish` | choose keep / merge / PR / abort |
| `runs` | list historical runs |
| `resume <run_id>` | resume a run |
| `abort` | abort current run |
| `open dashboard` | open dashboard |
| `help` | show available commands |
| `exit` | exit interactive shell |

P0 command subset:

| Command | P0 behavior |
|---------|-------------|
| natural language input | create run and write requirement artifact |
| `status` | show current phase, gate, and missing evidence |
| `approve` | approve spec or plan gates |
| `show spec` | print `artifacts/spec.md` |
| `write plan` | write plan scoring and plan artifacts |
| `show plan` | print `artifacts/plan.md` |
| `evidence` | show recorded evidence |
| `resume <run_id>` | restore existing run |
| `exit` | exit without losing run state |

Shortcut commands:

```bash
aw status [run_id]
aw resume <run_id>
aw dashboard --runs-dir ./runs --port 8080
aw eval --suite mvp
```

## Core Objects

| Object | Meaning |
|--------|---------|
| `Run` | one complete workflow instance |
| `Phase` | workflow stage such as intake, brainstorm, plan, execute |
| `Gate` | required proof before moving to the next step |
| `Artifact` | durable human-readable output such as spec or plan |
| `Evidence` | proof such as test output, approval, review result, screenshot |
| `Strategy` | execution mode: `quick`, `reviewed`, `dual`, `eval` |
| `Task` | smallest executable unit from a plan |
| `Decision` | recorded selection, usually from option scoring or user override |

## Phase Definitions

### Intake

Captures the requirement and decides whether the work is small enough for one run.

Gate: `requirement_captured`.

Required evidence:

- `artifacts/requirement.md`
- scope is not obviously too broad

### Brainstorming

Turns a rough idea into a design direction.

Required behavior:

- inspect repo/docs/recent commits
- ask one clarification at a time
- identify 3 current-era mainstream candidates
- define 10 domain-specific dimensions
- score and select top1
- compare alternatives horizontally

Gate: `option_scoring_done`.

Required evidence:

- `artifacts/brainstorm-option-matrix.md`
- `decisions.jsonl` entry for selected product direction

### Spec

Presents product/design sections for user approval.

Gate: `spec_approved`.

Required evidence:

- `artifacts/spec.md`
- no placeholders
- explicit user approval

### Plan

Builds implementation plan from approved spec.

Required behavior:

- compare 3 implementation paths
- define 10 plan-level dimensions
- select top1
- produce concrete task plan with files, tests, commands, and verification

Gates:

- `plan_scoring_done`
- `plan_approved`

Required evidence:

- `artifacts/plan-option-matrix.md`
- `artifacts/plan.md`
- explicit user approval

### Worktree

Prepares isolated execution workspace.

Gate: `baseline_verified`.

Required evidence:

- worktree path recorded
- baseline command run
- baseline output stored

### Execute

Runs plan tasks using TDD.

P0 only needs to record one evidence command. Full automatic TDD task execution is P1.

Gates:

- `task_red_verified`
- `task_green_verified`

Required evidence:

- failing test output for RED
- passing test output for GREEN
- task status updated

### Review

Checks spec compliance and code quality.

Gate: `review_passed`.

Required evidence:

- review artifact
- blocking findings count is 0

### Finish

Summarizes evidence and asks user how to finish.

Gate: `completion_evidence_ready`.

Required evidence:

- final test output
- review output
- approvals and overrides summary

## Gate Rules

- `status` always shows the current gate and missing evidence.
- `approve` only satisfies user gates such as `spec_approved` and `plan_approved`.
- automatic gates require command output or artifacts.
- `overridden` is not the same as `passed`.
- all overrides must appear in final summary.

Gate status enum:

```text
waiting | passed | failed | overridden
```

## MVP Walkthrough

```text
$ aw
aw> build a local-first note taking CLI
```

`aw` creates a run and captures the requirement.

```text
aw: Is this for personal single-user use or team-shared use?
```

After clarification, `aw` scores options:

```text
Options:
A. Plain Markdown folder
B. SQLite-backed CLI
C. Git-backed Markdown workspace

Top1: A. Plain Markdown folder
```

Then `aw` asks for spec approval section by section:

```text
aw: Proposed spec section 1/4: Product Scope
aw: approve / revise?
```

After spec approval:

```text
aw> write plan
```

`aw` scores implementation paths:

```text
A. Minimal CLI skeleton
B. Full command parser + tests
C. Plugin-ready architecture

Top1: B. Full command parser + tests
```

Then executes task by task:

```text
aw> run next
Task 001: CLI add/list command
RED: failed as expected
GREEN: tests passed
```

Finish:

```text
aw> finish
Evidence:
- 12 tests passed
- 0 blocking findings
- 3 tasks completed
```

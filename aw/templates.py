def brainstorm_matrix(requirement: str) -> str:
    return f"""# Brainstorm Option Matrix

Requirement: {requirement}

| Dimension | A. Plain Markdown folder | B. SQLite-backed CLI | C. Git-backed Markdown workspace |
|-----------|-------------------------:|---------------------:|---------------------------------:|
| MVP simplicity | 5 | 3 | 3 |
| Local-first fit | 5 | 5 | 5 |
| User inspectability | 5 | 3 | 4 |
| Testability | 4 | 4 | 3 |
| Data portability | 5 | 3 | 5 |
| Implementation risk | 5 | 3 | 2 |
| Future sync path | 3 | 3 | 5 |
| Performance needs | 4 | 5 | 4 |
| Beginner ergonomics | 5 | 4 | 3 |
| Scope discipline | 5 | 3 | 2 |
| **Total** | **46** | **36** | **36** |

Top1: **A. Plain Markdown folder**.

Reason: It best fits the P0 goal: simple, local-first, inspectable, and easy to test without adding a database or sync abstraction.
"""


def spec(requirement: str) -> str:
    return f"""# Spec

## Requirement

{requirement}

## Product Scope

Build the smallest local-first note taking CLI that can create and list notes stored as plain Markdown files.

## User Flow

1. User runs an add command with note text.
2. CLI writes a Markdown file into a local notes directory.
3. User runs a list command.
4. CLI prints the saved note titles or file names.

## Non-Goals

- No sync service.
- No database.
- No rich editor.
- No multi-user collaboration.

## Acceptance Criteria

- Notes are stored as human-readable Markdown files.
- Add and list behavior is covered by tests.
- Commands fail with clear output for invalid input.
"""


def plan_matrix(requirement: str) -> str:
    return f"""# Plan Option Matrix

Requirement: {requirement}

| Dimension | A. Minimal CLI only | B. Full parser with tests | C. Plugin-ready architecture |
|-----------|--------------------:|--------------------------:|-----------------------------:|
| P0 completeness | 3 | 5 | 4 |
| TDD fit | 3 | 5 | 4 |
| Simplicity | 5 | 4 | 2 |
| User-visible value | 3 | 5 | 4 |
| Risk control | 4 | 5 | 2 |
| File scope | 5 | 4 | 2 |
| Future extension | 2 | 4 | 5 |
| Reviewability | 4 | 5 | 3 |
| Evidence quality | 3 | 5 | 4 |
| Avoids overbuild | 5 | 4 | 1 |
| **Total** | **37** | **46** | **31** |

Top1: **B. Full parser with tests**.

Reason: It gives enough behavior to verify the spec while still avoiding plugin or framework complexity.
"""


def plan(requirement: str) -> str:
    return f"""# Implementation Plan

Requirement: {requirement}

## Task 1: CLI Skeleton

- Files: `src/notes_cli/cli.py`, `tests/test_cli.py`
- RED: write help/add/list command tests
- GREEN: implement the smallest parser that passes
- Verification: `pytest tests/test_cli.py -q`

## Task 2: Markdown Storage

- Files: `src/notes_cli/store.py`, `tests/test_store.py`
- RED: write add/list storage tests against a temp directory
- GREEN: write Markdown files and list them
- Verification: `pytest tests/test_store.py -q`

## Task 3: End-to-End Evidence

- Files: `tests/test_cli.py`
- RED: failing CLI flow for add then list
- GREEN: connect parser to storage
- Verification: `pytest -q`
"""

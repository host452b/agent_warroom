from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from aw import templates


@dataclass(frozen=True)
class RunRef:
    run_id: str
    path: Path


def _run_id_from_iso(now: str) -> str:
    dt = datetime.fromisoformat(now)
    return dt.strftime("run-%Y%m%d-%H%M%S")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, data: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def _gate(gate_id: str, phase: str, status: str, evidence: list[str], missing: list[str]) -> dict:
    return {
        "gate_id": gate_id,
        "phase": phase,
        "status": status,
        "required": ["user approval"] if gate_id.endswith("_approved") else ["evidence"],
        "evidence": evidence,
        "missing": missing,
    }


def append_event(run_path: Path, event: dict) -> None:
    _append_jsonl(run_path / "events.jsonl", event)


def create_run(runs_dir: Path, requirement: str, now: str) -> RunRef:
    run_id = _run_id_from_iso(now)
    run_path = runs_dir / run_id
    artifacts = run_path / "artifacts"
    evidence = run_path / "evidence"
    artifacts.mkdir(parents=True, exist_ok=False)
    evidence.mkdir(parents=True, exist_ok=False)

    (artifacts / "requirement.md").write_text(
        requirement.rstrip() + "\n",
        encoding="utf-8",
    )
    (artifacts / "brainstorm-option-matrix.md").write_text(
        templates.brainstorm_matrix(requirement),
        encoding="utf-8",
    )
    (artifacts / "spec.md").write_text(templates.spec(requirement), encoding="utf-8")
    _write_json(
        run_path / "run-manifest.json",
        {
            "run_id": run_id,
            "created_at": now,
            "updated_at": now,
            "requirement": requirement,
            "strategy": "reviewed",
            "status": "running",
        },
    )
    _write_json(
        run_path / "state.json",
        {
            "run_id": run_id,
            "status": "waiting_user",
            "current_phase": "spec",
            "current_gate": _gate(
                "spec_approved",
                "spec",
                "waiting",
                ["artifacts/brainstorm-option-matrix.md", "artifacts/spec.md"],
                ["user approval for spec.md"],
            ),
            "artifacts": {
                "requirement": "artifacts/requirement.md",
                "brainstorm_matrix": "artifacts/brainstorm-option-matrix.md",
                "spec": "artifacts/spec.md",
            },
        },
    )
    (run_path / "events.jsonl").write_text("", encoding="utf-8")
    (run_path / "decisions.jsonl").write_text("", encoding="utf-8")
    append_event(run_path, {"ts": now, "event": "run_created", "run_id": run_id})
    _append_jsonl(
        run_path / "decisions.jsonl",
        {
            "ts": now,
            "phase": "brainstorm",
            "decision": "select_product_direction",
            "selected": "plain_markdown_folder",
            "options": [
                "plain_markdown_folder",
                "sqlite_backed_cli",
                "git_backed_markdown_workspace",
            ],
            "reason": "highest score and lowest MVP risk",
        },
    )
    return RunRef(run_id=run_id, path=run_path)


def load_state(runs_dir: Path, run_id: str) -> dict:
    state_path = runs_dir / run_id / "state.json"
    return json.loads(state_path.read_text(encoding="utf-8"))


def list_runs(runs_dir: Path) -> list[dict]:
    if not runs_dir.exists():
        return []
    manifests = sorted(runs_dir.glob("run-*/run-manifest.json"))
    return [
        json.loads(manifest.read_text(encoding="utf-8"))
        for manifest in manifests
    ]


def save_state(runs_dir: Path, run_id: str, state: dict) -> None:
    _write_json(runs_dir / run_id / "state.json", state)


def approve_gate(runs_dir: Path, run_id: str, now: str) -> dict:
    run_path = runs_dir / run_id
    state = load_state(runs_dir, run_id)
    gate = state["current_gate"]
    gate_id = gate.get("gate_id", "unknown") if isinstance(gate, dict) else str(gate)
    if isinstance(gate, dict):
        gate["status"] = "passed"
        gate["missing"] = []
    (run_path / "evidence").mkdir(parents=True, exist_ok=True)
    _append_jsonl(
        run_path / "evidence" / "approvals.jsonl",
        {
            "ts": now,
            "gate": gate_id,
            "approved_by": "user",
        },
    )
    save_state(runs_dir, run_id, state)
    append_event(run_path, {"ts": now, "event": "gate_approved", "gate": gate_id})
    return state


def write_plan_artifacts(runs_dir: Path, run_id: str, now: str) -> None:
    run_path = runs_dir / run_id
    requirement = (run_path / "artifacts" / "requirement.md").read_text(encoding="utf-8").strip()
    artifacts = run_path / "artifacts"
    (artifacts / "plan-option-matrix.md").write_text(
        templates.plan_matrix(requirement),
        encoding="utf-8",
    )
    (artifacts / "plan.md").write_text(templates.plan(requirement), encoding="utf-8")

    state = load_state(runs_dir, run_id)
    state["status"] = "waiting_user"
    state["current_phase"] = "plan"
    state["current_gate"] = _gate(
        "plan_approved",
        "plan",
        "waiting",
        ["artifacts/plan-option-matrix.md", "artifacts/plan.md"],
        ["user approval for plan.md"],
    )
    state.setdefault("artifacts", {})["plan_matrix"] = "artifacts/plan-option-matrix.md"
    state["artifacts"]["plan"] = "artifacts/plan.md"
    save_state(runs_dir, run_id, state)

    append_event(run_path, {"ts": now, "event": "artifact_written", "artifact": "plan"})
    _append_jsonl(
        run_path / "decisions.jsonl",
        {
            "ts": now,
            "phase": "plan",
            "decision": "select_implementation_path",
            "selected": "full_parser_with_tests",
            "options": [
                "minimal_cli_only",
                "full_parser_with_tests",
                "plugin_ready_architecture",
            ],
            "reason": "best balance of testability and MVP scope",
        },
    )

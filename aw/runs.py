from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True)
class RunRef:
    run_id: str
    path: Path


def _run_id_from_iso(now: str) -> str:
    dt = datetime.fromisoformat(now)
    return dt.strftime("run-%Y%m%d-%H%M%S")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def append_event(run_path: Path, event: dict) -> None:
    with (run_path / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


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
            "status": "running",
            "current_phase": "brainstorm",
            "current_gate": "option_scoring_done",
            "artifacts": {"requirement": "artifacts/requirement.md"},
        },
    )
    (run_path / "events.jsonl").write_text("", encoding="utf-8")
    (run_path / "decisions.jsonl").write_text("", encoding="utf-8")
    append_event(run_path, {"ts": now, "event": "run_created", "run_id": run_id})
    return RunRef(run_id=run_id, path=run_path)

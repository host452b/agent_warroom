import json
from pathlib import Path


def write_artifact(run_path: Path, key: str, content: str, relative_path: str) -> None:
    path = run_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    state_path = run_path / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    artifacts = state.setdefault("artifacts", {})
    artifacts[key] = relative_path
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def read_artifact(run_path: Path, relative_path: str) -> str:
    return (run_path / relative_path).read_text(encoding="utf-8")

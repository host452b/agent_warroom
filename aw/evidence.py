import json
from pathlib import Path


def record_command(run_path: Path, command: str, status: str, output: str, ts: str) -> None:
    evidence_dir = run_path / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    output_path = evidence_dir / "last-command-output.txt"
    output_path.write_text(output, encoding="utf-8")
    entry = {
        "ts": ts,
        "kind": "command",
        "command": command,
        "status": status,
        "output": "evidence/last-command-output.txt",
    }
    with (evidence_dir / "commands.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

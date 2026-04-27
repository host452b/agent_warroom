import json

from aw.evidence import record_command
from aw.runs import create_run


def test_record_command_appends_evidence(tmp_path):
    run = create_run(tmp_path, "build notes", "2026-04-27T15:30:00+08:00")

    record_command(
        run.path,
        "pytest -q",
        "passed",
        "ok",
        "2026-04-27T15:31:00+08:00",
    )

    lines = (run.path / "evidence" / "commands.jsonl").read_text().splitlines()
    assert json.loads(lines[0])["command"] == "pytest -q"
    assert json.loads(lines[0])["status"] == "passed"

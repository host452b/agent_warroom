from aw.artifacts import write_artifact
from aw.runs import create_run


def test_write_artifact_updates_state(tmp_path):
    run = create_run(tmp_path, "build notes", "2026-04-27T15:30:00+08:00")

    write_artifact(run.path, "spec", "# Spec\n", "artifacts/spec.md")

    assert (run.path / "artifacts" / "spec.md").read_text() == "# Spec\n"
    assert "spec" in (run.path / "state.json").read_text()

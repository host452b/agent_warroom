from aw.runs import create_run


def test_create_run_writes_manifest_state_and_requirement(tmp_path):
    run = create_run(
        runs_dir=tmp_path,
        requirement="build a local-first note taking CLI",
        now="2026-04-27T15:30:00+08:00",
    )

    assert run.run_id.startswith("run-20260427-153000")
    assert (run.path / "run-manifest.json").exists()
    assert (run.path / "state.json").exists()
    assert (run.path / "events.jsonl").exists()
    assert (
        run.path / "artifacts" / "requirement.md"
    ).read_text() == "build a local-first note taking CLI\n"

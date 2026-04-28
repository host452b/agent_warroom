from pathlib import Path

from typer.testing import CliRunner

from aw.cli import app
from aw.runs import create_run


def test_start_creates_requirement_scoring_and_spec(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "start",
            "build a local-first note taking CLI",
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:30:00+08:00",
        ],
    )

    assert result.exit_code == 0
    assert "Started run-20260427-153000" in result.output

    run_path = tmp_path / "run-20260427-153000"
    assert (run_path / "artifacts" / "requirement.md").exists()
    assert (run_path / "artifacts" / "brainstorm-option-matrix.md").exists()
    assert (run_path / "artifacts" / "spec.md").exists()
    assert "spec_approved" in (run_path / "state.json").read_text()
    assert "select_product_direction" in (run_path / "decisions.jsonl").read_text()


def test_interactive_shell_creates_run_from_natural_language():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            [],
            input="build notes\nstatus\nshow spec\nexit\n",
        )

    assert result.exit_code == 0
    assert "Started run-" in result.output
    assert "Phase: spec" in result.output
    assert "# Spec" in result.output


def test_interactive_shell_prints_help_without_creating_run():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(app, [], input="help\nexit\n")

    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "record-evidence <command>" in result.output
    assert "Started run-" not in result.output


def test_interactive_shell_resumes_existing_run():
    runner = CliRunner()

    with runner.isolated_filesystem():
        run = create_run(Path("runs"), "build notes", "2026-04-27T15:30:00+08:00")
        result = runner.invoke(
            app,
            [],
            input=f"resume {run.run_id}\nstatus\nshow spec\nexit\n",
        )

    assert result.exit_code == 0
    assert f"Resumed {run.run_id}" in result.output
    assert "Phase: spec" in result.output
    assert "# Spec" in result.output


def test_runs_command_lists_existing_runs(tmp_path):
    create_run(tmp_path, "build notes", "2026-04-27T15:30:00+08:00")
    create_run(tmp_path, "build tasks", "2026-04-27T15:31:00+08:00")

    result = CliRunner().invoke(app, ["runs", "--runs-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "run-20260427-153000" in result.output
    assert "build notes" in result.output
    assert "run-20260427-153100" in result.output
    assert "build tasks" in result.output


def test_interactive_shell_lists_existing_runs():
    runner = CliRunner()

    with runner.isolated_filesystem():
        create_run(Path("runs"), "build notes", "2026-04-27T15:30:00+08:00")
        result = runner.invoke(app, [], input="runs\nexit\n")

    assert result.exit_code == 0
    assert "run-20260427-153000" in result.output
    assert "build notes" in result.output


def test_interactive_shell_records_command_evidence():
    runner = CliRunner()

    with runner.isolated_filesystem():
        run = create_run(Path("runs"), "build notes", "2026-04-27T15:30:00+08:00")
        result = runner.invoke(
            app,
            [],
            input=f"resume {run.run_id}\nrecord-evidence pytest -q\nevidence\nexit\n",
        )

    assert result.exit_code == 0
    assert f"Recorded evidence for {run.run_id}" in result.output
    assert "passed: pytest -q" in result.output


def test_show_spec_prints_spec_artifact(tmp_path):
    run_id = "run-20260427-153000"
    CliRunner().invoke(
        app,
        [
            "start",
            "build notes",
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:30:00+08:00",
        ],
    )

    result = CliRunner().invoke(app, ["show", "spec", run_id, "--runs-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "# Spec" in result.output
    assert "build notes" in result.output


def test_write_plan_creates_scoring_and_plan_artifacts(tmp_path):
    run_id = "run-20260427-153000"
    runner = CliRunner()
    runner.invoke(
        app,
        [
            "start",
            "build notes",
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:30:00+08:00",
        ],
    )

    result = runner.invoke(
        app,
        [
            "write",
            "plan",
            run_id,
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:31:00+08:00",
        ],
    )

    assert result.exit_code == 0
    run_path = tmp_path / run_id
    assert (run_path / "artifacts" / "plan-option-matrix.md").exists()
    assert (run_path / "artifacts" / "plan.md").exists()
    assert "plan_approved" in (run_path / "state.json").read_text()


def test_approve_records_gate_evidence(tmp_path):
    run_id = "run-20260427-153000"
    runner = CliRunner()
    runner.invoke(
        app,
        [
            "start",
            "build notes",
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:30:00+08:00",
        ],
    )

    result = runner.invoke(
        app,
        [
            "approve",
            run_id,
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:31:00+08:00",
        ],
    )

    assert result.exit_code == 0
    run_path = tmp_path / run_id
    assert "Approved spec_approved" in result.output
    assert "spec_approved" in (run_path / "evidence" / "approvals.jsonl").read_text()
    assert '"status": "passed"' in (run_path / "state.json").read_text()

    evidence = runner.invoke(app, ["evidence", run_id, "--runs-dir", str(tmp_path)])

    assert evidence.exit_code == 0
    assert "approval: spec_approved" in evidence.output


def test_record_evidence_updates_evidence_output(tmp_path):
    run_id = "run-20260427-153000"
    runner = CliRunner()
    runner.invoke(
        app,
        [
            "start",
            "build notes",
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:30:00+08:00",
        ],
    )

    result = runner.invoke(
        app,
        [
            "record-evidence",
            run_id,
            "pytest -q",
            "--status",
            "passed",
            "--output",
            "7 passed",
            "--runs-dir",
            str(tmp_path),
            "--now",
            "2026-04-27T15:32:00+08:00",
        ],
    )

    assert result.exit_code == 0
    evidence = runner.invoke(app, ["evidence", run_id, "--runs-dir", str(tmp_path)])

    assert evidence.exit_code == 0
    assert "pytest -q" in evidence.output
    assert "passed" in evidence.output

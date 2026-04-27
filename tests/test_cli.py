import subprocess
import sys

from typer.testing import CliRunner

from aw.cli import app
from aw.runs import create_run


def test_help_displays_aw_commands():
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "status" in result.output
    assert "resume" in result.output


def test_module_help_displays_aw_commands():
    result = subprocess.run(
        [sys.executable, "-m", "aw.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "status" in result.stdout
    assert "resume" in result.stdout


def test_status_shows_current_phase_and_gate(tmp_path):
    run = create_run(tmp_path, "build notes", "2026-04-27T15:30:00+08:00")

    result = CliRunner().invoke(app, ["status", run.run_id, "--runs-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "brainstorm" in result.output
    assert "option_scoring_done" in result.output


def test_resume_shows_restored_run(tmp_path):
    run = create_run(tmp_path, "build notes", "2026-04-27T15:30:00+08:00")

    result = CliRunner().invoke(app, ["resume", run.run_id, "--runs-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert f"Resumed {run.run_id}" in result.output

from typer.testing import CliRunner

from aw.cli import app


def test_help_displays_aw_commands():
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "status" in result.output
    assert "resume" in result.output

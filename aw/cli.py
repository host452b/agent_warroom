from pathlib import Path

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def status(run_id: str | None = None, runs_dir: Path = Path("runs")) -> None:
    """Show current run status."""
    typer.echo("No runs yet")


@app.command()
def resume(run_id: str, runs_dir: Path = Path("runs")) -> None:
    """Resume an existing run."""
    typer.echo(f"Resuming {run_id}")


def main() -> None:
    app()

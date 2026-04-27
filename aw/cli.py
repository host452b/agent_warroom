from pathlib import Path

import typer

from aw.runs import load_state

app = typer.Typer(no_args_is_help=True)


@app.command()
def status(
    run_id: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
) -> None:
    """Show current run status."""
    state = load_state(runs_dir, run_id)
    typer.echo(f"Run: {state['run_id']}")
    typer.echo(f"Phase: {state['current_phase']}")
    typer.echo(f"Gate: {state['current_gate']}")


@app.command()
def resume(
    run_id: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
) -> None:
    """Resume an existing run."""
    state = load_state(runs_dir, run_id)
    typer.echo(f"Resumed {state['run_id']}")
    typer.echo(f"Phase: {state['current_phase']}")


def main() -> None:
    app()

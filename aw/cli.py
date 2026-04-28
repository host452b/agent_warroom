from pathlib import Path
from datetime import datetime
import json

import typer

from aw.artifacts import read_artifact
from aw.evidence import record_command
from aw.runs import approve_gate, create_run, load_state, write_plan_artifacts

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)
show_app = typer.Typer()
write_app = typer.Typer()
app.add_typer(show_app, name="show")
app.add_typer(write_app, name="write")


def _now(now: str | None) -> str:
    return now or datetime.now().astimezone().isoformat(timespec="seconds")


def _gate_label(gate: object) -> str:
    if isinstance(gate, dict):
        return str(gate.get("gate_id", "unknown"))
    return str(gate)


def _run_path(runs_dir: Path, run_id: str) -> Path:
    return runs_dir / run_id


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """Start the interactive shell when no command is supplied."""
    if ctx.invoked_subcommand is None:
        run_shell()


def run_shell(runs_dir: Path = Path("runs")) -> None:
    current_run_id: str | None = None
    typer.echo("aw interactive shell. Type a requirement or `exit`.")
    while True:
        try:
            line = typer.prompt("aw").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo()
            return
        if not line:
            continue
        if line == "exit":
            typer.echo("Bye")
            return
        if line == "status":
            if current_run_id:
                status(current_run_id, runs_dir)
            else:
                typer.echo("No active run")
            continue
        if line.startswith("resume "):
            run_id = line.split(maxsplit=1)[1].strip()
            state = load_state(runs_dir, run_id)
            current_run_id = state["run_id"]
            typer.echo(f"Resumed {state['run_id']}")
            typer.echo(f"Phase: {state['current_phase']}")
            continue
        if line == "show spec":
            if current_run_id:
                show_spec(current_run_id, runs_dir)
            else:
                typer.echo("No active run")
            continue
        if line == "show plan":
            if current_run_id:
                show_plan(current_run_id, runs_dir)
            else:
                typer.echo("No active run")
            continue
        if line == "write plan":
            if current_run_id:
                write_plan(current_run_id, runs_dir)
            else:
                typer.echo("No active run")
            continue
        if line == "approve":
            if current_run_id:
                approve(current_run_id, runs_dir)
            else:
                typer.echo("No active run")
            continue
        if line == "evidence":
            if current_run_id:
                evidence(current_run_id, runs_dir)
            else:
                typer.echo("No active run")
            continue

        run = create_run(runs_dir, line, _now(None))
        current_run_id = run.run_id
        typer.echo(f"Started {run.run_id}")
        typer.echo("Next: review spec, then run `approve`.")


@app.command()
def start(
    requirement: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
    now: str | None = typer.Option(None, "--now"),
) -> None:
    """Start a P0 workflow run."""
    run = create_run(runs_dir, requirement, _now(now))
    typer.echo(f"Started {run.run_id}")
    typer.echo("Next: review spec, then run `approve`.")


@app.command()
def status(
    run_id: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
) -> None:
    """Show current run status."""
    state = load_state(runs_dir, run_id)
    typer.echo(f"Run: {state['run_id']}")
    typer.echo(f"Phase: {state['current_phase']}")
    typer.echo(f"Gate: {_gate_label(state['current_gate'])}")
    if isinstance(state["current_gate"], dict):
        missing = state["current_gate"].get("missing", [])
        if missing:
            typer.echo(f"Missing: {', '.join(missing)}")


@app.command()
def resume(
    run_id: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
) -> None:
    """Resume an existing run."""
    state = load_state(runs_dir, run_id)
    typer.echo(f"Resumed {state['run_id']}")
    typer.echo(f"Phase: {state['current_phase']}")


@show_app.command("spec")
def show_spec(run_id: str, runs_dir: Path = typer.Option(Path("runs"), "--runs-dir")) -> None:
    """Show the current spec artifact."""
    state = load_state(runs_dir, run_id)
    typer.echo(read_artifact(_run_path(runs_dir, run_id), state["artifacts"]["spec"]))


@show_app.command("plan")
def show_plan(run_id: str, runs_dir: Path = typer.Option(Path("runs"), "--runs-dir")) -> None:
    """Show the current plan artifact."""
    state = load_state(runs_dir, run_id)
    typer.echo(read_artifact(_run_path(runs_dir, run_id), state["artifacts"]["plan"]))


@app.command()
def approve(
    run_id: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
    now: str | None = typer.Option(None, "--now"),
) -> None:
    """Approve the current user gate."""
    state = approve_gate(runs_dir, run_id, _now(now))
    typer.echo(f"Approved {_gate_label(state['current_gate'])}")


@write_app.command("plan")
def write_plan(
    run_id: str,
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
    now: str | None = typer.Option(None, "--now"),
) -> None:
    """Write plan scoring and implementation plan artifacts."""
    write_plan_artifacts(runs_dir, run_id, _now(now))
    typer.echo(f"Wrote plan for {run_id}")


@app.command("record-evidence")
def record_evidence(
    run_id: str,
    command: str,
    status: str = typer.Option("passed", "--status"),
    output: str = typer.Option("", "--output"),
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
    now: str | None = typer.Option(None, "--now"),
) -> None:
    """Record one command evidence entry."""
    record_command(_run_path(runs_dir, run_id), command, status, output, _now(now))
    typer.echo(f"Recorded evidence for {run_id}")


@app.command()
def evidence(run_id: str, runs_dir: Path = typer.Option(Path("runs"), "--runs-dir")) -> None:
    """Show recorded evidence."""
    evidence_dir = _run_path(runs_dir, run_id) / "evidence"
    printed = False

    approvals_path = evidence_dir / "approvals.jsonl"
    if approvals_path.exists():
        for line in approvals_path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            typer.echo(f"approval: {entry['gate']}")
            printed = True

    commands_path = evidence_dir / "commands.jsonl"
    if commands_path.exists():
        for line in commands_path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            typer.echo(f"{entry['status']}: {entry['command']}")
            printed = True

    if not printed:
        typer.echo("No evidence recorded")
        return


def main() -> None:
    app()


if __name__ == "__main__":
    main()

"""Typer CLI: chat, extract, temp-study, serve."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml

from assistant.chat import run_turn
from assistant.client import format_metrics
from assistant.extract import extract_job, validity_summary
from assistant.schemas import ExtractSuccess
from assistant.temp_study import format_study_table, run_temperature_study

app = typer.Typer(
    name="assistant",
    help="Offline local LLM assistant (Ollama).",
    add_completion=False,
    invoke_without_command=True,
)

ROOT = Path(__file__).resolve().parents[2]
MODELS_YAML = ROOT / "configs" / "models.yaml"


def load_default_model() -> str:
    data = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))
    return str(data["default_model"])


@app.callback()
def main(ctx: typer.Context) -> None:
    """Show help when no subcommand is given."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def chat(
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Ollama model tag (default from configs/models.yaml).",
    ),
    temperature: float = typer.Option(0.7, "--temperature", "-t"),
) -> None:
    """
    Interactive chat in the terminal.

    Type a message and press Enter. Type /exit or /quit to leave.
    Metrics print after every reply.
    """
    chosen = model or load_default_model()
    typer.echo(f"Model: {chosen}")
    typer.echo("Chat is ready. Type /exit to quit.\n")

    history: list[dict[str, str]] = []

    while True:
        try:
            user_text = typer.prompt("you")
        except typer.Abort:
            typer.echo("\nBye.")
            raise typer.Exit(0) from None

        stripped = user_text.strip()
        if not stripped:
            continue
        if stripped.lower() in {"/exit", "/quit", "exit", "quit"}:
            typer.echo("Bye.")
            raise typer.Exit(0)

        def on_token(token: str) -> None:
            typer.echo(token, nl=False)

        typer.echo("assistant: ", nl=False)
        result = run_turn(
            stripped,
            history,
            chosen,
            temperature=temperature,
            on_token=on_token,
        )
        typer.echo(format_metrics(result.metrics))
        typer.echo()


@app.command()
def extract(
    job_file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to a job posting text file. If omitted, read until a line: END",
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    temperature: float = typer.Option(0.0, "--temperature", "-t"),
) -> None:
    """Extract a JobPosting JSON from a messy job description."""
    chosen = model or load_default_model()

    if job_file is not None:
        text = job_file.read_text(encoding="utf-8")
    else:
        typer.echo("Paste the job posting. End with a line that is only: END")
        lines: list[str] = []
        while True:
            line = typer.prompt("", prompt_suffix="")
            if line.strip() == "END":
                break
            lines.append(line)
        text = "\n".join(lines)

    if not text.strip():
        typer.echo("No job text provided.", err=True)
        raise typer.Exit(1)

    typer.echo(f"Model: {chosen}  temperature={temperature}")
    result = extract_job(text, chosen, temperature=temperature)
    typer.echo(json.dumps(result.model_dump(), indent=2))
    if isinstance(result, ExtractSuccess):
        typer.echo(
            f"\nvalid_first_try={result.valid_first_try}  attempts={result.attempts}"
        )
    summary = validity_summary()
    typer.echo(f"\nlog summary: {summary}")


@app.command("temp-study")
def temp_study(
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    runs: int = typer.Option(5, "--runs", help="Runs per job per temperature."),
) -> None:
    """
    Run the temperature variance study (Phase 2).

    Same sample jobs × N runs at temperature 0.0 and 0.7.
    Writes reports/temperature_study.json and prints the summary table.
    """
    typer.echo("Running temperature study (this can take a few minutes)...")
    report = run_temperature_study(model=model, runs_per_temp=runs)
    typer.echo(format_study_table(report))
    typer.echo("\nFull report: reports/temperature_study.json")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    """Start the FastAPI server (POST /chat and POST /extract)."""
    import uvicorn

    typer.echo(f"Serving on http://{host}:{port}")
    typer.echo("If port is busy, try: uv run assistant serve --port 8001")
    uvicorn.run("assistant.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()

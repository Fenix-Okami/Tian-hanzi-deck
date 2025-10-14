"""Validation commands for deck sanity checks."""
from __future__ import annotations

import typer

__all__ = ["app"]

app = typer.Typer(help="Run validation routines against generated decks.")


@app.command()
def smoke() -> None:
    """Placeholder smoke check until validation suite is migrated to pytest."""
    typer.secho(
        "Validation suite is under migration. Refer to scripts/validation for legacy checks.",
        fg=typer.colors.YELLOW,
    )

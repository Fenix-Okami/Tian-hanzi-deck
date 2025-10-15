"""Analytics commands wrapping reporting utilities."""
from __future__ import annotations

from pathlib import Path

import typer

__all__ = ["app"]

app = typer.Typer(help="Analysis utilities for Tian Hanzi datasets.")


@app.command()
def distribution(
    data_dir: Path = typer.Option(Path("data"), help="Directory containing generated artefacts"),
) -> None:
    """Placeholder distribution report until legacy scripts are migrated."""
    typer.secho(
        "Distribution analysis has not yet been ported. Run scripts/analysis/analyze_level_breakpoints.py",
        fg=typer.colors.YELLOW,
    )

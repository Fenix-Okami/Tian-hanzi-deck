"""Deck-related Typer commands."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import typer

from ..core.deck_pipeline import DeckBuildConfig, DeckBuilder

__all__ = ["app"]

app = typer.Typer(help="Build and manage Tian Hanzi decks.")


@app.command()
def build(
    level: Iterable[int] = typer.Option(
        (1, 2, 3),
        "--level",
        "-l",
        help="HSK levels to include",
        show_default=True,
    ),
    hsk_data_dir: Path = typer.Option(
        Path("data/HSK-3.0"),
        "--hsk-data-dir",
        help="Directory containing raw HSK files",
    ),
    output_dir: Path = typer.Option(Path("data"), "--output-dir", help="Destination for generated artefacts"),
) -> None:
    """Generate deck artefacts for the provided HSK ``level`` selection."""
    config = DeckBuildConfig(hsk_levels=tuple(level), hsk_data_dir=str(hsk_data_dir), output_dir=str(output_dir))
    builder = DeckBuilder(config)
    try:
        builder.build()
    except RuntimeError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

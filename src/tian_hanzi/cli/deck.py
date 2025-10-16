"""Deck-related Typer commands."""
from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from ..core.deck_pipeline import DeckBuildConfig, DeckBuilder
from ..core.samples import SampleGenerator

__all__ = ["app"]

app = typer.Typer(help="Build and manage Tian Hanzi decks.")


@app.command()
def build(
    level: List[int] = typer.Option(
        [1, 2, 3],
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
    skip_samples: bool = typer.Option(False, "--skip-samples", help="Skip generating sample HTML previews"),
) -> None:
    """Generate deck artefacts for the provided HSK ``level`` selection."""
    config = DeckBuildConfig(hsk_levels=tuple(level), hsk_data_dir=str(hsk_data_dir), output_dir=str(output_dir))
    builder = DeckBuilder(config)
    try:
        builder.build()
        
        # Automatically generate samples unless skipped
        if not skip_samples:
            _generate_samples(output_dir)
    except RuntimeError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


def _generate_samples(output_dir: Path) -> None:
    """Generate sample CSV and HTML files from the built deck data."""
    import pandas as pd
    
    try:
        # Load the generated CSV files
        radicals_df = pd.read_csv(output_dir / "radicals.csv")
        hanzi_df = pd.read_csv(output_dir / "hanzi.csv")
        vocabulary_df = pd.read_csv(output_dir / "vocabulary.csv")
        
        # Generate samples
        generator = SampleGenerator(output_dir=output_dir)
        generator.generate(radicals_df, hanzi_df, vocabulary_df)
    except FileNotFoundError as exc:
        typer.secho(f"⚠️  Could not generate samples: {exc}", fg=typer.colors.YELLOW)
    except Exception as exc:
        typer.secho(f"⚠️  Error generating samples: {exc}", fg=typer.colors.YELLOW)

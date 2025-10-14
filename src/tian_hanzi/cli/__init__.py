"""Public CLI surface for the Tian Hanzi toolkit."""
from __future__ import annotations

import typer

from . import analytics, deck, validate

__all__ = ["app", "main"]

app = typer.Typer(help="Tian Hanzi command line interface")
app.add_typer(deck.app, name="deck")
app.add_typer(analytics.app, name="analyze")
app.add_typer(validate.app, name="validate")


def main() -> None:
    app()

"""Tian Hanzi Deck - Core package exports."""
from __future__ import annotations

from .cli import app as cli_app
from .core.deck_pipeline import DeckBuildConfig, DeckBuilder
from .data_generator import HSKDeckBuilder

__all__ = [
    "HSKDeckBuilder",
    "DeckBuilder",
    "DeckBuildConfig",
    "cli_app",
]

__version__ = "2.1.0"

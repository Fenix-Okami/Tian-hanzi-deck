"""Backward compatible facade exposing the deck build pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .core.deck_pipeline import DeckBuildConfig, DeckBuilder

__all__ = ["HSKDeckBuilder", "DeckBuildConfig", "DeckBuilder"]


@dataclass
class HSKDeckBuilder:
    """Compatibility wrapper delegating to :class:`DeckBuilder`."""

    hsk_levels: Sequence[int] = (1, 2, 3)
    hsk_data_dir: str = "data/HSK-3.0"
    output_dir: str = "data"

    def build(self) -> dict[str, list[dict]]:
        builder = DeckBuilder(
            DeckBuildConfig(hsk_levels=tuple(self.hsk_levels), hsk_data_dir=self.hsk_data_dir, output_dir=self.output_dir)
        )
        return builder.build()

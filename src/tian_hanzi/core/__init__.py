"""Core modules powering the Tian Hanzi deck pipeline."""
from __future__ import annotations

from .cards import clean_surname_from_definition, create_ruby_text, format_components_with_meanings
from .deck_pipeline import DeckBuildConfig, DeckBuilder
from .pinyin import numbered_to_accented
from .storage import ParquetDataManager

__all__ = [
    "clean_surname_from_definition",
    "create_ruby_text",
    "format_components_with_meanings",
    "DeckBuildConfig",
    "DeckBuilder",
    "numbered_to_accented",
    "ParquetDataManager",
]

"""Legacy utility namespace maintained for backwards compatibility."""
from __future__ import annotations

from ..core.cards import create_ruby_text, format_components_with_meanings
from ..core.pinyin import numbered_to_accented

__all__ = [
    "numbered_to_accented",
    "create_ruby_text",
    "format_components_with_meanings",
]

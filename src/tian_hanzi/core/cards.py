"""Utilities for building Hanzi deck card content."""
from __future__ import annotations

from typing import Iterable

import pandas as pd

__all__ = [
    "clean_surname_from_definition",
    "create_ruby_text",
    "format_components_with_meanings",
]


def clean_surname_from_definition(definition: str | None) -> tuple[str, bool]:
    """Remove surname references from a dictionary definition string."""
    if not definition:
        return "", False

    is_surname = False
    parts: list[str] = []
    for part in definition.split(";"):
        candidate = part.strip()
        if not candidate:
            continue
        lower = candidate.lower()
        if lower.startswith("surname "):
            is_surname = True
            continue
        if "surname " in lower:
            is_surname = True
            subparts = [sub.strip() for sub in candidate.split("/") if sub.strip()]
            filtered = [sub for sub in subparts if not sub.lower().startswith("surname ")]
            if filtered:
                parts.append("/".join(filtered))
            continue
        parts.append(candidate)

    cleaned = "; ".join(parts).strip()
    return cleaned, is_surname


def create_ruby_text(word: str, pinyin: str) -> str:
    """Create HTML ruby markup for the supplied ``word`` and ``pinyin`` pair."""
    if not word or not pinyin:
        return word

    syllables = pinyin.strip().split()
    chars = list(word)
    if len(syllables) == len(chars):
        ruby_parts = [
            (
                f'<ruby><rb class="vocab-char">{char}</rb>'
                f'<rt class="pinyin-reading">{syllable}</rt></ruby>'
            )
            for char, syllable in zip(chars, syllables)
        ]
        return "".join(ruby_parts)

    return (
        f'<ruby><rb class="vocab-word">{word}</rb>'
        f'<rt class="pinyin-reading">{pinyin}</rt></ruby>'
    )


def _split_components(value: str | Iterable[str]) -> list[str]:
    """Split the stored component representation into individual entries."""
    if value is None:
        return []

    try:
        if pd.isna(value):  # type: ignore[arg-type]
            return []
    except TypeError:
        # Non-numeric iterables (like lists) fall through below.
        pass

    if isinstance(value, str):
        if "|" in value:
            return [item.strip() for item in value.split("|") if item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    try:
        return [item for item in value if item]
    except TypeError:
        # Value is not iterable (e.g., an int); fall back to string conversion.
        return [str(value)] if value else []


def format_components_with_meanings(
    components: str | Iterable[str], radicals_df: pd.DataFrame
) -> str:
    """Format component strings along with their meanings from ``radicals_df``."""
    split = _split_components(components)
    if not split:
        return "No components"

    formatted: list[str] = []
    for component in split:
        match = radicals_df[radicals_df["radical"] == component]
        if match.empty:
            formatted.append(component)
            continue
        meaning = match.iloc[0].get("meaning", "")
        if meaning and len(meaning) > 30:
            meaning = meaning[:27] + "..."
        formatted.append(f"{component} ({meaning})" if meaning else component)

    return ", ".join(formatted) if formatted else "No components"

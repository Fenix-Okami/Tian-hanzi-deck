"""Utilities for converting between pinyin representations."""
from __future__ import annotations

__all__ = ["numbered_to_accented"]

_TONE_MARKS = {
    "a": ["a", "ā", "á", "ǎ", "à"],
    "e": ["e", "ē", "é", "ě", "è"],
    "i": ["i", "ī", "í", "ǐ", "ì"],
    "o": ["o", "ō", "ó", "ǒ", "ò"],
    "u": ["u", "ū", "ú", "ǔ", "ù"],
    "ü": ["ü", "ǖ", "ǘ", "ǚ", "ǜ"],
    "A": ["A", "Ā", "Á", "Ǎ", "À"],
    "E": ["E", "Ē", "É", "Ě", "È"],
    "I": ["I", "Ī", "Í", "Ǐ", "Ì"],
    "O": ["O", "Ō", "Ó", "Ǒ", "Ò"],
    "U": ["U", "Ū", "Ú", "Ǔ", "Ù"],
    "Ü": ["Ü", "Ǖ", "Ǘ", "Ǚ", "Ǜ"],
}


def numbered_to_accented(pinyin: str | None) -> str | None:
    """Convert numbered tone markers (``ma3``) to accented syllables (``mǎ``)."""
    if not pinyin:
        return pinyin

    converted: list[str] = []
    for syllable in pinyin.split():
        if not syllable:
            continue
        tone_char = syllable[-1]
        tone = int(tone_char) if tone_char.isdigit() else None
        base = syllable[:-1] if tone is not None else syllable

        if tone is None or tone in (0, 5):
            converted.append(base)
            continue

        chars = list(base.replace("v", "ü").replace("V", "Ü"))
        index = _tone_index(chars)
        if index is None:
            converted.append(base)
            continue
        letter = chars[index]
        replacement = _TONE_MARKS.get(letter, [])
        if tone < len(replacement):
            chars[index] = replacement[tone]
        converted.append("".join(chars))

    return " ".join(converted)


def _tone_index(chars: list[str]) -> int | None:
    for idx, char in enumerate(chars):
        if char.lower() in {"a", "e"}:
            return idx
    for idx, char in enumerate(chars):
        if char.lower() == "o":
            return idx
    for idx in range(len(chars) - 1, -1, -1):
        if chars[idx].lower() in {"i", "u", "ü"}:
            return idx
    return None

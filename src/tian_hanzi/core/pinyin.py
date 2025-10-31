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
    for original_syllable in pinyin.split():
        if not original_syllable:
            continue
        tone_char = original_syllable[-1]
        tone = int(tone_char) if tone_char.isdigit() else None
        base = original_syllable[:-1] if tone is not None else original_syllable

        style = _detect_case_style(base)
        working = base.lower()

        if tone is None or tone in (0, 5):
            converted.append(_apply_case_style(working, style))
            continue

        chars = list(working.replace("v", "ü"))
        index = _tone_index(chars)
        if index is None:
            converted.append(_apply_case_style(working, style))
            continue
        letter = chars[index]
        replacement = _TONE_MARKS.get(letter, [])
        if tone < len(replacement):
            chars[index] = replacement[tone]
        accented = "".join(chars)
        converted.append(_apply_case_style(accented, style))

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


def _detect_case_style(text: str) -> str:
    if not text:
        return "lower"
    if text.isupper():
        return "upper"
    if text[0].isupper() and text[1:].islower():
        return "capitalized"
    return "lower"


def _apply_case_style(text: str, style: str) -> str:
    if not text:
        return text
    if style == "upper":
        return text.upper()
    if style == "capitalized":
        return text[0].upper() + text[1:]
    return text

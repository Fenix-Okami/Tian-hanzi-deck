"""Data loading helpers for the Tian Hanzi deck pipeline."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable, List

from .cards import clean_surname_from_definition
from .pinyin import numbered_to_accented

__all__ = ["HSKDataRepository"]


class HSKDataRepository:
    """Provide access to the raw HSK data assets used by the deck build."""

    def __init__(self, hsk_data_dir: str | Path) -> None:
        self.hsk_dir = Path(hsk_data_dir)
        self.frequency_dir = self.hsk_dir / "HSK List (Frequency)"
        self.hanzi_dir = self.hsk_dir / "HSK Hanzi"

    def load_vocabulary(
        self,
        levels: Iterable[int],
        dictionary,
    ) -> list[dict]:
        """Return vocabulary rows for the provided ``levels``."""
        entries: list[dict] = []
        for level in levels:
            file_path = self.frequency_dir / f"HSK {level}.txt"
            if not file_path.exists():
                continue
            words = _read_lines(file_path)
            for position, word in enumerate(words, start=1):
                pinyin, meaning, is_surname = self._dictionary_lookup(dictionary, word)
                entries.append(
                    {
                        "word": word,
                        "hsk_level": level,
                        "frequency_position": position,
                        "pinyin": pinyin,
                        "meaning": meaning,
                        "is_surname": is_surname,
                    }
                )
        return entries

    def load_hanzi_levels(self, levels: Iterable[int]) -> dict[str, int]:
        """Map hanzi characters to their first observed HSK level."""
        mapping: dict[str, int] = {}
        for level in levels:
            file_path = self.hanzi_dir / f"HSK {level}.txt"
            if not file_path.exists():
                continue
            for char in _read_lines(file_path):
                mapping.setdefault(char, level)
        return mapping

    @staticmethod
    def extract_hanzi_from_vocabulary(vocabulary: Iterable[dict]) -> set[str]:
        """Collect the set of unique hanzi used across ``vocabulary`` rows."""
        characters: set[str] = set()
        for vocab in vocabulary:
            for char in vocab["word"]:
                if "\u4e00" <= char <= "\u9fff":
                    characters.add(char)
        return characters

    @staticmethod
    def _dictionary_lookup(dictionary, term: str) -> tuple[str, str, bool]:
        try:
            definitions = dictionary.definition_lookup(term)
        except Exception:
            return "", "", False
        if not definitions:
            return "", "", False
        pinyin = numbered_to_accented(definitions[0].get("pinyin", ""))
        combined = "; ".join(
            entry.get("definition", "") for entry in definitions if entry.get("definition")
        )
        meaning, is_surname = clean_surname_from_definition(combined)
        return pinyin, meaning, is_surname

    @staticmethod
    def build_component_counters(
        hanzi_data: dict[str, dict],
        hanzi_to_hsk: dict[str, int],
    ) -> tuple[Counter, dict[int, Counter]]:
        component_usage: Counter = Counter()
        by_level: dict[int, Counter] = {1: Counter(), 2: Counter(), 3: Counter()}
        for char, data in hanzi_data.items():
            level = hanzi_to_hsk.get(char)
            for component in data.get("components", []):
                component_usage[component] += 1
                if level in by_level:
                    by_level[level][component] += 1
        return component_usage, by_level


def _read_lines(file_path: Path) -> list[str]:
    with file_path.open("r", encoding="utf-8-sig") as handle:
        return [line.strip() for line in handle if line.strip()]

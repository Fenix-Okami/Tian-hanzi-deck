"""Core pipeline for generating HSK deck artefacts.

This module builds three tabular datasets (vocabulary, hanzi, radicals)
from the raw HSK 3.0 sources.  The output is saved to CSV (and optionally
Parquet) so that downstream scripts – including the Anki deck creator and
HTML preview generator – can operate on consistent artefacts.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence

import pandas as pd

from .components import ComponentAnalyzer
from .data_sources import HSKDataRepository
from .storage import ParquetDataManager

__all__ = ["DeckBuildConfig", "DeckBuilder"]


@dataclass(frozen=True)
class DeckBuildConfig:
    """Configuration parameters for :class:`DeckBuilder`."""

    hsk_levels: Sequence[int] = (1, 2, 3)
    hsk_data_dir: str = "data/HSK-3.0"
    output_dir: str = "data"
    save_csv: bool = True
    save_parquet: bool = True


class DeckBuilder:
    """Generate HSK deck artefacts from raw input files.

    Parameters can be customised by injecting alternative dictionary,
    decomposer, or storage implementations.  This is especially useful in
    tests where deterministic fixtures are required.
    """

    def __init__(
        self,
        config: DeckBuildConfig,
        *,
        dictionary: Optional[object] = None,
        decomposer: Optional[object] = None,
        stroke_counter: Optional[Callable[[str], int]] = None,
        repository: Optional[HSKDataRepository] = None,
        storage: Optional[ParquetDataManager] = None,
    ) -> None:
        self.config = DeckBuildConfig(  # ensure we store immutable copy
            hsk_levels=tuple(config.hsk_levels),
            hsk_data_dir=config.hsk_data_dir,
            output_dir=config.output_dir,
            save_csv=config.save_csv,
            save_parquet=config.save_parquet,
        )

        base_dir = Path(self.config.hsk_data_dir)
        self.dictionary = dictionary or _HSKDictionary(base_dir)
        self.decomposer = decomposer or _create_default_decomposer()
        self.stroke_counter = stroke_counter or _create_default_stroke_counter()
        if self.stroke_counter is None:
            self.stroke_counter = _fallback_stroke_counter

        self.repository = repository or HSKDataRepository(base_dir)
        self.storage = storage or ParquetDataManager(self.config.output_dir)
        self.component_analyzer = ComponentAnalyzer(self.decomposer, self.dictionary)

    # ------------------------------------------------------------------
    def build(self) -> dict[str, list[dict]]:
        """Execute the deck pipeline, returning generated artefacts."""

        levels = tuple(int(level) for level in self.config.hsk_levels)

        vocabulary_rows = self.repository.load_vocabulary(levels, self.dictionary)
        hanzi_level_map = self.repository.load_hanzi_levels(levels)

        if not hanzi_level_map:
            hanzi_level_map = {}

        # Ensure every character appearing in vocabulary has a level mapping
        for vocab in vocabulary_rows:
            level = int(vocab.get("hsk_level", 0) or 0)
            for char in vocab.get("word", ""):
                if "\u4e00" <= char <= "\u9fff" and char not in hanzi_level_map:
                    if level:
                        hanzi_level_map[char] = level

        unique_hanzi = self.repository.extract_hanzi_from_vocabulary(vocabulary_rows)
        hanzi_meta, component_stats = self.component_analyzer.analyse(unique_hanzi, hanzi_level_map)

        radicals = self._build_radicals(component_stats.details)
        hanzi = self._build_hanzi(hanzi_meta, hanzi_level_map)
        vocabulary = self._build_vocabulary(vocabulary_rows)

        exports = {
            "components": radicals,
            "radicals": radicals,  # alias kept for backwards compatibility
            "hanzi": hanzi,
            "vocabulary": vocabulary,
        }

        if self.config.save_csv:
            self._save_csv(radicals, hanzi, vocabulary)
        if self.config.save_parquet:
            self.storage.save_all(radicals, hanzi, vocabulary)

        return exports

    # ------------------------------------------------------------------
    def _build_radicals(self, statistics: dict[str, dict]) -> list[dict]:
        records: list[dict] = []
        for component, data in statistics.items():
            record = {
                "radical": component,
                "meaning": data.get("meaning", ""),
                "productivity_score": int(data.get("productivity_score", 0) or 0),
                "usage_count": int(data.get("usage_count", 0) or 0),
                "usage_hsk1": int(data.get("usage_hsk1", 0) or 0),
                "usage_hsk2": int(data.get("usage_hsk2", 0) or 0),
                "usage_hsk3": int(data.get("usage_hsk3", 0) or 0),
                "stroke_count": self._count_strokes(component),
                "level": 0,
            }
            records.append(record)

        records.sort(key=lambda item: (-item["productivity_score"], item["radical"]))
        return records

    def _build_hanzi(self, hanzi_meta: dict[str, dict], hanzi_levels: dict[str, int]) -> list[dict]:
        records: list[dict] = []
        for char, data in hanzi_meta.items():
            components = data.get("components") or []
            components_str = "|".join(components)
            hsk_level = data.get("hsk_level") or hanzi_levels.get(char)
            record = {
                "hanzi": char,
                "pinyin": data.get("pinyin", ""),
                "meaning": data.get("meaning", ""),
                "components": components_str,
                "component_count": len(components),
                "hsk_level": hsk_level,
                "is_surname": bool(data.get("is_surname", False)),
                "stroke_count": self._count_strokes(char),
                "level": 0,
            }
            records.append(record)

        records.sort(key=lambda item: (item.get("hsk_level") or 0, item["hanzi"]))
        return records

    def _build_vocabulary(self, rows: Iterable[dict]) -> list[dict]:
        records: list[dict] = []
        for row in rows:
            word = row.get("word", "")
            record = {
                "word": word,
                "hsk_level": row.get("hsk_level"),
                "frequency_position": row.get("frequency_position"),
                "pinyin": row.get("pinyin", ""),
                "meaning": row.get("meaning", ""),
                "is_surname": bool(row.get("is_surname", False)),
                "stroke_count": self._count_strokes(word),
                "hanzi_breakdown": " ".join(list(word)) if word else "",
                "level": 0,
            }
            records.append(record)

        records.sort(key=lambda item: (item.get("hsk_level") or 0, item.get("frequency_position") or 0))
        return records

    # ------------------------------------------------------------------
    def _count_strokes(self, text: str) -> int:
        if not text:
            return 0
        counter = self.stroke_counter
        try:
            value = counter(text)
        except Exception:
            value = None

        if isinstance(value, (list, tuple)):
            try:
                return int(sum(value))
            except Exception:
                value = None

        if isinstance(value, (int, float)) and value >= 0:
            return int(value)

        # Fallback: sum per-character strokes (or 1 per char if unavailable)
        total = 0
        for char in text:
            try:
                subtotal = counter(char)
                if isinstance(subtotal, (int, float)) and subtotal >= 0:
                    total += int(subtotal)
                else:
                    total += 1
            except Exception:
                total += 1
        return total

    # ------------------------------------------------------------------
    def _save_csv(self, radicals: list[dict], hanzi: list[dict], vocabulary: list[dict]) -> None:
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        pd.DataFrame(radicals).to_csv(output_dir / "radicals.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(hanzi).to_csv(output_dir / "hanzi.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(vocabulary).to_csv(output_dir / "vocabulary.csv", index=False, encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# Helper classes & factories


class _HSKDictionary:
    """Thin wrapper that exposes a ``definition_lookup`` method."""

    def __init__(self, data_dir: Path) -> None:
        self.entries: Dict[str, List[dict]] = {}
        self._load_meanings(data_dir)

    def definition_lookup(self, term: str) -> List[dict]:  # pragma: no cover - simple proxy
        return [entry.copy() for entry in self.entries.get(term, [])]

    # Internal helpers --------------------------------------------------
    def _load_meanings(self, data_dir: Path) -> None:
        meaning_dir = data_dir / "HSK List (Meaning)"
        if not meaning_dir.exists():  # pragma: no cover - defensive guard
            return

        for file_path in sorted(meaning_dir.glob("HSK *.tsv")):
            with file_path.open("r", encoding="utf-8-sig") as handle:
                reader = csv.reader(handle, delimiter="\t")
                for row in reader:
                    if len(row) < 4:
                        continue
                    trad, simp, pinyin, *meaning_parts = row
                    meaning = "\t".join(meaning_parts).strip() or ""
                    entry = {"pinyin": pinyin, "definition": meaning}
                    for key in {simp, trad}:
                        key = key.strip()
                        if not key:
                            continue
                        self.entries.setdefault(key, []).append(entry)


def _create_default_decomposer():
    try:  # pragma: no cover - optional dependency
        from hanzipy.decomposer import HanziDecomposer
    except Exception:
        return _FallbackDecomposer()

    try:
        return HanziDecomposer()
    except Exception:
        return _FallbackDecomposer()


def _create_default_stroke_counter() -> Optional[Callable[[str], int]]:
    try:  # pragma: no cover - optional dependency
        from strokes import strokes as stroke_fn
    except Exception:
        return None
    return stroke_fn


def _fallback_stroke_counter(text: str) -> int:  # pragma: no cover - simple fallback
    return len(text or "")


class _FallbackDecomposer:
    """No-op decomposer used when hanzipy is unavailable."""

    def decompose(self, _char: str) -> dict:
        return {"radical": [], "graphical": []}

    def get_radical_meaning(self, component: str) -> str:
        return ""
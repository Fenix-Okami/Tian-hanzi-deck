"""Composable deck build pipeline for Tian Hanzi."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

from .components import ComponentAnalyzer
from .data_sources import HSKDataRepository

__all__ = ["DeckBuildConfig", "DeckBuilder"]


@dataclass(frozen=True)
class DeckBuildConfig:
    hsk_levels: Sequence[int] = (1, 2, 3)
    hsk_data_dir: str = "data/HSK-3.0"
    output_dir: str = "data"
    cache_components: bool = False


@dataclass
class DeckBuilder:
    config: DeckBuildConfig
    dictionary: object | None = None
    decomposer: object | None = None
    stroke_counter: callable | None = None
    repository: HSKDataRepository = field(init=False)

    def __post_init__(self) -> None:
        self.repository = HSKDataRepository(self.config.hsk_data_dir)
        self.dictionary = self.dictionary or self._load_dictionary()
        self.decomposer = self.decomposer or self._load_decomposer()
        self.stroke_counter = self.stroke_counter or self._load_stroke_counter()
        self.analyzer = ComponentAnalyzer(self.decomposer, self.dictionary)

    def build(self) -> dict[str, list[dict]]:
        levels = tuple(int(level) for level in self.config.hsk_levels)
        vocabulary = self.repository.load_vocabulary(levels, self.dictionary)
        hanzi_to_hsk = self.repository.load_hanzi_levels(levels)
        hanzi = self.repository.extract_hanzi_from_vocabulary(vocabulary)

        print("⚙️  Processing hanzi and components...")
        hanzi_data, component_stats = self.analyzer.analyse(hanzi, hanzi_to_hsk)
        components = self._normalise_components(component_stats.details)

        print("💾 Exporting artefacts...")
        exports = self._export(vocabulary, hanzi_data, components)
        self._print_summary(vocabulary, hanzi_data, components)
        return exports

    def _export(
        self,
        vocabulary: list[dict],
        hanzi_data: dict[str, dict],
        components: list[dict],
    ) -> dict[str, list[dict]]:
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        vocab_df = pd.DataFrame(vocabulary)
        if not vocab_df.empty:
            vocab_df["stroke_count"] = vocab_df["word"].apply(self._stroke_count)
            vocab_df.to_csv(output_path / "vocabulary.csv", index=False, encoding="utf-8")
            vocab_df.to_parquet(
                output_path / "vocabulary.parquet", engine="pyarrow", compression="snappy", index=False
            )

        hanzi_list = []
        for char, data in hanzi_data.items():
            level = data.get("hsk_level")
            hanzi_list.append(
                {
                    "hanzi": data["hanzi"],
                    "pinyin": data.get("pinyin", ""),
                    "meaning": data.get("meaning", ""),
                    "components": "|".join(data.get("components", [])),
                    "component_count": data.get("component_count", 0),
                    "hsk_level": None if level in ("", None) else int(level),
                    "is_surname": data.get("is_surname", False),
                }
            )
        hanzi_df = pd.DataFrame(hanzi_list)
        if not hanzi_df.empty:
            hanzi_df["stroke_count"] = hanzi_df["hanzi"].apply(self._stroke_count)
            hanzi_df["hsk_level"] = hanzi_df["hsk_level"].astype("Int64")
            hanzi_df.to_csv(output_path / "hanzi.csv", index=False, encoding="utf-8")
            hanzi_df.to_parquet(
                output_path / "hanzi.parquet", engine="pyarrow", compression="snappy", index=False
            )

        comp_df = pd.DataFrame(components)
        if not comp_df.empty:
            comp_df = comp_df.sort_values("productivity_score", ascending=False)
            comp_df.to_csv(output_path / "radicals.csv", index=False, encoding="utf-8")
            comp_df.to_parquet(
                output_path / "radicals.parquet", engine="pyarrow", compression="snappy", index=False
            )

        return {
            "vocabulary": vocab_df.to_dict("records"),
            "hanzi": hanzi_df.to_dict("records"),
            "components": comp_df.to_dict("records"),
        }

    def _stroke_count(self, text: str) -> int:
        result = self.stroke_counter(text)
        if isinstance(result, int):
            return result
        if isinstance(result, list):
            return sum(result)
        return 0

    def _normalise_components(self, component_details: dict[str, dict]) -> list[dict]:
        rows = []
        for component, data in component_details.items():
            row = {**data}
            row["radical"] = row.pop("component")
            row["stroke_count"] = self._stroke_count(component)
            rows.append(row)
        return rows

    def _print_summary(
        self,
        vocabulary: Iterable[dict],
        hanzi_data: dict[str, dict],
        components: list[dict],
    ) -> None:
        print("=" * 70)
        print(f"HSK DECK BUILDER STATISTICS (Levels {list(self.config.hsk_levels)})")
        print("=" * 70)
        print(f"\n📚 Vocabulary: {len(vocabulary)} words")
        print(f"🔤 Hanzi: {len(hanzi_data)} characters")
        print(f"🧩 Components: {len(components)} unique components")
        print("=" * 70)

    @staticmethod
    def _load_dictionary():
        try:
            from hanzipy.dictionary import HanziDictionary
        except ImportError as exc:  # pragma: no cover - external dependency
            raise RuntimeError("hanzipy is required to build the deck") from exc
        return HanziDictionary()

    @staticmethod
    def _load_decomposer():
        try:
            from hanzipy.decomposer import HanziDecomposer
        except ImportError as exc:  # pragma: no cover - external dependency
            raise RuntimeError("hanzipy is required to build the deck") from exc
        return HanziDecomposer()

    @staticmethod
    def _load_stroke_counter():
        try:
            from strokes import strokes
        except ImportError as exc:  # pragma: no cover - external dependency
            raise RuntimeError("strokes is required to build the deck") from exc
        return strokes

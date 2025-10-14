"""Scoring helpers for HSK vocabulary and hanzi."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

__all__ = ["HSKScorer"]


class HSKScorer:
    DEFAULT_LEVEL_SCORES = {1: 1000, 2: 700, 3: 500, 4: 350, 5: 200, 6: 100, "7-9": 0}
    FREQUENCY_BONUS_THRESHOLD = 100
    FREQUENCY_BONUS_POINTS = 100

    def __init__(
        self,
        hsk_data_dir: str = "data/HSK-3.0",
        level_scores: Dict | None = None,
        frequency_threshold: int | None = None,
        frequency_bonus: int | None = None,
    ) -> None:
        self.hsk_dir = Path(hsk_data_dir)
        self.hanzi_dir = self.hsk_dir / "HSK Hanzi"
        self.frequency_dir = self.hsk_dir / "HSK List (Frequency)"
        self.level_scores = level_scores if level_scores else self.DEFAULT_LEVEL_SCORES
        self.frequency_threshold = (
            frequency_threshold if frequency_threshold else self.FREQUENCY_BONUS_THRESHOLD
        )
        self.frequency_bonus = frequency_bonus if frequency_bonus else self.FREQUENCY_BONUS_POINTS
        self.hanzi_data: Dict[str, dict] = {}
        self.vocab_data: Dict[str, dict] = {}

    def load_hsk_hanzi(self) -> Dict[str, dict]:
        hanzi_dict: Dict[str, dict] = {}
        for level in [1, 2, 3, 4, 5, 6, "7-9"]:
            file_path = self.hanzi_dir / f"HSK {level}.txt"
            if not file_path.exists():
                continue
            with file_path.open("r", encoding="utf-8") as handle:
                characters = [line.strip() for line in handle if line.strip()]
            for char in characters:
                hanzi_dict.setdefault(
                    char,
                    {
                        "hanzi": char,
                        "hsk_level": level,
                        "level_score": self.level_scores.get(level, 0),
                    },
                )
        self.hanzi_data = hanzi_dict
        return hanzi_dict

    def load_hsk_vocabulary(self) -> Dict[str, dict]:
        vocab_dict: Dict[str, dict] = {}
        for level in [1, 2, 3, 4, 5, 6, "7-9"]:
            file_path = self.frequency_dir / f"HSK {level}.txt"
            if not file_path.exists():
                continue
            with file_path.open("r", encoding="utf-8") as handle:
                words = [line.strip() for line in handle if line.strip()]
            for position, word in enumerate(words, start=1):
                if word in vocab_dict:
                    continue
                bonus = self.frequency_bonus if position <= self.frequency_threshold else 0
                vocab_dict[word] = {
                    "word": word,
                    "hsk_level": level,
                    "frequency_position": position,
                    "level_score": self.level_scores.get(level, 0),
                    "frequency_bonus": bonus,
                    "total_score": self.level_scores.get(level, 0) + bonus,
                }
        self.vocab_data = vocab_dict
        return vocab_dict

    def get_hanzi_score(self, hanzi: str) -> Tuple[int, dict]:
        data = self.hanzi_data.get(hanzi, {})
        return data.get("level_score", 0), data

    def get_vocab_score(self, word: str) -> Tuple[int, dict]:
        data = self.vocab_data.get(word, {})
        return data.get("total_score", 0), data

    def export_scored_hanzi_csv(self, output_file: str = "data/hsk_hanzi_scored.csv") -> None:
        if not self.hanzi_data:
            raise RuntimeError("No hanzi data loaded. Call load_hsk_hanzi() first.")
        df = pd.DataFrame(list(self.hanzi_data.values())).sort_values("level_score", ascending=False)
        df.to_csv(output_file, index=False, encoding="utf-8")

    def export_scored_vocabulary_csv(
        self, output_file: str = "data/hsk_vocabulary_scored.csv"
    ) -> None:
        if not self.vocab_data:
            raise RuntimeError("No vocabulary data loaded. Call load_hsk_vocabulary() first.")
        df = pd.DataFrame(list(self.vocab_data.values())).sort_values(
            "total_score", ascending=False
        )
        df.to_csv(output_file, index=False, encoding="utf-8")

    def export_scored_hanzi_parquet(
        self, output_file: str = "data/hsk_hanzi_scored.parquet"
    ) -> None:
        if not self.hanzi_data:
            raise RuntimeError("No hanzi data loaded. Call load_hsk_hanzi() first.")
        df = pd.DataFrame(list(self.hanzi_data.values())).sort_values("level_score", ascending=False)
        df.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)

    def export_scored_vocabulary_parquet(
        self, output_file: str = "data/hsk_vocabulary_scored.parquet"
    ) -> None:
        if not self.vocab_data:
            raise RuntimeError("No vocabulary data loaded. Call load_hsk_vocabulary() first.")
        df = pd.DataFrame(list(self.vocab_data.values())).sort_values(
            "total_score", ascending=False
        )
        df.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)

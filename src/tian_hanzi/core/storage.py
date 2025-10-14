"""Persistent storage helpers for deck artefacts."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

__all__ = ["ParquetDataManager"]


class ParquetDataManager:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.radicals_file = self.data_dir / "radicals.parquet"
        self.hanzi_file = self.data_dir / "hanzi.parquet"
        self.vocabulary_file = self.data_dir / "vocabulary.parquet"

    def save_radicals(self, radicals: List[Dict]) -> None:
        if not radicals:
            return
        df = pd.DataFrame(radicals)
        df.to_parquet(self.radicals_file, engine="pyarrow", compression="snappy", index=False)

    def save_hanzi(self, hanzi: List[Dict]) -> None:
        if not hanzi:
            return
        df = pd.DataFrame(hanzi)
        df.to_parquet(self.hanzi_file, engine="pyarrow", compression="snappy", index=False)

    def save_vocabulary(self, vocabulary: List[Dict]) -> None:
        if not vocabulary:
            return
        df = pd.DataFrame(vocabulary)
        df.to_parquet(self.vocabulary_file, engine="pyarrow", compression="snappy", index=False)

    def save_all(
        self, radicals: List[Dict], hanzi: List[Dict], vocabulary: List[Dict]
    ) -> None:
        self.save_radicals(radicals)
        self.save_hanzi(hanzi)
        self.save_vocabulary(vocabulary)

    def load_radicals(self) -> List[Dict]:
        if not self.radicals_file.exists():
            return []
        return pd.read_parquet(self.radicals_file, engine="pyarrow").to_dict("records")

    def load_hanzi(self) -> List[Dict]:
        if not self.hanzi_file.exists():
            return []
        return pd.read_parquet(self.hanzi_file, engine="pyarrow").to_dict("records")

    def load_vocabulary(self) -> List[Dict]:
        if not self.vocabulary_file.exists():
            return []
        return pd.read_parquet(self.vocabulary_file, engine="pyarrow").to_dict("records")

    def load_all(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        return self.load_radicals(), self.load_hanzi(), self.load_vocabulary()

    def get_stats(self) -> Dict[str, Dict]:
        stats: Dict[str, Dict] = {}
        for name, path in (
            ("radicals", self.radicals_file),
            ("hanzi", self.hanzi_file),
            ("vocabulary", self.vocabulary_file),
        ):
            if not path.exists():
                stats[name] = {"exists": False}
                continue
            df = pd.read_parquet(path, engine="pyarrow")
            stats[name] = {
                "file_path": str(path),
                "file_size_bytes": path.stat().st_size,
                "row_count": len(df),
                "columns": list(df.columns),
            }
        return stats

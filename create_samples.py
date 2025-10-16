#!/usr/bin/env python3
"""Generate sample CSV files and HTML previews using the shared SampleGenerator."""

from __future__ import annotations

import sys
import io
from pathlib import Path

# Windows console UTF-8 setup
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import pandas as pd
except ImportError as exc:
    print(f"❌ Error: pandas is not installed ({exc})")
    print("Install dependencies with: pip install pandas")
    sys.exit(1)

from tian_hanzi.core.samples import SampleGenerator


def load_dataframe(path: Path) -> pd.DataFrame:
    """Load a CSV file with friendly error messages."""
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"❌ Required file not found: {path}")
        print("Run create_hsk_deck.py first to generate the processed data.")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - passthrough diagnostics
        print(f"❌ Failed to load {path}: {exc}")
        sys.exit(1)


def main() -> None:
    data_dir = Path("data")
    print("🎴 Generating sample artefacts from processed deck data...\n")

    radicals_df = load_dataframe(data_dir / "radicals.csv")
    hanzi_df = load_dataframe(data_dir / "hanzi.csv")
    vocabulary_df = load_dataframe(data_dir / "vocabulary.csv")

    # Load and merge hanzi mnemonics from CSV
    hanzi_mnemonic_path = data_dir / "hanzi_mnemonic.csv"
    if hanzi_mnemonic_path.exists():
        print("📝 Loading hanzi mnemonics from hanzi_mnemonic.csv...")
        hanzi_mn_df = pd.read_csv(hanzi_mnemonic_path)
        
        # Get the columns we need
        merge_cols = ['hanzi']
        if 'meaning' in hanzi_mn_df.columns:
            hanzi_mn_df = hanzi_mn_df.rename(columns={'meaning': 'mnemonic_meaning'})
            merge_cols.append('mnemonic_meaning')
        if 'meaning_mnemonic' in hanzi_mn_df.columns:
            merge_cols.append('meaning_mnemonic')
        if 'reading_mnemonic' in hanzi_mn_df.columns:
            merge_cols.append('reading_mnemonic')
        
        # Merge with hanzi data
        hanzi_df = hanzi_df.merge(hanzi_mn_df[merge_cols], on='hanzi', how='left')
        
        # Use mnemonic meaning if available
        if 'mnemonic_meaning' in hanzi_df.columns:
            hanzi_df['meaning'] = hanzi_df['mnemonic_meaning'].fillna(hanzi_df['meaning'])
            hanzi_df = hanzi_df.drop(columns=['mnemonic_meaning'])
        
        # Fill missing mnemonic columns
        for col in ['meaning_mnemonic', 'reading_mnemonic']:
            if col in hanzi_df.columns:
                hanzi_df[col] = hanzi_df[col].fillna('')
        
        print(f"   ✓ Merged mnemonics for {len(hanzi_df)} hanzi\n")
    else:
        print("⚠️  hanzi_mnemonic.csv not found, skipping mnemonic merge\n")

    # Load and merge radical meanings from radicals_tian.csv
    radicals_tian_path = data_dir / "radicals_tian.csv"
    if radicals_tian_path.exists():
        print("📝 Loading enhanced radical data from radicals_tian.csv...")
        radicals_tian_df = pd.read_csv(radicals_tian_path)
        
        # Merge to get better meanings and HSK breakdown
        merge_cols = ['radical', 'meaning', 'usage_hsk1', 'usage_hsk2', 'usage_hsk3']
        radicals_merge = radicals_tian_df[merge_cols].copy()
        
        radicals_df = radicals_df.merge(
            radicals_merge,
            on='radical',
            how='left',
            suffixes=('_old', '_tian')
        )
        
        # Use Tian meaning if available
        radicals_df['meaning'] = radicals_df['meaning_tian'].fillna(radicals_df.get('meaning_old', radicals_df.get('meaning', '')))
        
        # Fill missing HSK counts
        for col in ['usage_hsk1', 'usage_hsk2', 'usage_hsk3']:
            if col not in radicals_df.columns:
                radicals_df[col] = 0
            else:
                radicals_df[col] = radicals_df[col].fillna(0).astype(int)
        
        # Clean up temp columns
        radicals_df = radicals_df.drop(columns=[c for c in radicals_df.columns if c.endswith('_old') or c.endswith('_tian')], errors='ignore')
        
        print(f"   ✓ Enhanced {len(radicals_df)} radicals with Tian data\n")

    generator = SampleGenerator(output_dir=data_dir)
    generator.generate(radicals_df, hanzi_df, vocabulary_df)


if __name__ == "__main__":
    main()


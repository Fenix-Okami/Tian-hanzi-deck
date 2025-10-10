#!/usr/bin/env python3
"""
Test the mnemonic generator with a small sample
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pandas as pd
except ImportError:
    print("Installing pandas...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "pyarrow"])
    import pandas as pd

# Load just a few entries
print("Loading data...")
hanzi_df = pd.read_parquet('data/hanzi.parquet')
vocab_df = pd.read_parquet('data/vocabulary.parquet')

print(f"Total: {len(hanzi_df)} hanzi, {len(vocab_df)} vocab")
print(f"\nFirst 3 hanzi:")
print(hanzi_df.head(3)[['hanzi', 'pinyin', 'meaning', 'components']])

print(f"\nFirst 3 vocab:")
print(vocab_df.head(3)[['word', 'pinyin', 'meaning']])

# Test the structure
hanzi_sample = hanzi_df.head(3)
for idx, row in hanzi_sample.iterrows():
    hanzi = row['hanzi']
    meaning = row['meaning']
    components = row.get('components', 'Unknown')
    print(f"\nHandling: {hanzi} = {meaning} (components: {components})")

#!/usr/bin/env python3
"""
Verify that 0-component hanzi are properly distributed across levels
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from collections import Counter

# Read hanzi data
hanzi_df = pd.read_csv('data/hanzi.csv')

# Filter 0-component hanzi
zero_comp = hanzi_df[hanzi_df['component_count'] == 0].copy()

print("=" * 70)
print(f"ZERO-COMPONENT HANZI DISTRIBUTION")
print("=" * 70)
print(f"\nTotal 0-component hanzi: {len(zero_comp)}")
print()

# Count by level
level_counts = Counter(zero_comp['tian_level'])

print("Distribution by Tian Level:")
print("-" * 70)
for level in sorted(level_counts.keys()):
    count = level_counts[level]
    hanzi_list = zero_comp[zero_comp['tian_level'] == level]['hanzi'].tolist()
    hanzi_str = ''.join(hanzi_list)
    print(f"Level {level:2d}: {count:3d} hanzi | {hanzi_str}")

print()
print("=" * 70)
print("LEVEL STATISTICS")
print("=" * 70)
print(f"Levels used: {min(level_counts.keys())} to {max(level_counts.keys())}")
print(f"Average per level: {len(zero_comp) / len(level_counts):.1f}")
print(f"Min per level: {min(level_counts.values())}")
print(f"Max per level: {max(level_counts.values())}")
print()

# Show a few examples from different levels
print("=" * 70)
print("EXAMPLES FROM DIFFERENT LEVELS")
print("=" * 70)
for level in sorted(level_counts.keys())[:10]:
    examples = zero_comp[zero_comp['tian_level'] == level].head(3)
    print(f"\nLevel {level}:")
    for _, row in examples.iterrows():
        print(f"  {row['hanzi']} ({row['pinyin']}) - {row['meaning'][:50]}")

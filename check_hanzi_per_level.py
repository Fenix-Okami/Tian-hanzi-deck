#!/usr/bin/env python3
"""
Check total hanzi (0-component + regular) per level
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

print("=" * 70)
print("TOTAL HANZI PER LEVEL")
print("=" * 70)

# Count total hanzi per level
level_counts = Counter(hanzi_df['tian_level'])

# Count 0-component hanzi per level
zero_comp_df = hanzi_df[hanzi_df['component_count'] == 0]
zero_comp_counts = Counter(zero_comp_df['tian_level'])

print("\nLevel | Total | 0-comp | Regular | Status")
print("-" * 70)

for level in sorted(level_counts.keys()):
    total = level_counts[level]
    zero_comp = zero_comp_counts.get(level, 0)
    regular = total - zero_comp
    
    # Status indicator
    if total < 15:
        status = "⚠️  LOW"
    elif total > 30:
        status = "❌ HIGH"
    else:
        status = "✅"
    
    print(f"{level:5d} | {total:5d} | {zero_comp:6d} | {regular:7d} | {status}")

print()
print("=" * 70)
print("STATISTICS")
print("=" * 70)
print(f"Total levels: {len(level_counts)}")
print(f"Total hanzi: {sum(level_counts.values())}")
print(f"Average per level: {sum(level_counts.values()) / len(level_counts):.1f}")
print(f"Min per level: {min(level_counts.values())} (level {min(level_counts, key=level_counts.get)})")
print(f"Max per level: {max(level_counts.values())} (level {max(level_counts, key=level_counts.get)})")
print()

# Show problem levels
problem_levels = [level for level, count in level_counts.items() if count < 15 or count > 30]
if problem_levels:
    print("⚠️  PROBLEM LEVELS:")
    for level in sorted(problem_levels):
        total = level_counts[level]
        zero_comp = zero_comp_counts.get(level, 0)
        print(f"   Level {level}: {total} hanzi ({zero_comp} are 0-comp)")

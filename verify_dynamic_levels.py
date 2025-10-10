#!/usr/bin/env python3
"""Verify dynamic level assignments from breakpoint analysis"""

import pandas as pd
import sys
import io

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load data
radicals_df = pd.read_parquet('data/radicals.parquet')
hanzi_df = pd.read_parquet('data/hanzi.parquet')
breakpoints_df = pd.read_csv('data/breakpoint_analysis.csv')

print("=" * 70)
print("🔍 Dynamic Level Assignment Verification")
print("=" * 70)

# Check radicals
print(f"\n📊 Radical Levels:")
print(f"   Total unique levels: {len(radicals_df['level'].unique())}")
print(f"   Level range: {int(radicals_df['level'].min())}-{int(radicals_df['level'].max())}")

print(f"\n🎯 Level 1 Radicals (most productive):")
level_1_radicals = radicals_df[radicals_df['level'] == 1].sort_values('usage_count', ascending=False)
for _, row in level_1_radicals.head(10).iterrows():
    print(f"   {row['radical']:3s} - {row['meaning']:20s} (used in {row['usage_count']:3d} hanzi)")

print(f"\n🎯 Level 2 Radicals:")
level_2_radicals = radicals_df[radicals_df['level'] == 2].sort_values('usage_count', ascending=False)
for _, row in level_2_radicals.head(6).iterrows():
    print(f"   {row['radical']:3s} - {row['meaning']:20s} (used in {row['usage_count']:3d} hanzi)")

# Compare with breakpoint analysis
print(f"\n📋 Comparison with Breakpoint Analysis:")
print(f"   Expected levels from analysis: {len(breakpoints_df)}")
print(f"   Actual radical levels applied: {len(radicals_df['level'].unique())}")

# Check hanzi level distribution
print(f"\n📊 Hanzi Levels:")
print(f"   Total unique levels: {len(hanzi_df['level'].unique())}")
print(f"   Level range: {int(hanzi_df['level'].min())}-{int(hanzi_df['level'].max())}")

print(f"\n🎯 Level 2 Hanzi (unlocked by Level 1 radicals):")
level_2_hanzi = hanzi_df[hanzi_df['level'] == 2].head(10)
for _, row in level_2_hanzi.iterrows():
    print(f"   {row['hanzi']} ({row['pinyin']:8s}) - {row['meaning'][:30]:30s} [{row['components']}]")

# Check level distribution
print(f"\n📈 Radicals per level (first 10 levels):")
level_counts = radicals_df['level'].value_counts().sort_index()
for level in sorted(level_counts.index)[:10]:
    count = level_counts[level]
    radicals_list = list(radicals_df[radicals_df['level'] == level]['radical'].values)
    print(f"   Level {int(level):2d}: {count:2d} radicals - {' '.join(radicals_list[:15])}")

print("\n" + "=" * 70)
print("✅ Verification complete!")
print("=" * 70)

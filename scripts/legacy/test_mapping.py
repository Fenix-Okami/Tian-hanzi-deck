#!/usr/bin/env python3
"""Quick test of dynamic level mapping"""
import pandas as pd

breakpoints_df = pd.read_csv('data/breakpoint_analysis.csv')
print(f"Breakpoints file has {len(breakpoints_df)} levels\n")

# Build radical to level mapping
radical_to_level = {}
for _, bp_row in breakpoints_df.iterrows():
    level = bp_row['level']
    radicals_str = bp_row['radicals']
    if pd.notna(radicals_str):
        radicals_list = radicals_str.split('|')
        for radical in radicals_list:
            radical = radical.strip()
            if radical and radical != 'No glyph available':
                radical_to_level[radical] = level

print(f"Created mapping for {len(radical_to_level)} radicals")
print(f"Levels in mapping: {sorted(set(radical_to_level.values()))[:10]}...")
print(f"\nSample mappings:")
for i, (rad, lev) in enumerate(list(radical_to_level.items())[:10]):
    print(f"  {rad} -> Level {lev}")

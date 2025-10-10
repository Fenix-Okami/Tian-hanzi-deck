#!/usr/bin/env python3
"""
Find hanzi that could be in Level 1 (only use Level 1 radicals)
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

# Read data
hanzi_df = pd.read_csv('data/hanzi.csv')
radicals_df = pd.read_csv('data/radicals.csv')

# Get Level 1 radicals
level_1_radicals = set(radicals_df[radicals_df['tian_level'] == 1]['radical'].tolist())

print("=" * 70)
print("LEVEL 1 RADICALS")
print("=" * 70)
print(f"Total: {len(level_1_radicals)}")
print(f"Radicals: {', '.join(sorted(level_1_radicals, key=lambda x: str(x)))}")
print()

# Find hanzi that only use Level 1 radicals
eligible_hanzi = []

for _, row in hanzi_df.iterrows():
    hanzi = row['hanzi']
    components = row['components']
    component_count = row['component_count']
    
    # 0-component hanzi (are themselves radicals)
    if component_count == 0:
        if hanzi in level_1_radicals:
            eligible_hanzi.append((hanzi, row['pinyin'], 'SELF', True))
        continue
    
    # Parse components
    if pd.isna(components) or components == '':
        continue
    
    comp_list = [c.strip() for c in str(components).split('|')]
    
    # Check if all components are in Level 1
    all_in_level_1 = all(comp in level_1_radicals for comp in comp_list)
    
    if all_in_level_1:
        eligible_hanzi.append((hanzi, row['pinyin'], '|'.join(comp_list), False))

print("=" * 70)
print(f"HANZI THAT COULD BE IN LEVEL 1")
print("=" * 70)
print(f"Total: {len(eligible_hanzi)}")
print()

zero_comp = [h for h in eligible_hanzi if h[3]]
regular = [h for h in eligible_hanzi if not h[3]]

print(f"0-component (themselves): {len(zero_comp)}")
for hanzi, pinyin, comps, _ in zero_comp:
    print(f"  {hanzi} ({pinyin})")

print()
print(f"Regular (use only Level 1 radicals): {len(regular)}")
for hanzi, pinyin, comps, _ in regular[:20]:
    print(f"  {hanzi} ({pinyin}) = {comps}")

if len(regular) > 20:
    print(f"  ... and {len(regular) - 20} more")

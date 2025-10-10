#!/usr/bin/env python3
"""
Debug: Compare breakpoint analysis predictions vs actual hanzi unlocked
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

# Read data
breakpoints_df = pd.read_csv('data/breakpoint_analysis.csv')
hanzi_df = pd.read_csv('data/hanzi.csv')
radicals_df = pd.read_csv('data/radicals.csv')

print("=" * 70)
print("BREAKPOINT ANALYSIS vs ACTUAL HANZI")
print("=" * 70)

# Check first few levels
for level in range(1, 11):
    bp_row = breakpoints_df[breakpoints_df['level'] == level]
    if bp_row.empty:
        continue
    
    predicted = bp_row.iloc[0]['num_unlocked_hanzi']
    radicals_str = bp_row.iloc[0]['radicals']
    radicals_list = radicals_str.split('|')
    
    # Get actual hanzi at this level
    actual_hanzi = hanzi_df[hanzi_df['tian_level'] == level]
    actual_count = len(actual_hanzi)
    
    # Get radicals at this level
    level_radicals = radicals_df[radicals_df['tian_level'] == level]
    
    print(f"\nLevel {level}:")
    print(f"  Radicals: {len(level_radicals)} | {', '.join(level_radicals['radical'].tolist())}")
    print(f"  Predicted hanzi: {predicted}")
    print(f"  Actual hanzi:    {actual_count}")
    
    if actual_count != predicted:
        diff = actual_count - predicted
        print(f"  ⚠️  MISMATCH: {diff:+d}")
        
        # Show actual hanzi
        zero_comp = actual_hanzi[actual_hanzi['component_count'] == 0]
        regular = actual_hanzi[actual_hanzi['component_count'] > 0]
        print(f"     - {len(zero_comp)} are 0-component: {''.join(zero_comp['hanzi'].tolist())}")
        print(f"     - {len(regular)} are regular: {''.join(regular['hanzi'].tolist()[:15])}")

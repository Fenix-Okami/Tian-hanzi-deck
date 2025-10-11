#!/usr/bin/env python3
"""Check hanzi with zero components"""
import pandas as pd
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

h = pd.read_csv('data/hanzi.csv')
zero_comp = h[h['component_count'] == 0]

print('='*70)
print(f'Hanzi with 0 components: {len(zero_comp)}')
print('='*70)

if len(zero_comp) > 0:
    print('\nThese hanzi ARE radicals themselves, so they should be at Tian Level 1:')
    for _, row in zero_comp.head(15).iterrows():
        print(f"  Tian {row['tian_level']:2d} | {row['hanzi']} ({row['pinyin']:8s}) | {row['meaning'][:50]}")
else:
    print('\n✓ No hanzi with 0 components found')

print('\n' + '='*70)

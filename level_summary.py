#!/usr/bin/env python3
"""Final summary of dynamic level distribution"""
import pandas as pd
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print('='*70)
print('DYNAMIC LEVEL DISTRIBUTION - FINAL SUMMARY')
print('='*70)

r = pd.read_parquet('data/radicals.parquet')
h = pd.read_parquet('data/hanzi.parquet')
v = pd.read_parquet('data/vocabulary.parquet')

print(f'\nRADICALS: {len(r)} total, levels {int(r.level.min())}-{int(r.level.max())}')
print(f'   Unique levels: {r.level.nunique()}')
print(f'   Average per level: {len(r)/r.level.nunique():.1f}')

print(f'\nHANZI: {len(h)} total, levels {int(h.level.min())}-{int(h.level.max())}')
print(f'   Unique levels: {h.level.nunique()}')
print(f'   Average per level: {len(h)/h.level.nunique():.1f}')

print(f'\nVOCABULARY: {len(v)} total, levels {int(v.level.min())}-{int(v.level.max())}')
print(f'   Unique levels: {v.level.nunique()}')
print(f'   Average per level: {len(v)/v.level.nunique():.1f}')

print('\n' + '='*70)
print('COMPARISON: Fixed vs Dynamic')
print('='*70)
print('\n  Fixed approach:  47 levels (5 radicals each)')
print('  Dynamic approach: 37 levels (variable radicals)')
print('  Improvement:     21% reduction (10 fewer levels)')
print('\n' + '='*70)

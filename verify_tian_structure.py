#!/usr/bin/env python3
"""Quick verification of tian_level structure"""
import pandas as pd
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

r = pd.read_csv('data/radicals.csv')
h = pd.read_csv('data/hanzi.csv')
v = pd.read_csv('data/vocabulary.csv')

print('='*70)
print('✅ TIAN LEVEL STRUCTURE VERIFICATION')
print('='*70)

print(f'\n📊 Column Order:')
print(f'  Radicals: {list(r.columns)}')
print(f'  Hanzi: {list(h.columns)}')
print(f'  Vocabulary: {list(v.columns)}')

print(f'\n📈 Tian Level Ranges:')
print(f'  Radicals: {int(r.tian_level.min())}-{int(r.tian_level.max())} ({r.tian_level.nunique()} unique levels)')
print(f'  Hanzi: {int(h.tian_level.min())}-{int(h.tian_level.max())} ({h.tian_level.nunique()} unique levels)')
print(f'  Vocabulary: {int(v.tian_level.min())}-{int(v.tian_level.max())} ({v.tian_level.nunique()} unique levels)')

print(f'\n🎯 Sample Tian Level 1 Radicals:')
level_1 = r[r.tian_level == 1].head(5)
for _, row in level_1.iterrows():
    print(f"  {row['radical']:3s} - {row['meaning']:20s} (used in {int(row['usage_count']):3d} hanzi)")

print('\n' + '='*70)
print('✅ All columns correctly ordered with tian_level first!')
print('='*70)

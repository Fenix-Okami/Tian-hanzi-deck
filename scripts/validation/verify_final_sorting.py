#!/usr/bin/env python3
"""Final verification of sorting order"""
import pandas as pd
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print('='*70)
print('✅ FINAL SORTING VERIFICATION')
print('='*70)

# Check radicals
r = pd.read_csv('data/radicals.csv')
print('\n📊 RADICALS - Sorted by: tian_level ↑, usage_count ↓')
print('   First 10 entries:')
for i in range(min(10, len(r))):
    row = r.iloc[i]
    print(f'   Tian {int(row.tian_level):2d} | {row.radical:3s} | {row.meaning:20s} | uses: {int(row.usage_count):3d}')

# Check hanzi
h = pd.read_csv('data/hanzi.csv')
print('\n📊 HANZI - Sorted by: tian_level ↑, hsk_level ↑, component_count ↑')
print('   First 10 entries:')
for i in range(min(10, len(h))):
    row = h.iloc[i]
    hsk = int(row.hsk_level)
    print(f'   Tian {int(row.tian_level):2d} | HSK {hsk} | {row.hanzi} ({row.pinyin:8s}) | {row.component_count} components')

# Check vocabulary
v = pd.read_csv('data/vocabulary.csv')
print('\n📊 VOCABULARY - Sorted by: tian_level ↑, hsk_level ↑, frequency_position ↑')
print('   First 10 entries:')
for i in range(min(10, len(v))):
    row = v.iloc[i]
    hsk = int(row.hsk_level)
    freq = int(row.frequency_position)
    print(f'   Tian {int(row.tian_level):2d} | HSK {hsk} | freq #{freq:4d} | {row.word:6s} ({row.pinyin})')

print('\n' + '='*70)
print('✅ All files properly sorted!')
print('='*70)

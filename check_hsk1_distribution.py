#!/usr/bin/env python3
import pandas as pd

vocab_df = pd.read_parquet('data/vocabulary.parquet')

print('=' * 70)
print('NEW HSK1 DISTRIBUTION (After Productivity Score Fix)')
print('=' * 70)
print()
print('First 15 Tian Levels:')
print('-' * 70)
print(f"{'Level':>5} | {'Total':>5} | {'HSK1':>8} | {'HSK2':>8} | {'HSK3':>8}")
print('-' * 70)

for tian_level in range(1, 16):
    level_data = vocab_df[vocab_df['tian_level'] == tian_level]
    hsk_counts = level_data['hsk_level'].value_counts().sort_index()
    total = len(level_data)
    
    hsk1 = hsk_counts.get(1, 0)
    hsk2 = hsk_counts.get(2, 0)
    hsk3 = hsk_counts.get(3, 0)
    
    hsk1_pct = (hsk1/total*100) if total > 0 else 0
    hsk2_pct = (hsk2/total*100) if total > 0 else 0
    hsk3_pct = (hsk3/total*100) if total > 0 else 0
    
    print(f'{tian_level:5d} | {total:5d} | {hsk1:3d} ({hsk1_pct:4.1f}%) | {hsk2:3d} ({hsk2_pct:4.1f}%) | {hsk3:3d} ({hsk3_pct:4.1f}%)')

print('-' * 70)

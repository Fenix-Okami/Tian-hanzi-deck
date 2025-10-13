#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show radical usage breakdown by HSK level
"""
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pandas as pd

def main():
    df = pd.read_csv('data/radicals.csv')
    
    print()
    print('=' * 80)
    print('RADICAL HSK LEVEL DISTRIBUTION PATTERNS')
    print('=' * 80)
    print()
    
    # Radicals heavily used in HSK 1
    print('HSK 1 Heavy Radicals (>40% of usage in HSK 1):')
    print('-' * 80)
    hsk1_heavy = df[df['usage_hsk1'] / df['usage_count'] > 0.40].nlargest(10, 'usage_count')
    for idx, row in hsk1_heavy.iterrows():
        pct = row['usage_hsk1'] / row['usage_count'] * 100
        print(f'  {row["radical"]:>3} ({row["meaning"][:15]:15}): {row["usage_hsk1"]:2}/{row["usage_count"]:3} = {pct:5.1f}% | HSK2:{row["usage_hsk2"]:2} HSK3:{row["usage_hsk3"]:2}')
    
    print()
    
    # Radicals heavily used in HSK 2
    print('HSK 2 Heavy Radicals (>45% of usage in HSK 2):')
    print('-' * 80)
    hsk2_heavy = df[df['usage_hsk2'] / df['usage_count'] > 0.45].nlargest(10, 'usage_count')
    for idx, row in hsk2_heavy.iterrows():
        pct = row['usage_hsk2'] / row['usage_count'] * 100
        print(f'  {row["radical"]:>3} ({row["meaning"][:15]:15}): {row["usage_hsk2"]:2}/{row["usage_count"]:3} = {pct:5.1f}% | HSK1:{row["usage_hsk1"]:2} HSK3:{row["usage_hsk3"]:2}')
    
    print()
    
    # Radicals heavily used in HSK 3
    print('HSK 3 Heavy Radicals (>45% of usage in HSK 3):')
    print('-' * 80)
    hsk3_heavy = df[df['usage_hsk3'] / df['usage_count'] > 0.45].nlargest(10, 'usage_count')
    for idx, row in hsk3_heavy.iterrows():
        pct = row['usage_hsk3'] / row['usage_count'] * 100
        print(f'  {row["radical"]:>3} ({row["meaning"][:15]:15}): {row["usage_hsk3"]:2}/{row["usage_count"]:3} = {pct:5.1f}% | HSK1:{row["usage_hsk1"]:2} HSK2:{row["usage_hsk2"]:2}')
    
    print()
    
    # Show balanced radicals (used roughly evenly across all levels)
    df['variance'] = df[['usage_hsk1', 'usage_hsk2', 'usage_hsk3']].var(axis=1)
    balanced = df[df['usage_count'] >= 20].nsmallest(10, 'variance')
    
    print('Balanced Radicals (used evenly across all HSK levels):')
    print('-' * 80)
    for idx, row in balanced.iterrows():
        print(f'  {row["radical"]:>3} ({row["meaning"][:15]:15}): Total:{row["usage_count"]:3} | HSK1:{row["usage_hsk1"]:2} HSK2:{row["usage_hsk2"]:2} HSK3:{row["usage_hsk3"]:2}')
    
    print()
    print('=' * 80)

if __name__ == '__main__':
    main()

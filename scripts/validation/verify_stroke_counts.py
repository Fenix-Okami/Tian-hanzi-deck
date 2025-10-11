#!/usr/bin/env python3
"""
Verify stroke counts in the data
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from strokes import strokes

print("=" * 70)
print("STROKE COUNT VERIFICATION")
print("=" * 70)
print()

# Load data
radicals_df = pd.read_csv('data/radicals.csv')
hanzi_df = pd.read_csv('data/hanzi.csv')
vocab_df = pd.read_csv('data/vocabulary.csv')

print("1. Radicals:")
print("-" * 70)
sample_radicals = radicals_df.head(10)
for _, row in sample_radicals.iterrows():
    radical = row['radical']
    stored = row['stroke_count']
    try:
        actual = strokes(radical)
        status = '✓' if stored == actual else f'✗ (actual: {actual})'
    except:
        status = '? (cannot verify)'
    print(f"  {radical:3} | Stored: {stored:2} {status}")

print("\n2. Hanzi:")
print("-" * 70)
sample_hanzi = hanzi_df.head(10)
for _, row in sample_hanzi.iterrows():
    char = row['hanzi']
    stored = row['stroke_count']
    actual = strokes(char)
    status = '✓' if stored == actual else f'✗ (actual: {actual})'
    print(f"  {char} | Stored: {stored:2} | Actual: {actual:2} {status}")

print("\n3. Vocabulary:")
print("-" * 70)
sample_vocab = vocab_df.head(10)
for _, row in sample_vocab.iterrows():
    word = row['word']
    stored = row['stroke_count']
    
    # Calculate actual
    result = strokes(word)
    if isinstance(result, int):
        actual = result
    else:
        actual = sum(result)
    
    status = '✓' if stored == actual else f'✗ (actual: {actual})'
    print(f"  {word:6} | Stored: {stored:2} | Actual: {actual:2} {status}")

print("\n" + "=" * 70)
print("STATISTICS")
print("=" * 70)
print(f"Radicals: {len(radicals_df)} with stroke counts")
print(f"Hanzi:    {len(hanzi_df)} with stroke counts")
print(f"Vocab:    {len(vocab_df)} with stroke counts")
print()
print(f"Hanzi stroke range: {hanzi_df['stroke_count'].min()}-{hanzi_df['stroke_count'].max()}")
print(f"Vocab stroke range: {vocab_df['stroke_count'].min()}-{vocab_df['stroke_count'].max()}")

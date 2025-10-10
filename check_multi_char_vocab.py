#!/usr/bin/env python3
"""
Check multi-character vocabulary words
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

hanzi_df = pd.read_csv('data/hanzi.csv')
vocab_df = pd.read_csv('data/vocabulary.csv')
h2l = dict(zip(hanzi_df['hanzi'], hanzi_df['tian_level']))

print('Multi-character vocabulary verification:')
print('-' * 70)

# Get 2-character words
two_char = vocab_df[vocab_df['word'].str.len() == 2].head(20)

for _, row in two_char.iterrows():
    word = row['word']
    vocab_level = row['tian_level']
    
    char_levels = []
    for char in word:
        if char in h2l:
            char_levels.append(h2l[char])
    
    if len(char_levels) == 2:
        expected = max(char_levels)
        status = '✓' if vocab_level == expected else f'❌ (expected {expected})'
        print(f'{word} (Level {vocab_level:2}) = {word[0]}(L{char_levels[0]:2}) + {word[1]}(L{char_levels[1]:2}) = max({char_levels[0]},{char_levels[1]}) = {expected} {status}')

#!/usr/bin/env python3
"""Verify the dependency-based sorting is correct"""

import pandas as pd

hanzi_df = pd.read_parquet('data/hanzi.parquet')
radicals_df = pd.read_parquet('data/radicals.parquet')

# Create radical to level mapping
radical_to_level = dict(zip(radicals_df['radical'], radicals_df['level']))

print('Verifying hanzi use only earlier radicals:\n')

# Check first few hanzi from different levels
for level in [1, 2, 3, 5, 10]:
    level_hanzi = hanzi_df[hanzi_df['level'] == level].head(3)
    
    print(f'Level {level} Hanzi:')
    for idx, row in level_hanzi.iterrows():
        char = row['character']
        radicals_str = row['radicals']
        char_level = row['level']
        
        # Parse radicals
        if pd.notna(radicals_str) and radicals_str:
            radicals_list = [r.strip() for r in radicals_str.split(' + ')]
            radical_levels = [radical_to_level.get(r, '?') for r in radicals_list]
            max_rad_level = max([l for l in radical_levels if l != '?'], default=0)
            
            status = "✓" if max_rad_level <= char_level else "✗"
            print(f'  {status} {char} (L{char_level}): uses radicals from levels {radical_levels}')
    print()

# Check vocabulary
print('\nVerifying vocabulary uses only earlier hanzi:\n')

vocab_df = pd.read_parquet('data/vocabulary.parquet')
hanzi_to_level = dict(zip(hanzi_df['character'], hanzi_df['level']))

for level in [1, 3, 5, 10]:
    level_vocab = vocab_df[vocab_df['level'] == level].head(3)
    
    print(f'Level {level} Vocabulary:')
    for idx, row in level_vocab.iterrows():
        word = row['word']
        word_level = row['level']
        
        # Get character levels
        char_levels = [hanzi_to_level.get(c, '?') for c in word]
        max_char_level = max([l for l in char_levels if l != '?'], default=0)
        
        status = "✓" if max_char_level <= word_level else "✗"
        print(f'  {status} {word} (L{word_level}): uses hanzi from levels {char_levels}')
    print()

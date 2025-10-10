#!/usr/bin/env python3
"""Show detailed breakdown of first levels"""

import pandas as pd

radicals_df = pd.read_parquet('data/radicals.parquet')
hanzi_df = pd.read_parquet('data/hanzi.parquet')
vocab_df = pd.read_parquet('data/vocabulary.parquet')

print('First 10 Levels - Detailed Breakdown\n')
print('='*70)

for level in range(1, 11):
    # Radicals
    level_radicals = radicals_df[radicals_df['level'] == level]
    rad_list = level_radicals['radical'].tolist()
    
    # Hanzi
    level_hanzi = hanzi_df[hanzi_df['level'] == level]
    hanzi_count = len(level_hanzi)
    hanzi_sample = level_hanzi['character'].head(10).tolist()
    
    # Vocabulary
    level_vocab = vocab_df[vocab_df['level'] == level]
    vocab_count = len(level_vocab)
    vocab_sample = level_vocab['word'].head(5).tolist()
    
    print(f'\nLEVEL {level}:')
    print(f'  Radicals ({len(rad_list)}): {" ".join(rad_list)}')
    print(f'  Hanzi ({hanzi_count}): {" ".join(hanzi_sample)}' + (' ...' if hanzi_count > 10 else ''))
    print(f'  Vocab ({vocab_count}): {" ".join(vocab_sample)}' + (' ...' if vocab_count > 5 else ''))

print('\n' + '='*70)
print(f'\nTotal: {len(radicals_df)} radicals, {len(hanzi_df)} hanzi, {len(vocab_df)} vocabulary')

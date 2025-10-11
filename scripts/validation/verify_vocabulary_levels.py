#!/usr/bin/env python3
"""
Verify that vocabulary levels match max(hanzi levels) in the word
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

# Read data
hanzi_df = pd.read_csv('data/hanzi.csv')
vocab_df = pd.read_csv('data/vocabulary.csv')

# Create hanzi to level mapping
hanzi_to_level = dict(zip(hanzi_df['hanzi'], hanzi_df['tian_level']))

print("=" * 70)
print("VOCABULARY LEVEL VERIFICATION")
print("=" * 70)
print()

# Check a sample of vocabulary
errors = []
checked = 0

for idx, row in vocab_df.head(50).iterrows():
    word = row['word']
    vocab_level = row['tian_level']
    
    # Get hanzi levels in this word
    hanzi_levels = []
    for char in word:
        if char in hanzi_to_level:
            hanzi_levels.append(hanzi_to_level[char])
    
    if hanzi_levels:
        expected_level = max(hanzi_levels)
        
        if vocab_level != expected_level:
            errors.append({
                'word': word,
                'vocab_level': vocab_level,
                'expected': expected_level,
                'hanzi_levels': hanzi_levels
            })
        
        checked += 1

print(f"Checked: {checked} vocabulary entries")
print(f"Errors: {len(errors)}")
print()

if errors:
    print("❌ MISMATCHES FOUND:")
    print("-" * 70)
    for err in errors[:10]:
        print(f"  {err['word']} (Level {err['vocab_level']}) -> Should be Level {err['expected']}")
        print(f"    Hanzi levels: {err['hanzi_levels']}")
    
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more")
else:
    print("✅ All vocabulary levels correct!")
    print()
    print("Sample verification:")
    for idx, row in vocab_df.head(10).iterrows():
        word = row['word']
        vocab_level = row['tian_level']
        
        # Get hanzi levels
        hanzi_levels = []
        for char in word:
            if char in hanzi_to_level:
                hanzi_levels.append(hanzi_to_level[char])
        
        if hanzi_levels:
            print(f"  {word} (Level {vocab_level}) = max({hanzi_levels}) ✓")

#!/usr/bin/env python3
"""
Example: How to use the generated mnemonic CSVs
================================================
Shows how to load and use the mnemonic data
"""

import pandas as pd

# Load the mnemonic CSVs
print("Loading mnemonic CSVs...")
hanzi_mnemonics = pd.read_csv('data/hanzi_mnemonics_test.csv')
vocab_mnemonics = pd.read_csv('data/vocabulary_mnemonics_test.csv')

print(f"✓ Loaded {len(hanzi_mnemonics)} hanzi mnemonics")
print(f"✓ Loaded {len(vocab_mnemonics)} vocab mnemonics")
print()

# Show hanzi example
print("=" * 80)
print("EXAMPLE: Hanzi Mnemonic Card")
print("=" * 80)
row = hanzi_mnemonics.iloc[0]
print(f"Character: {row['hanzi']}")
print(f"Pinyin: {row['pinyin']}")
print(f"Meaning: {row['meaning'][:80]}...")
print(f"Components: {row['components']}")
print(f"HSK Level: {row['hsk_level']}")
print()
print("AI-Generated Mnemonics:")
print(f"  📖 Meaning: {row['openai_meaning_mnemonic']}")
print(f"  🔊 Reading: {row['openai_reading_mnemonic']}")
print()

# Show vocab example
print("=" * 80)
print("EXAMPLE: Vocabulary Mnemonic Card")
print("=" * 80)
row = vocab_mnemonics.iloc[0]
print(f"Word: {row['word']}")
print(f"Pinyin: {row['pinyin']}")
print(f"Meaning: {row['meaning'][:80]}...")
print(f"Breakdown: {row['hanzi_breakdown'][:80]}...")
print(f"HSK Level: {row['hsk_level']}")
print()
print("AI-Generated Mnemonics:")
print(f"  📖 Meaning: {row['openai_meaning_mnemonic']}")
print(f"  🔊 Reading: {row['openai_reading_mnemonic']}")
print()

# Usage ideas
print("=" * 80)
print("USAGE IDEAS")
print("=" * 80)
print("""
1. Import into Anki as new note fields
2. Create separate mnemonic-focused deck
3. Use for review/study guide
4. Export to mobile flashcard apps
5. Analyze mnemonic effectiveness
6. Generate custom study materials
7. Create visual mnemonic posters
8. Build API-based learning app
""")

#!/usr/bin/env python3
"""
Quick test of mnemonic generator - processes just 3 entries
"""
import sys
import io
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

print("Testing mnemonic generator structure...")
print()

# Load data
radicals_df = pd.read_parquet('data/radicals.parquet').head(3)
hanzi_df = pd.read_parquet('data/hanzi.parquet').head(3)
vocab_df = pd.read_parquet('data/vocabulary.parquet').head(3)

print(f"✓ Loaded {len(radicals_df)} radicals (test sample)")
print(f"✓ Loaded {len(hanzi_df)} hanzi (test sample)")
print(f"✓ Loaded {len(vocab_df)} vocab (test sample)")
print()

# Test radical structure
print("=" * 60)
print("RADICAL CSV STRUCTURE")
print("=" * 60)
radical_output = []
for idx, row in radicals_df.iterrows():
    radical = row['radical']
    meaning = row['meaning']
    usage_count = row.get('usage_count', 0)
    
    radical_output.append({
        'radical': radical,
        'meaning': meaning,
        'usage_count': usage_count,
        'level': row.get('level', 0),
        'openai_meaning_mnemonic': f"[AI] Remember {radical} represents '{meaning}'"
    })
    print(f"{idx + 1}. {radical} = {meaning} (appears in {usage_count} hanzi)")

radical_df_out = pd.DataFrame(radical_output)
radical_df_out.to_csv('data/radicals_mnemonics_test.csv', index=False, encoding='utf-8')
print(f"\n✅ Created: data/radicals_mnemonics_test.csv")
print(f"   Columns: {list(radical_df_out.columns)}")
print()

# Test hanzi structure
print("=" * 60)
print("HANZI CSV STRUCTURE")
print("=" * 60)
hanzi_output = []
for idx, row in hanzi_df.iterrows():
    hanzi = row['hanzi']
    meaning = row['meaning']
    pinyin = row['pinyin']
    components = row.get('components', 'Unknown')
    
    hanzi_output.append({
        'hanzi': hanzi,
        'pinyin': pinyin,
        'meaning': meaning,
        'components': components,
        'hsk_level': row.get('hsk_level', 0),
        'level': row.get('level', 0),
        'openai_meaning_mnemonic': f"[AI] Remember {hanzi} means '{meaning}'",
        'openai_reading_mnemonic': f"[AI] Remember {hanzi} sounds like '{pinyin}'"
    })
    print(f"{idx + 1}. {hanzi} = {meaning} (pinyin: {pinyin}, components: {components})")

hanzi_df_out = pd.DataFrame(hanzi_output)
hanzi_df_out.to_csv('data/hanzi_mnemonics_test.csv', index=False, encoding='utf-8')
print(f"\n✅ Created: data/hanzi_mnemonics_test.csv")
print(f"   Columns: {list(hanzi_df_out.columns)}")
print()

# Test vocab structure
print("=" * 60)
print("VOCABULARY CSV STRUCTURE")
print("=" * 60)
vocab_output = []
for idx, row in vocab_df.iterrows():
    word = row['word']
    meaning = row['meaning']
    pinyin = row['pinyin']
    
    # Build hanzi breakdown
    hanzi_breakdown_parts = []
    for char in word:
        char_row = hanzi_df[hanzi_df['hanzi'] == char]
        if not char_row.empty:
            char_meaning = char_row.iloc[0]['meaning']
            hanzi_breakdown_parts.append(f"{char} ({char_meaning})")
        else:
            hanzi_breakdown_parts.append(char)
    
    hanzi_breakdown = ' + '.join(hanzi_breakdown_parts)
    
    vocab_output.append({
        'word': word,
        'pinyin': pinyin,
        'meaning': meaning,
        'hanzi_breakdown': hanzi_breakdown,
        'hsk_level': row.get('hsk_level', 0),
        'level': row.get('level', 0),
        'openai_meaning_mnemonic': f"[AI] Remember {word} means '{meaning}'",
        'openai_reading_mnemonic': f"[AI] Remember {word} sounds like '{pinyin}'"
    })
    print(f"{idx + 1}. {word} = {meaning}")
    print(f"   Breakdown: {hanzi_breakdown}")

vocab_df_out = pd.DataFrame(vocab_output)
vocab_df_out.to_csv('data/vocabulary_mnemonics_test.csv', index=False, encoding='utf-8')
print(f"\n✅ Created: data/vocabulary_mnemonics_test.csv")
print(f"   Columns: {list(vocab_df_out.columns)}")
print()

print("=" * 60)
print("✨ Test Complete!")
print("=" * 60)
print("\nGenerated test CSVs with proper structure.")
print("Ready to run full script with OpenAI API!")

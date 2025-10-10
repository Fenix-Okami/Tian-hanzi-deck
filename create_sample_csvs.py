#!/usr/bin/env python3
"""
Create sample CSV files from parquet data
Shows 20 random entries from each subdeck
"""

import random
import csv
import sys

try:
    import pandas as pd
except ImportError:
    print("❌ Error: pandas is not installed")
    print("Please run: pip install pandas pyarrow")
    sys.exit(1)

# Set seed for reproducibility
random.seed(42)

print("📊 Creating sample CSV files from parquet data...\n")

# Load data from parquet files
print("📂 Loading data from parquet files...")
radicals_df = pd.read_parquet('data/radicals.parquet')
hanzi_df = pd.read_parquet('data/hanzi.parquet')
vocabulary_df = pd.read_parquet('data/vocabulary.parquet')

# Convert to list of dictionaries
radicals = radicals_df.to_dict('records')
hanzi = hanzi_df.to_dict('records')
vocabulary = vocabulary_df.to_dict('records')

# Sample 20 random entries from each
print("\n🎲 Sampling 20 random entries from each...")
radicals_sample = random.sample(radicals, min(20, len(radicals)))
hanzi_sample = random.sample(hanzi, min(20, len(hanzi)))
vocab_sample = random.sample(vocabulary, min(20, len(vocabulary)))

# Save to CSV
print("\n💾 Saving sample CSV files...\n")

# Save radicals
with open('data/radicals_sample.csv', 'w', newline='', encoding='utf-8') as f:
    if radicals:
        writer = csv.DictWriter(f, fieldnames=radicals[0].keys())
        writer.writeheader()
        writer.writerows(radicals_sample)

print('✓ Created data/radicals_sample.csv')
if radicals:
    print(f'  Fields: {list(radicals[0].keys())}')
print(f'  Entries: {len(radicals_sample)}/{len(radicals)}')

print()

# Save hanzi
with open('data/hanzi_sample.csv', 'w', newline='', encoding='utf-8') as f:
    if hanzi:
        writer = csv.DictWriter(f, fieldnames=hanzi[0].keys())
        writer.writeheader()
        writer.writerows(hanzi_sample)

print('✓ Created data/hanzi_sample.csv')
if hanzi:
    print(f'  Fields: {list(hanzi[0].keys())}')
print(f'  Entries: {len(hanzi_sample)}/{len(hanzi)}')

print()

# Save vocabulary
with open('data/vocabulary_sample.csv', 'w', newline='', encoding='utf-8') as f:
    if vocabulary:
        writer = csv.DictWriter(f, fieldnames=vocabulary[0].keys())
        writer.writeheader()
        writer.writerows(vocab_sample)

print('✓ Created data/vocabulary_sample.csv')
if vocabulary:
    print(f'  Fields: {list(vocabulary[0].keys())}')
print(f'  Entries: {len(vocab_sample)}/{len(vocabulary)}')

print("\n" + "=" * 60)
print("✨ Sample CSV files created successfully!")
print("=" * 60)
print("\nPreview the files:")
print("  • data/radicals_sample.csv")
print("  • data/hanzi_sample.csv")
print("  • data/vocabulary_sample.csv")

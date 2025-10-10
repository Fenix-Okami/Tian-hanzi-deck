#!/usr/bin/env python3
"""
Create HSK 1-3 Hanzi Deck Anki Package
=======================================
Loads HSK 1-3 data from Parquet files and creates a complete Anki deck
with radicals, hanzi, and vocabulary cards.

Features:
- Level-based learning order (requires sort_hsk_by_dependencies.py first)
- HSK-appropriate styling and card types
- Productivity scores for radicals
- Component breakdowns for hanzi
- Example sentences for vocabulary
"""

import random
import sys
import os
import io

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import genanki
    import pandas as pd
except ImportError as e:
    print(f"❌ Error: Required library not installed - {e}")
    print("\nTo install dependencies, run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Load HSK data from Parquet files
print("📂 Loading HSK 1-3 data from Parquet files...")
try:
    radicals_df = pd.read_parquet('data/radicals.parquet')
    hanzi_df = pd.read_parquet('data/hanzi.parquet')
    vocab_df = pd.read_parquet('data/vocabulary.parquet')
    print(f"✓ Loaded {len(radicals_df)} radicals, {len(hanzi_df)} hanzi, {len(vocab_df)} vocabulary entries\n")
except Exception as e:
    print(f"\n❌ Error loading Parquet files: {e}")
    print("\nMake sure to generate data files first:")
    print("  python generate_hsk_deck.py")
    sys.exit(1)

# Define unique model IDs for each card type
RADICAL_MODEL_ID = random.randrange(1 << 30, 1 << 31)
HANZI_MODEL_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Define unique deck ID
DECK_ID = random.randrange(1 << 30, 1 << 31)

# Card model for Radicals (Brown theme)
radical_model = genanki.Model(
    RADICAL_MODEL_ID,
    'HSK Radical Model',
    fields=[
        {'name': 'Radical'},
        {'name': 'Meaning'},
        {'name': 'Productivity'},
        {'name': 'Mnemonic'},
        {'name': 'Level'},
    ],
    templates=[
        {
            'name': 'Radical Recognition',
            'qfmt': '''
                <div class="card-type radical-type">Radical • Level {{Level}}</div>
                <div class="character radical-char">{{Radical}}</div>
                <div class="prompt">What does this radical mean?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning radical-meaning">{{Meaning}}</div>
                <div class="productivity">Used in {{Productivity}} characters</div>
                <div class="mnemonic">{{Mnemonic}}</div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #4a3728;
            background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c4 100%);
            padding: 20px;
        }
        .card-type {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .radical-type { color: #8b4513; }
        .character {
            font-size: 120px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .radical-char { color: #654321; }
        .prompt {
            font-size: 20px;
            color: #6b5544;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
        .radical-meaning { color: #8b4513; }
        .productivity {
            font-size: 16px;
            color: #8b6914;
            background-color: rgba(139, 69, 19, 0.1);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin: 10px 0;
        }
        .mnemonic {
            font-size: 18px;
            color: #5a4a3a;
            margin: 20px;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 12px;
            border-left: 4px solid #8b4513;
        }
    '''
)

# Card model for Hanzi (Green theme)
hanzi_model = genanki.Model(
    HANZI_MODEL_ID,
    'HSK Hanzi Model',
    fields=[
        {'name': 'Character'},
        {'name': 'Meaning'},
        {'name': 'Reading'},
        {'name': 'Radicals'},
        {'name': 'MeaningMnemonic'},
        {'name': 'ReadingMnemonic'},
        {'name': 'HSKLevel'},
        {'name': 'Level'},
    ],
    templates=[
        {
            'name': 'Character Recognition',
            'qfmt': '''
                <div class="card-type hanzi-type">Hanzi • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="character hanzi-char">{{Character}}</div>
                <div class="prompt">What is the meaning and reading?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning hanzi-meaning">{{Meaning}}</div>
                <div class="reading">{{Reading}}</div>
                <div class="section">
                    <div class="section-title">Components</div>
                    <div class="radicals">{{Radicals}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Meaning Mnemonic</div>
                    <div class="mnemonic">{{MeaningMnemonic}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Reading Mnemonic</div>
                    <div class="mnemonic">{{ReadingMnemonic}}</div>
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #2d4a2b;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            padding: 20px;
        }
        .card-type {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .hanzi-type { color: #2e7d32; }
        .character {
            font-size: 120px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .hanzi-char { color: #1b5e20; }
        .prompt {
            font-size: 20px;
            color: #4a6741;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
        .hanzi-meaning { color: #2e7d32; }
        .reading {
            font-size: 24px;
            color: #558b2f;
            margin: 10px 0;
        }
        .section {
            background-color: rgba(255, 255, 255, 0.5);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 12px;
            border-left: 4px solid #2e7d32;
        }
        .section-title {
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .radicals {
            font-size: 18px;
            color: #4a6741;
        }
        .mnemonic {
            font-size: 16px;
            color: #4a6741;
            text-align: left;
        }
    '''
)

# Card model for Vocabulary (Blue theme)
vocab_model = genanki.Model(
    VOCAB_MODEL_ID,
    'HSK Vocabulary Model',
    fields=[
        {'name': 'Word'},
        {'name': 'Meaning'},
        {'name': 'Reading'},
        {'name': 'Characters'},
        {'name': 'Example'},
        {'name': 'HSKLevel'},
        {'name': 'Level'},
    ],
    templates=[
        {
            'name': 'Word Recognition',
            'qfmt': '''
                <div class="card-type vocab-type">Vocabulary • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="word vocab-word">{{Word}}</div>
                <div class="prompt">What does this word mean?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning vocab-meaning">{{Meaning}}</div>
                <div class="reading">{{Reading}}</div>
                <div class="section">
                    <div class="section-title">Character Breakdown</div>
                    <div class="characters">{{Characters}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Example</div>
                    <div class="example">{{Example}}</div>
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #1a237e;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
        }
        .card-type {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .vocab-type { color: #1565c0; }
        .word {
            font-size: 80px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .vocab-word { color: #0d47a1; }
        .prompt {
            font-size: 20px;
            color: #283593;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
        .vocab-meaning { color: #1565c0; }
        .reading {
            font-size: 24px;
            color: #1976d2;
            margin: 10px 0;
        }
        .section {
            background-color: rgba(255, 255, 255, 0.5);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 12px;
            border-left: 4px solid #1565c0;
            text-align: left;
        }
        .section-title {
            font-weight: bold;
            color: #1565c0;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .characters {
            font-size: 18px;
            color: #283593;
            line-height: 1.6;
        }
        .example {
            font-size: 18px;
            color: #283593;
            line-height: 1.6;
        }
    '''
)

# Create the main deck
deck = genanki.Deck(
    DECK_ID,
    'HSK 1-3 Hanzi Deck'
)

print("🎴 Creating Anki cards...")

# Add radical cards
print(f"\n🔷 Adding {len(radicals_df)} radical cards...")
for idx, row in radicals_df.iterrows():
    note = genanki.Note(
        model=radical_model,
        fields=[
            str(row['radical']),
            str(row['meaning']),
            str(row['usage_count']),
            str(row.get('mnemonic', 'Remember this radical!')),
            str(row.get('level', '')),
        ],
        tags=['radical', f'hsk1-3', f'level-{row.get("level", "0")}']
    )
    deck.add_note(note)

print(f"   ✓ Added {len(radicals_df)} radical cards")

# Add hanzi cards
print(f"\n🔤 Adding {len(hanzi_df)} hanzi cards...")
for idx, row in hanzi_df.iterrows():
    note = genanki.Note(
        model=hanzi_model,
        fields=[
            str(row['character']),
            str(row['meaning']),
            str(row['pinyin']),
            str(row['radicals']),
            str(row.get('meaning_mnemonic', 'Think about the meaning of each component.')),
            str(row.get('reading_mnemonic', 'Remember the sound through practice.')),
            str(row.get('hsk_level', '')),
            str(row.get('level', '')),
        ],
        tags=['hanzi', f'hsk{row.get("hsk_level", "")}', f'level-{row.get("level", "0")}']
    )
    deck.add_note(note)

print(f"   ✓ Added {len(hanzi_df)} hanzi cards")

# Add vocabulary cards
print(f"\n📚 Adding {len(vocab_df)} vocabulary cards...")
for idx, row in vocab_df.iterrows():
    note = genanki.Note(
        model=vocab_model,
        fields=[
            str(row['word']),
            str(row['meaning']),
            str(row['pinyin']),
            str(row.get('characters', '')),
            str(row.get('example', '')),
            str(row.get('hsk_level', '')),
            str(row.get('level', '')),
        ],
        tags=['vocabulary', f'hsk{row.get("hsk_level", "")}', f'level-{row.get("level", "0")}']
    )
    deck.add_note(note)

print(f"   ✓ Added {len(vocab_df)} vocabulary cards")

# Create output directory if it doesn't exist
os.makedirs('anki_deck', exist_ok=True)

# Save the deck
output_file = 'anki_deck/HSK_1-3_Hanzi_Deck.apkg'
print(f"\n💾 Saving Anki deck to {output_file}...")

try:
    genanki.Package(deck).write_to_file(output_file)
    print(f"   ✓ Deck saved successfully!")
    
    total_cards = len(radicals_df) + len(hanzi_df) + len(vocab_df)
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Created Anki deck with {total_cards} cards:")
    print(f"   • {len(radicals_df)} radical cards")
    print(f"   • {len(hanzi_df)} hanzi cards")
    print(f"   • {len(vocab_df)} vocabulary cards")
    print(f"{'='*60}")
    print(f"\n📦 Import {output_file} into Anki to start learning!")
    
    if 'level' in radicals_df.columns:
        max_level = max(
            radicals_df['level'].max(),
            hanzi_df.get('level', pd.Series([0])).max(),
            vocab_df.get('level', pd.Series([0])).max()
        )
        print(f"\n🎯 Cards are organized into {int(max_level)} dependency-based levels")
        print("   Use custom study or filter by level tags in Anki!")
    
except Exception as e:
    print(f"\n❌ Error creating deck: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

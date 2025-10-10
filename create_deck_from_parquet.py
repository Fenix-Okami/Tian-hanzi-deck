#!/usr/bin/env python3
"""
Create Tian Hanzi Deck v1 Anki Package from Parquet Data
Loads data from Parquet files and creates a complete Anki deck
"""

import random
import sys
import os

try:
    import genanki
except ImportError:
    print("❌ Error: genanki is not installed")
    print("\nTo install genanki, run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

from parquet_utils import load_tian_v1_data_from_parquet

# Load data from Parquet files
print("📂 Loading data from Parquet files...")
try:
    RADICALS, HANZI, VOCABULARY = load_tian_v1_data_from_parquet(data_dir="data")
    print(f"✓ Loaded {len(RADICALS)} radicals, {len(HANZI)} hanzi, {len(VOCABULARY)} vocabulary entries\n")
except Exception as e:
    print(f"\n❌ Error loading Parquet files: {e}")
    print("\nMake sure to generate Parquet files first:")
    print("  python generate_tian_v1_fast.py")
    sys.exit(1)

# Define unique model IDs for each card type
RADICAL_MODEL_ID = random.randrange(1 << 30, 1 << 31)
HANZI_MODEL_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Define unique deck IDs
MAIN_DECK_ID = random.randrange(1 << 30, 1 << 31)
RADICAL_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_DECK_ID = random.randrange(1 << 30, 1 << 31)

# Card model for Radicals
radical_model = genanki.Model(
    RADICAL_MODEL_ID,
    'Tian Hanzi Radical Model',
    fields=[
        {'name': 'Radical'},
        {'name': 'Meaning'},
        {'name': 'Mnemonic'},
    ],
    templates=[
        {
            'name': 'Radical Recognition',
            'qfmt': '''
                <div class="card-type">Radical</div>
                <div class="character">{{Radical}}</div>
                <div class="prompt">What does this radical mean?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="mnemonic">{{Mnemonic}}</div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #333;
            background-color: #fff;
        }
        .card-type {
            font-size: 14px;
            color: #888;
            margin-bottom: 20px;
        }
        .character {
            font-size: 120px;
            margin: 30px 0;
        }
        .prompt {
            font-size: 20px;
            color: #666;
            margin: 20px 0;
        }
        .meaning {
            font-size: 28px;
            color: #2ecc71;
            margin: 20px 0;
        }
        .mnemonic {
            font-size: 18px;
            color: #666;
            margin: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
    '''
)

# Card model for Hanzi
hanzi_model = genanki.Model(
    HANZI_MODEL_ID,
    'Tian Hanzi Character Model',
    fields=[
        {'name': 'Character'},
        {'name': 'Meaning'},
        {'name': 'Reading'},
        {'name': 'Radicals'},
        {'name': 'MeaningMnemonic'},
        {'name': 'ReadingMnemonic'},
    ],
    templates=[
        {
            'name': 'Character Recognition',
            'qfmt': '''
                <div class="card-type">Hanzi</div>
                <div class="character">{{Character}}</div>
                <div class="question">What is the meaning and reading?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="reading">{{Reading}}</div>
                <div class="radicals">
                    <h3>Radicals:</h3>
                    {{Radicals}}
                </div>
                <div class="mnemonic">
                    <h3>Meaning Mnemonic:</h3>
                    {{MeaningMnemonic}}
                </div>
                <div class="mnemonic">
                    <h3>Reading Mnemonic:</h3>
                    {{ReadingMnemonic}}
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .card-type {
            color: #f0a;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .character {
            font-size: 100px;
            margin: 30px 0;
        }
        .question {
            font-size: 24px;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            color: #f0a;
            margin: 20px 0;
        }
        .reading {
            font-size: 24px;
            color: #666;
            margin: 10px 0;
        }
        .radicals, .mnemonic {
            background-color: #f0f0f0;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
            text-align: left;
        }
        .radicals h3, .mnemonic h3 {
            margin-top: 0;
            color: #666;
        }
    '''
)

# Card model for Vocabulary
vocab_model = genanki.Model(
    VOCAB_MODEL_ID,
    'Tian Hanzi Vocabulary Model',
    fields=[
        {'name': 'Word'},
        {'name': 'Meaning'},
        {'name': 'Reading'},
        {'name': 'Characters'},
        {'name': 'Example'},
        {'name': 'Mnemonic'},
    ],
    templates=[
        {
            'name': 'Vocabulary Recognition',
            'qfmt': '''
                <div class="card-type">Vocabulary</div>
                <div class="character">{{Word}}</div>
                <div class="question">What is the meaning and reading?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="reading">{{Reading}}</div>
                <div class="characters">
                    <h3>Characters:</h3>
                    {{Characters}}
                </div>
                {{#Example}}
                <div class="example">
                    <h3>Example:</h3>
                    {{Example}}
                </div>
                {{/Example}}
                <div class="mnemonic">
                    <h3>Mnemonic:</h3>
                    {{Mnemonic}}
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .card-type {
            color: #a0f;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .character {
            font-size: 80px;
            margin: 30px 0;
        }
        .question {
            font-size: 24px;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            color: #a0f;
            margin: 20px 0;
        }
        .reading {
            font-size: 24px;
            color: #666;
            margin: 10px 0;
        }
        .characters, .example, .mnemonic {
            background-color: #f0f0f0;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
            text-align: left;
        }
        .characters h3, .example h3, .mnemonic h3 {
            margin-top: 0;
            color: #666;
        }
    '''
)

print("🎴 Creating Anki deck from Parquet data...")
print(f"   • {len(RADICALS)} radical cards")
print(f"   • {len(HANZI)} hanzi cards")
print(f"   • {len(VOCABULARY)} vocabulary cards")

# Create subdecks
radical_deck = genanki.Deck(RADICAL_DECK_ID, 'Tian Hanzi Deck::1_Radicals')
hanzi_deck = genanki.Deck(HANZI_DECK_ID, 'Tian Hanzi Deck::2_Hanzi')
vocab_deck = genanki.Deck(VOCAB_DECK_ID, 'Tian Hanzi Deck::3_Vocabulary')

# Add radical cards
print("\n📝 Adding radical cards...")
for radical in RADICALS:
    note = genanki.Note(
        model=radical_model,
        fields=[
            radical['radical'],
            radical['meaning'],
            radical['mnemonic']
        ]
    )
    radical_deck.add_note(note)
print(f"✓ Added {len(RADICALS)} radical cards")

# Add hanzi cards
print("\n📝 Adding hanzi cards...")
for hanzi in HANZI:
    note = genanki.Note(
        model=hanzi_model,
        fields=[
            hanzi['character'],
            hanzi['meaning'],
            hanzi['reading'],
            hanzi['radicals'],
            hanzi['meaning_mnemonic'],
            hanzi['reading_mnemonic']
        ]
    )
    hanzi_deck.add_note(note)
print(f"✓ Added {len(HANZI)} hanzi cards")

# Add vocabulary cards
print("\n📝 Adding vocabulary cards...")
for vocab in VOCABULARY:
    note = genanki.Note(
        model=vocab_model,
        fields=[
            vocab['word'],
            vocab['meaning'],
            vocab['reading'],
            vocab['characters'],
            vocab.get('example', ''),
            vocab['mnemonic']
        ]
    )
    vocab_deck.add_note(note)
print(f"✓ Added {len(VOCABULARY)} vocabulary cards")

# Create package and save
print("\n💾 Creating Anki package...")
output_file = 'anki_deck/Tian_Hanzi_Deck_v1.apkg'
os.makedirs('anki_deck', exist_ok=True)

package = genanki.Package([radical_deck, hanzi_deck, vocab_deck])
package.write_to_file(output_file)

print(f"\n✅ Deck created successfully!")
print(f"📦 Output: {output_file}")
print(f"📊 Total cards: {len(RADICALS) + len(HANZI) + len(VOCABULARY)}")
print("\n🎯 Next step: Import the .apkg file into Anki")

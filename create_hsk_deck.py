#!/usr/bin/env python3
"""
Create HSK 1-3 Hanzi Deck Anki Package
=======================================
Loads HSK 1-3 data from Parquet files and creates a complete Anki deck
with radicals, hanzi, and vocabulary cards.

Features:
- Level-based learning order (requires sort_hsk_by_dependencies.py first)
- Dynamic breakpoint analysis (shows optimal radical grouping)
- HSK-appropriate styling and card types
- Productivity scores for radicals
- Component breakdowns for hanzi
- Example sentences for vocabulary
"""

import random
import sys
import os
import io
import subprocess
from pathlib import Path

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

# Import shared utility functions
from card_utils import create_ruby_text, format_components_with_meanings


def run_breakpoint_analysis():
    """Run breakpoint analysis and display results"""
    print("🔍 Running breakpoint analysis...")
    print("=" * 70)
    
    try:
        # Run the breakpoint analysis script
        result = subprocess.run(
            [sys.executable, 'analyze_level_breakpoints.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            # Parse key statistics from output
            output_lines = result.stdout.split('\n')
            
            for line in output_lines:
                if 'Total Levels:' in line or 'Total Radicals:' in line or 'Total Hanzi:' in line:
                    print(f"   {line.strip()}")
                elif 'Dynamic approach uses' in line:
                    print(f"   ✓ {line.strip()}")
            
            print("=" * 70)
            print()
            
            # Load the breakpoint analysis results
            if Path('data/breakpoint_analysis.csv').exists():
                breakpoints_df = pd.read_csv('data/breakpoint_analysis.csv')
                return breakpoints_df
            else:
                print("⚠️  Warning: Breakpoint analysis file not found, continuing with current data...")
                return None
        else:
            print("⚠️  Warning: Breakpoint analysis failed, continuing with current data...")
            print(f"Error: {result.stderr[:200]}")
            return None
            
    except Exception as e:
        print(f"⚠️  Warning: Could not run breakpoint analysis: {e}")
        print("Continuing with current data...")
        return None


# Run breakpoint analysis first
breakpoints_df = run_breakpoint_analysis()

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


def apply_dynamic_levels(radicals_df, hanzi_df, vocab_df, breakpoints_df):
    """
    Apply dynamic level assignments from breakpoint analysis.
    
    Args:
        radicals_df: DataFrame with radical data
        hanzi_df: DataFrame with hanzi data
        vocab_df: DataFrame with vocabulary data
        breakpoints_df: DataFrame with breakpoint analysis results
    
    Returns:
        Tuple of (radicals_df, hanzi_df, vocab_df) with updated levels
    """
    if breakpoints_df is None:
        print("⚠️  Using existing level assignments (no breakpoint data available)")
        return radicals_df, hanzi_df, vocab_df
    
    print("🔄 Applying dynamic level assignments from breakpoint analysis...")
    
    # Create a copy to avoid modifying original data
    radicals_df = radicals_df.copy()
    hanzi_df = hanzi_df.copy()
    vocab_df = vocab_df.copy()
    
    # Build radical to level mapping
    radical_to_level = {}
    for _, bp_row in breakpoints_df.iterrows():
        level = bp_row['level']
        radicals_str = bp_row['radicals']
        if pd.notna(radicals_str):
            radicals_list = radicals_str.split('|')
            for radical in radicals_list:
                radical = radical.strip()
                if radical and radical != 'No glyph available':
                    radical_to_level[radical] = level
    
    # Apply levels to radicals
    radicals_df['level'] = radicals_df['radical'].map(radical_to_level)
    
    # For any radicals without a level, assign to last level
    max_level = breakpoints_df['level'].max() if len(breakpoints_df) > 0 else 1
    radicals_df['level'] = radicals_df['level'].fillna(max_level)
    
    # Apply levels to hanzi based on their components
    def calculate_hanzi_level(components_str):
        """Calculate hanzi level as max(component levels) + 1"""
        if pd.isna(components_str) or not components_str:
            return max_level
        
        components = [c.strip() for c in str(components_str).split('|')]
        component_levels = []
        
        for comp in components:
            if comp and comp in radical_to_level:
                component_levels.append(radical_to_level[comp])
        
        if component_levels:
            return max(component_levels) + 1
        else:
            return max_level
    
    hanzi_df['level'] = hanzi_df['components'].apply(calculate_hanzi_level)
    
    # Cap hanzi levels at max_level + 1 (since they're components + 1)
    hanzi_df['level'] = hanzi_df['level'].clip(upper=max_level + 1)
    
    # Apply levels to vocabulary based on their characters
    def calculate_vocab_level(word):
        """Calculate vocabulary level as max(hanzi levels) + 1"""
        if pd.isna(word) or not word:
            return max_level + 2
        
        hanzi_levels = []
        for char in str(word):
            if char in hanzi_df['hanzi'].values:
                char_level = hanzi_df[hanzi_df['hanzi'] == char]['level'].iloc[0]
                hanzi_levels.append(char_level)
        
        if hanzi_levels:
            return max(hanzi_levels) + 1
        else:
            return max_level + 2
    
    vocab_df['level'] = vocab_df['word'].apply(calculate_vocab_level)
    
    # Cap vocab levels appropriately
    vocab_df['level'] = vocab_df['level'].clip(upper=max_level + 10)
    
    # Print statistics
    print(f"   ✓ Assigned {len(radicals_df['level'].unique())} radical levels (1-{int(radicals_df['level'].max())})")
    print(f"   ✓ Assigned {len(hanzi_df['level'].unique())} hanzi levels (1-{int(hanzi_df['level'].max())})")
    print(f"   ✓ Assigned {len(vocab_df['level'].unique())} vocabulary levels (1-{int(vocab_df['level'].max())})")
    print()
    
    return radicals_df, hanzi_df, vocab_df


# Apply dynamic levels if breakpoint analysis was successful
radicals_df, hanzi_df, vocab_df = apply_dynamic_levels(
    radicals_df, hanzi_df, vocab_df, breakpoints_df
)

# Define unique model IDs for each card type
RADICAL_MODEL_ID = random.randrange(1 << 30, 1 << 31)
HANZI_MODEL_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Define unique deck IDs (parent and three subdecks)
PARENT_DECK_ID = random.randrange(1 << 30, 1 << 31)
RADICAL_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_DECK_ID = random.randrange(1 << 30, 1 << 31)

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
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning radical-meaning">{{Meaning}}</div>
                <div class="productivity">appears in {{Productivity}} hanzi</div>
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
            ''',
            'afmt': '''
                <div class="card-type hanzi-type">Hanzi • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="character-with-reading">
                    <ruby>
                        <rb class="hanzi-char">{{Character}}</rb>
                        <rt class="pinyin-reading">{{Reading}}</rt>
                    </ruby>
                </div>
                <hr id="answer">
                <div class="meaning hanzi-meaning">{{Meaning}}</div>
                <div class="audio-placeholder">🔊 [Audio: {{Reading}}]</div>
                <div class="section">
                    <div class="section-title">Meaning Mnemonic</div>
                    <div class="mnemonic">{{MeaningMnemonic}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Reading Mnemonic</div>
                    <div class="mnemonic">{{ReadingMnemonic}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Components</div>
                    <div class="radicals">{{Radicals}}</div>
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
        .character-with-reading {
            margin: 30px 0;
            line-height: 1;
        }
        ruby {
            ruby-position: over;
        }
        rt {
            ruby-align: center;
            margin-bottom: 15px;
        }
        .character-with-reading .hanzi-char {
            font-size: 120px;
            color: #1b5e20;
        }
        .pinyin-reading {
            font-size: 28px;
            color: #558b2f;
            font-weight: bold;
        }
        .audio-placeholder {
            font-size: 16px;
            color: #666;
            margin: 10px 0;
            opacity: 0.7;
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
        {'name': 'RubyText'},
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
            ''',
            'afmt': '''
                <div class="card-type vocab-type">Vocabulary • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="word-with-reading">
                    {{RubyText}}
                </div>
                <hr id="answer">
                <div class="meaning vocab-meaning">{{Meaning}}</div>
                <div class="audio-placeholder">🔊 [Audio: {{Reading}}]</div>
                <div class="section">
                    <div class="section-title">Example</div>
                    <div class="example">{{Example}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Character Breakdown</div>
                    <div class="characters">{{Characters}}</div>
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
        .word-with-reading {
            margin: 30px 0;
            line-height: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 5px;
        }
        ruby {
            ruby-position: over;
        }
        rt {
            ruby-align: center;
            margin-bottom: 15px;
        }
        .word-with-reading .vocab-word {
            font-size: 80px;
            color: #0d47a1;
        }
        .word-with-reading .vocab-char {
            font-size: 80px;
            color: #0d47a1;
        }
        .pinyin-reading {
            font-size: 24px;
            color: #1976d2;
            font-weight: bold;
        }
        .audio-placeholder {
            font-size: 16px;
            color: #666;
            margin: 10px 0;
            opacity: 0.7;
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

# Create parent deck and three subdecks
radical_deck = genanki.Deck(
    RADICAL_DECK_ID,
    'HSK 1-3 Hanzi Deck::1. Radicals'
)

hanzi_deck = genanki.Deck(
    HANZI_DECK_ID,
    'HSK 1-3 Hanzi Deck::2. Hanzi'
)

vocab_deck = genanki.Deck(
    VOCAB_DECK_ID,
    'HSK 1-3 Hanzi Deck::3. Vocabulary'
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
        tags=['radical', 'hsk1-3', f'level-{row.get("level", "0")}']
    )
    radical_deck.add_note(note)

print(f"   ✓ Added {len(radicals_df)} radical cards")

# Add hanzi cards
print(f"\n🔤 Adding {len(hanzi_df)} hanzi cards...")
for idx, row in hanzi_df.iterrows():
    # Use correct column names: 'hanzi' not 'character', 'components' not 'radicals'
    char = row.get('hanzi', row.get('character', ''))
    components_str = row.get('components', row.get('radicals', ''))
    
    # Format components with their meanings
    formatted_components = format_components_with_meanings(components_str, radicals_df)
    
    note = genanki.Note(
        model=hanzi_model,
        fields=[
            str(char),
            str(row['meaning']),
            str(row['pinyin']),
            formatted_components,
            str(row.get('meaning_mnemonic', 'Think about the meaning of each component.')),
            str(row.get('reading_mnemonic', 'Remember the sound through practice.')),
            str(row.get('hsk_level', '')),
            str(row.get('level', '')),
        ],
        tags=['hanzi', f'hsk{row.get("hsk_level", "")}', f'level-{row.get("level", "0")}']
    )
    hanzi_deck.add_note(note)

print(f"   ✓ Added {len(hanzi_df)} hanzi cards")

# Add vocabulary cards
print(f"\n📚 Adding {len(vocab_df)} vocabulary cards...")
for idx, row in vocab_df.iterrows():
    word = str(row['word'])
    pinyin = str(row['pinyin'])
    ruby_text = create_ruby_text(word, pinyin)
    
    # Create character breakdown without "+" (just space-separated)
    character_breakdown = ' '.join(list(word))
    
    note = genanki.Note(
        model=vocab_model,
        fields=[
            word,
            str(row['meaning']),
            pinyin,
            ruby_text,
            character_breakdown,
            str(row.get('example', '')),
            str(row.get('hsk_level', '')),
            str(row.get('level', '')),
        ],
        tags=['vocabulary', f'hsk{row.get("hsk_level", "")}', f'level-{row.get("level", "0")}']
    )
    vocab_deck.add_note(note)

print(f"   ✓ Added {len(vocab_df)} vocabulary cards")

# Create output directory if it doesn't exist
os.makedirs('anki_deck', exist_ok=True)

# Save the deck package with all three subdecks
output_file = 'anki_deck/HSK_1-3_Hanzi_Deck.apkg'
print(f"\n💾 Saving Anki deck to {output_file}...")

try:
    # Package all three subdecks together
    genanki.Package([radical_deck, hanzi_deck, vocab_deck]).write_to_file(output_file)
    print("   ✓ Deck saved successfully!")
    
    total_cards = len(radicals_df) + len(hanzi_df) + len(vocab_df)
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Created Anki deck with {total_cards} cards:")
    print(f"   📦 HSK 1-3 Hanzi Deck (parent)")
    print(f"      ├── 1. Radicals: {len(radicals_df)} cards")
    print(f"      ├── 2. Hanzi: {len(hanzi_df)} cards")
    print(f"      └── 3. Vocabulary: {len(vocab_df)} cards")
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

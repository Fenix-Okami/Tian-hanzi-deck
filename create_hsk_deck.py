#!/usr/bin/env python3
"""
Create HSK 1-3 Hanzi Deck Anki Package
=======================================
Loads HSK 1-3 data from CSV files and creates a complete Anki deck
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
from tian_hanzi.core.cards import create_ruby_text, format_components_with_meanings


def run_breakpoint_analysis():
    """Run breakpoint analysis and display results"""
    print("🔍 Running breakpoint analysis...")
    print("=" * 70)
    
    try:
        # Run the breakpoint analysis script
        result = subprocess.run(
            [sys.executable, 'scripts/analysis/analyze_level_breakpoints.py'],
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

# Load HSK data from CSV files
print("📂 Loading HSK 1-3 data from CSV files...")
try:
    radicals_df = pd.read_csv('data/radicals.csv')
    hanzi_df = pd.read_csv('data/hanzi.csv')
    vocab_df = pd.read_csv('data/vocabulary.csv')
    print(f"✓ Loaded {len(radicals_df)} radicals, {len(hanzi_df)} hanzi, {len(vocab_df)} vocabulary entries\n")
except Exception as e:
    print(f"\n❌ Error loading CSV files: {e}")
    print("\nMake sure to generate data files first:")
    print("  python generate_hsk_deck.py")
    sys.exit(1)

# Load radicals_tian.csv for better meanings and HSK breakdown
print("📂 Loading enhanced radical data from radicals_tian.csv...")
try:
    radicals_tian_df = pd.read_csv('data/radicals_tian.csv')
    print(f"✓ Loaded enhanced data for {len(radicals_tian_df)} radicals\n")
except Exception as e:
    print(f"⚠️  Warning: Could not load radicals_tian.csv: {e}")
    print("   Continuing with standard radical data\n")
    radicals_tian_df = None


def load_mnemonic_table(path: str, key_column: str) -> pd.DataFrame:
    """
    Load a mnemonic CSV by its key column, returning the last entry per key.
    If the file is missing or invalid, returns an empty DataFrame with the key column.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        print(f"Mnemonic file not found: {path}. Continuing without it.")
        return pd.DataFrame(columns=[key_column])

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        print(f"Failed to load {path}: {exc}. Mnemonics will be left blank.")
        return pd.DataFrame(columns=[key_column])

    if key_column not in df.columns:
        print(f"Mnemonic file {path} is missing the '{key_column}' column. Skipping merge.")
        return pd.DataFrame(columns=[key_column])

    return df.drop_duplicates(subset=[key_column], keep='last')


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
    print(f"   → Mapping {len(radical_to_level)} radicals to {len(set(radical_to_level.values()))} levels...")
    radicals_df['level'] = radicals_df['radical'].map(radical_to_level)
    
    # For any radicals without a level, assign to last level
    max_level = breakpoints_df['level'].max() if len(breakpoints_df) > 0 else 1
    unmapped_count = radicals_df['level'].isna().sum()
    if unmapped_count > 0:
        print(f"   → Assigning {unmapped_count} unmapped radicals to level {max_level}")
    radicals_df['level'] = radicals_df['level'].fillna(max_level)
    
    # Apply levels to hanzi based on their components
    def calculate_hanzi_level(row):
        """Calculate hanzi level as max(component levels) + 1
        
        Special case: If component_count is 0, the hanzi IS a radical itself.
        It should unlock at the SAME level as when that radical is introduced,
        not default to level 1.
        """
        hanzi_char = row.get('hanzi', row.get('character', ''))
        components_str = row['components']
        component_count = row.get('component_count', 0)
        
        # If no components, the hanzi IS a radical itself
        # Find when this radical is introduced and use that level
        if component_count == 0 or pd.isna(components_str) or not components_str:
            # Look up this hanzi in the radical_to_level mapping
            if hanzi_char in radical_to_level:
                return radical_to_level[hanzi_char]
            else:
                # If not in radical list, assign to last level
                return max_level
        
        # For hanzi with components, calculate based on component levels
        components = [c.strip() for c in str(components_str).split('|')]
        component_levels = []
        
        for comp in components:
            if comp and comp in radical_to_level:
                component_levels.append(radical_to_level[comp])
        
        if component_levels:
            # Assign to same level as the highest component (not +1)
            # Hanzi unlock when all their components are available
            return max(component_levels)
        else:
            # If components exist but aren't in our radical list, assign to max level
            return max_level
    
    hanzi_df['level'] = hanzi_df.apply(calculate_hanzi_level, axis=1)
    
    # Cap hanzi levels at max_level + 1 (since they're components + 1)
    hanzi_df['level'] = hanzi_df['level'].clip(upper=max_level + 1)
    
    # Apply levels to vocabulary based on their characters
    def calculate_vocab_level(word):
        """Calculate vocabulary level as max(hanzi tian_levels)"""
        if pd.isna(word) or not word:
            return max_level + 2
        
        hanzi_levels = []
        for char in str(word):
            if char in hanzi_df['hanzi'].values:
                char_level = hanzi_df[hanzi_df['hanzi'] == char]['level'].iloc[0]
                hanzi_levels.append(char_level)
        
        if hanzi_levels:
            # Vocabulary unlocks at the same level as its most advanced hanzi
            return max(hanzi_levels)
        else:
            # If no hanzi found (shouldn't happen), assign to max level
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

# Merge Tian meanings BEFORE saving (so they're reflected in the CSV outputs)
if radicals_tian_df is not None:
    print("🔄 Merging enhanced radical meanings from radicals_tian.csv...")
    # Keep only the columns we need from tian_df
    tian_cols = ['radical', 'meaning']
    tian_merge = radicals_tian_df[tian_cols].copy()
    
    # Merge with radicals_df, preferring Tian meanings
    radicals_df = radicals_df.merge(
        tian_merge,
        on='radical',
        how='left',
        suffixes=('_old', '_tian')
    )
    
    # Use Tian meaning if available, otherwise fall back to original
    if 'meaning_tian' in radicals_df.columns:
        radicals_df['meaning'] = radicals_df['meaning_tian'].fillna(radicals_df.get('meaning_old', radicals_df.get('meaning', '')))
        # Clean up temporary columns
        radicals_df = radicals_df.drop(columns=['meaning_old', 'meaning_tian'], errors='ignore')
    
    print(f"   ✓ Enhanced {len(radicals_df)} radicals with Tian meanings\n")

# Save the updated data with dynamic levels and reordered columns
if breakpoints_df is not None:
    print("💾 Saving updated data with dynamic levels...")
    
    # Drop 'tian_level' if it already exists (from previous runs)
    if 'tian_level' in radicals_df.columns:
        radicals_df = radicals_df.drop(columns=['tian_level'])
    if 'tian_level' in hanzi_df.columns:
        hanzi_df = hanzi_df.drop(columns=['tian_level'])
    if 'tian_level' in vocab_df.columns:
        vocab_df = vocab_df.drop(columns=['tian_level'])
    
    # Sort dataframes FIRST (using 'level' column), then rename
    # Radicals: Sort by level (ascending), then productivity_score (descending - HSK1-weighted score)
    radicals_df = radicals_df.sort_values(['level', 'productivity_score'], ascending=[True, False])
    
    # Hanzi: Sort by level, hsk_level, component_count (simpler first)
    hanzi_df = hanzi_df.sort_values(['level', 'hsk_level', 'component_count'], ascending=[True, True, True])
    
    # Vocabulary: Sort by level, hsk_level, frequency_position (lower = more frequent)
    vocab_df = vocab_df.sort_values(['level', 'hsk_level', 'frequency_position'], ascending=[True, True, True])
    
    # NOW rename 'level' to 'tian_level' for clarity
    radicals_df = radicals_df.rename(columns={'level': 'tian_level'})
    hanzi_df = hanzi_df.rename(columns={'level': 'tian_level'})
    vocab_df = vocab_df.rename(columns={'level': 'tian_level'})
    
    # Convert tian_level to integers (no decimals)
    radicals_df['tian_level'] = radicals_df['tian_level'].astype(int)
    hanzi_df['tian_level'] = hanzi_df['tian_level'].astype(int)
    vocab_df['tian_level'] = vocab_df['tian_level'].astype(int)
    
    # Reorder columns: tian_level first, then other important columns
    # Radicals: tian_level, radical, meaning, productivity_score, usage_count, usage_hsk1, usage_hsk2, usage_hsk3, stroke_count
    radical_cols = ['tian_level', 'radical', 'meaning', 'productivity_score', 'usage_count', 'usage_hsk1', 'usage_hsk2', 'usage_hsk3', 'stroke_count']
    radicals_df = radicals_df[radical_cols]
    
    # Hanzi: tian_level, hsk_level, hanzi, pinyin, meaning, components, component_count, stroke_count, is_surname
    hanzi_cols = ['tian_level', 'hsk_level', 'hanzi', 'pinyin', 'meaning', 'components', 'component_count', 'stroke_count', 'is_surname']
    hanzi_df = hanzi_df[hanzi_cols]
    
    # Vocabulary: tian_level, hsk_level, frequency_position, word, pinyin, meaning, stroke_count, is_surname
    # Note: 'description' column will be added later from vocabulary_mnemonic.csv
    vocab_cols = ['tian_level', 'hsk_level', 'frequency_position', 'word', 'pinyin', 'meaning', 'stroke_count', 'is_surname']
    # Only include description if it exists
    if 'description' in vocab_df.columns:
        vocab_cols.insert(6, 'description')
    vocab_df = vocab_df[vocab_cols]
    
    
    # Save CSV files
    radicals_df.to_csv('data/radicals.csv', index=False, encoding='utf-8-sig')
    hanzi_df.to_csv('data/hanzi.csv', index=False, encoding='utf-8-sig')
    vocab_df.to_csv('data/vocabulary.csv', index=False, encoding='utf-8-sig')
    
    print("   ✓ Saved updated CSV files\n")

# Merge mnemonic CSV data so deck fields use generated mnemonics
radical_mn_df = load_mnemonic_table('data/radicals_mnemonic.csv', 'radical')
if not radical_mn_df.empty:
    mn_col = 'meaning_mnemonic' if 'meaning_mnemonic' in radical_mn_df.columns else 'openai_meaning_mnemonic'
    if mn_col in radical_mn_df.columns:
        radical_merge = radical_mn_df[['radical', mn_col]].rename(columns={mn_col: 'meaning_mnemonic'})
        radicals_df = radicals_df.merge(radical_merge, on='radical', how='left')
if 'meaning_mnemonic' not in radicals_df.columns:
    radicals_df['meaning_mnemonic'] = ''
else:
    radicals_df['meaning_mnemonic'] = radicals_df['meaning_mnemonic'].fillna('')

hanzi_mn_df = load_mnemonic_table('data/hanzi_mnemonic.csv', 'hanzi')
if not hanzi_mn_df.empty:
    hanzi_merge = hanzi_mn_df.copy()
    if 'meaning' in hanzi_merge.columns:
        hanzi_merge = hanzi_merge.rename(columns={'meaning': 'mnemonic_meaning'})
    hanzi_cols = ['hanzi']
    for col in ('mnemonic_meaning', 'meaning_mnemonic', 'reading_mnemonic'):
        if col in hanzi_merge.columns:
            hanzi_cols.append(col)
    if len(hanzi_cols) > 1:
        hanzi_df = hanzi_df.merge(hanzi_merge[hanzi_cols], on='hanzi', how='left')
for col in ('meaning_mnemonic', 'reading_mnemonic'):
    if col not in hanzi_df.columns:
        hanzi_df[col] = ''
    else:
        hanzi_df[col] = hanzi_df[col].fillna('')
if 'mnemonic_meaning' in hanzi_df.columns:
    hanzi_df['meaning'] = hanzi_df['mnemonic_meaning'].fillna(hanzi_df['meaning'])
    hanzi_df = hanzi_df.drop(columns=['mnemonic_meaning'])
hanzi_df['meaning'] = hanzi_df['meaning'].fillna('')

vocabulary_mn_df = load_mnemonic_table('data/vocabulary_mnemonic.csv', 'word')
if not vocabulary_mn_df.empty:
    vocabulary_merge = vocabulary_mn_df.copy()
    backward_map = {
        'openai_meaning_mnemonic': 'meaning',
        'openai_usage_mnemonic': 'description',
    }
    vocabulary_merge = vocabulary_merge.rename(
        columns={old: new for old, new in backward_map.items() if old in vocabulary_merge.columns}
    )

    merge_cols = ['word']
    if 'meaning' in vocabulary_merge.columns:
        vocabulary_merge = vocabulary_merge.rename(columns={'meaning': 'meaning_simple'})
        merge_cols.append('meaning_simple')
    if 'description' in vocabulary_merge.columns:
        merge_cols.append('description')

    if len(merge_cols) > 1:
        vocab_df = vocab_df.merge(vocabulary_merge[merge_cols], on='word', how='left')

if 'meaning_simple' in vocab_df.columns:
    vocab_df['meaning'] = vocab_df['meaning_simple'].fillna(vocab_df['meaning'])
    vocab_df = vocab_df.drop(columns=['meaning_simple'])

if 'description' not in vocab_df.columns:
    vocab_df['description'] = ''
else:
    vocab_df['description'] = vocab_df['description'].fillna('')

if 'tian_level' not in vocab_df.columns:
    base_levels = vocab_df['level'] if 'level' in vocab_df.columns else 0
    vocab_df['tian_level'] = pd.to_numeric(base_levels, errors='coerce').fillna(0).astype(int)
else:
    vocab_df['tian_level'] = pd.to_numeric(vocab_df['tian_level'], errors='coerce').fillna(0).astype(int)

# Define unique model IDs for each card type
RADICAL_MODEL_ID = random.randrange(1 << 30, 1 << 31)
HANZI_MODEL_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Define unique deck IDs (parent and seven subdecks)
PARENT_DECK_ID = random.randrange(1 << 30, 1 << 31)
RADICAL_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_HSK1_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_HSK2_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_HSK3_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_HSK1_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_HSK2_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_HSK3_DECK_ID = random.randrange(1 << 30, 1 << 31)

# Card model for Radicals (Brown theme)
radical_model = genanki.Model(
    RADICAL_MODEL_ID,
    'HSK Radical Model',
    fields=[
        {'name': 'Radical'},
        {'name': 'Meaning'},
        {'name': 'Productivity'},
        {'name': 'HSK1Count'},
        {'name': 'HSK2Count'},
        {'name': 'HSK3Count'},
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
                <div class="hsk-breakdown">
                    <div class="breakdown-title">HSK Distribution</div>
                    <div class="breakdown-bars">
                        <div class="breakdown-row">
                            <div class="breakdown-label">HSK 1</div>
                            <div class="breakdown-bar-container">
                                <div class="breakdown-bar hsk1" style="width: calc({{HSK1Count}} / {{Productivity}} * 100%);">
                                    <span class="breakdown-count">{{HSK1Count}}</span>
                                </div>
                            </div>
                        </div>
                        <div class="breakdown-row">
                            <div class="breakdown-label">HSK 2</div>
                            <div class="breakdown-bar-container">
                                <div class="breakdown-bar hsk2" style="width: calc({{HSK2Count}} / {{Productivity}} * 100%);">
                                    <span class="breakdown-count">{{HSK2Count}}</span>
                                </div>
                            </div>
                        </div>
                        <div class="breakdown-row">
                            <div class="breakdown-label">HSK 3</div>
                            <div class="breakdown-bar-container">
                                <div class="breakdown-bar hsk3" style="width: calc({{HSK3Count}} / {{Productivity}} * 100%);">
                                    <span class="breakdown-count">{{HSK3Count}}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
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
        .hsk-breakdown {
            margin: 25px auto;
            max-width: 400px;
            background-color: rgba(255, 255, 255, 0.6);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #8b4513;
        }
        .breakdown-title {
            font-size: 18px;
            font-weight: bold;
            color: #654321;
            margin-bottom: 15px;
            text-align: center;
        }
        .breakdown-bars {
            text-align: left;
        }
        .breakdown-row {
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .breakdown-label {
            font-size: 14px;
            font-weight: bold;
            color: #5a4a3a;
            min-width: 50px;
        }
        .breakdown-bar-container {
            flex: 1;
            background-color: rgba(139, 69, 19, 0.1);
            border-radius: 10px;
            overflow: hidden;
            height: 30px;
            position: relative;
        }
        .breakdown-bar {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            transition: width 0.3s ease;
            min-width: 30px;
        }
        .breakdown-bar.hsk1 {
            background: linear-gradient(90deg, #ff6b6b 0%, #ff8787 100%);
        }
        .breakdown-bar.hsk2 {
            background: linear-gradient(90deg, #4dabf7 0%, #74c0fc 100%);
        }
        .breakdown-bar.hsk3 {
            background: linear-gradient(90deg, #51cf66 0%, #8ce99a 100%);
        }
        .breakdown-count {
            font-size: 13px;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
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

# Create parent deck and seven subdecks
radical_deck = genanki.Deck(
    RADICAL_DECK_ID,
    'HSK 1-3 Hanzi Deck::1. Radicals'
)

# Hanzi subdecks by HSK level
hanzi_hsk1_deck = genanki.Deck(
    HANZI_HSK1_DECK_ID,
    'HSK 1-3 Hanzi Deck::2. Hanzi::HSK 1'
)

hanzi_hsk2_deck = genanki.Deck(
    HANZI_HSK2_DECK_ID,
    'HSK 1-3 Hanzi Deck::2. Hanzi::HSK 2'
)

hanzi_hsk3_deck = genanki.Deck(
    HANZI_HSK3_DECK_ID,
    'HSK 1-3 Hanzi Deck::2. Hanzi::HSK 3'
)

# Vocabulary subdecks by HSK level
vocab_hsk1_deck = genanki.Deck(
    VOCAB_HSK1_DECK_ID,
    'HSK 1-3 Hanzi Deck::3. Vocabulary::HSK 1'
)

vocab_hsk2_deck = genanki.Deck(
    VOCAB_HSK2_DECK_ID,
    'HSK 1-3 Hanzi Deck::3. Vocabulary::HSK 2'
)

vocab_hsk3_deck = genanki.Deck(
    VOCAB_HSK3_DECK_ID,
    'HSK 1-3 Hanzi Deck::3. Vocabulary::HSK 3'
)

print("🎴 Creating Anki cards...")

# Ensure HSK breakdown columns exist (meanings were already merged earlier)
# Check if HSK count columns are missing and add them if needed
if radicals_tian_df is not None:
    for col in ['usage_hsk1', 'usage_hsk2', 'usage_hsk3']:
        if col not in radicals_df.columns:
            print(f"🔄 Adding {col} column from radicals_tian.csv...")
            # Merge just the HSK columns
            tian_hsk = radicals_tian_df[['radical', col]].copy()
            radicals_df = radicals_df.merge(tian_hsk, on='radical', how='left')
            radicals_df[col] = radicals_df[col].fillna(0).astype(int)
else:
    # If no Tian data, create default HSK count columns
    for col in ['usage_hsk1', 'usage_hsk2', 'usage_hsk3']:
        if col not in radicals_df.columns:
            radicals_df[col] = 0

# Add radical cards
print(f"🔷 Adding {len(radicals_df)} radical cards...")
for idx, row in radicals_df.iterrows():
    hsk1 = int(row.get('usage_hsk1', 0))
    hsk2 = int(row.get('usage_hsk2', 0))
    hsk3 = int(row.get('usage_hsk3', 0))
    
    note = genanki.Note(
        model=radical_model,
        fields=[
            str(row['radical']),
            str(row['meaning']),
            str(int(row['usage_count'])),
            str(hsk1),
            str(hsk2),
            str(hsk3),
            str(int(row['tian_level'])),
        ],
        tags=['radical', 'hsk1-3', f'tian-{int(row["tian_level"])}']
    )
    radical_deck.add_note(note)

print(f"   ✓ Added {len(radicals_df)} radical cards")

# Add hanzi cards to appropriate HSK subdeck
print(f"\n🔤 Adding {len(hanzi_df)} hanzi cards...")
hanzi_counts = {'hsk1': 0, 'hsk2': 0, 'hsk3': 0, 'unknown': 0}

for idx, row in hanzi_df.iterrows():
    # Use correct column names: 'hanzi' not 'character', 'components' not 'radicals'
    char = row.get('hanzi', row.get('character', ''))
    components_str = row.get('components', row.get('radicals', ''))
    
    # Format components with their meanings
    formatted_components = format_components_with_meanings(components_str, radicals_df)
    
    # Handle potential NaN values for hsk_level
    hsk_level = row.get('hsk_level', '')
    if pd.notna(hsk_level):
        hsk_level_int = int(hsk_level)
        hsk_level_str = str(hsk_level_int)
        hsk_tag = f'hsk{hsk_level_int}'
        
        # Select the appropriate deck
        if hsk_level_int == 1:
            target_deck = hanzi_hsk1_deck
            hanzi_counts['hsk1'] += 1
        elif hsk_level_int == 2:
            target_deck = hanzi_hsk2_deck
            hanzi_counts['hsk2'] += 1
        elif hsk_level_int == 3:
            target_deck = hanzi_hsk3_deck
            hanzi_counts['hsk3'] += 1
        else:
            target_deck = hanzi_hsk1_deck  # Default to HSK1
            hanzi_counts['unknown'] += 1
    else:
        hsk_level_str = ''
        hsk_tag = 'hsk-unknown'
        target_deck = hanzi_hsk1_deck  # Default to HSK1
        hanzi_counts['unknown'] += 1
    
    note = genanki.Note(
        model=hanzi_model,
        fields=[
            str(char),
            str(row['meaning']),
            str(row['pinyin']),
            formatted_components,
            str(row.get('meaning_mnemonic', '') or ''),
            str(row.get('reading_mnemonic', '') or ''),
            hsk_level_str,
            str(int(row['tian_level'])),
        ],
        tags=['hanzi', hsk_tag, f'tian-{int(row["tian_level"])}']
    )
    target_deck.add_note(note)

print(f"   ✓ Added {len(hanzi_df)} hanzi cards:")
print(f"      • HSK 1: {hanzi_counts['hsk1']} cards")
print(f"      • HSK 2: {hanzi_counts['hsk2']} cards")
print(f"      • HSK 3: {hanzi_counts['hsk3']} cards")

# Add vocabulary cards to appropriate HSK subdeck
print(f"\n📚 Adding {len(vocab_df)} vocabulary cards...")
vocab_counts = {'hsk1': 0, 'hsk2': 0, 'hsk3': 0}

for idx, row in vocab_df.iterrows():
    word = str(row['word'])
    pinyin = str(row['pinyin'])
    ruby_text = create_ruby_text(word, pinyin)
    
    # Create character breakdown without "+" (just space-separated)
    character_breakdown = ' '.join(list(word))
    
    hsk_level = int(row['hsk_level'])
    
    # Select the appropriate deck
    if hsk_level == 1:
        target_deck = vocab_hsk1_deck
        vocab_counts['hsk1'] += 1
    elif hsk_level == 2:
        target_deck = vocab_hsk2_deck
        vocab_counts['hsk2'] += 1
    elif hsk_level == 3:
        target_deck = vocab_hsk3_deck
        vocab_counts['hsk3'] += 1
    else:
        target_deck = vocab_hsk1_deck  # Default to HSK1
        vocab_counts['hsk1'] += 1
    
    note = genanki.Note(
        model=vocab_model,
        fields=[
            word,
            str(row['meaning']),
            pinyin,
            ruby_text,
            character_breakdown,
            str(row.get('example', '')),
            str(hsk_level),
            str(int(row['tian_level'])),
        ],
        tags=['vocabulary', f'hsk{hsk_level}', f'tian-{int(row["tian_level"])}']
    )
    target_deck.add_note(note)

print(f"   ✓ Added {len(vocab_df)} vocabulary cards:")
print(f"      • HSK 1: {vocab_counts['hsk1']} cards")
print(f"      • HSK 2: {vocab_counts['hsk2']} cards")
print(f"      • HSK 3: {vocab_counts['hsk3']} cards")

# Create output directory if it doesn't exist
os.makedirs('anki_deck', exist_ok=True)

# Save the deck package with all three subdecks
output_file = 'anki_deck/HSK_1-3_Hanzi_Deck.apkg'
print(f"\n💾 Saving Anki deck to {output_file}...")

try:
    # Package all seven subdecks together
    all_decks = [
        radical_deck,
        hanzi_hsk1_deck, hanzi_hsk2_deck, hanzi_hsk3_deck,
        vocab_hsk1_deck, vocab_hsk2_deck, vocab_hsk3_deck
    ]
    genanki.Package(all_decks).write_to_file(output_file)
    print("   ✓ Deck saved successfully!")
    
    total_cards = len(radicals_df) + len(hanzi_df) + len(vocab_df)
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Created Anki deck with {total_cards} cards:")
    print(f"   📦 HSK 1-3 Hanzi Deck (parent)")
    print(f"      ├── 1. Radicals: {len(radicals_df)} cards")
    print(f"      ├── 2. Hanzi:")
    print(f"      │   ├── HSK 1: {hanzi_counts['hsk1']} cards")
    print(f"      │   ├── HSK 2: {hanzi_counts['hsk2']} cards")
    print(f"      │   └── HSK 3: {hanzi_counts['hsk3']} cards")
    print(f"      └── 3. Vocabulary:")
    print(f"          ├── HSK 1: {vocab_counts['hsk1']} cards")
    print(f"          ├── HSK 2: {vocab_counts['hsk2']} cards")
    print(f"          └── HSK 3: {vocab_counts['hsk3']} cards")
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
